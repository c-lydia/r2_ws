import math
import time 

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup

from nav_msgs.msg import Odometry
from std_srvs.srv import Trigger 
from geometry_msgs.msg import Twist
from enum import Enum

from custom_messages.msg import WaypointBatch, UpdateWaypoint, Return, Waypoint
from typing import List, Tuple 

# UPDATE V0.3: 
# - correct kinematics (done)
# - change udp_listener to publishes in batch (done)
# - add state machine (done)
# - simplify controller to P only with rate limit and velocity limit

# NOTE:
# - learn state machine
# - document the code properly for next report

K_P_LINEAR = 0.25
K_P_ANGULAR = 0.18

A_MAX = 0.35

POSITION_DEADZONE = 0.05            
SPEED_DEADZONE = 0.02   
        
ANGULAR_POSITION_DEADZONE = 0.05
ANGULAR_SPEED_DEADZONE = 0.01

ANGULAR_VEL_MAX = 1.0
LINEAR_VEL_MAX = 1.5

ARRIVAL_THRESHOLD = 0.10

PAUSE_DURATION = 0.5

ODOM_RESET_TIMEOUT = 2.0

LOOK_AHEAD_DISTANCE = 0.3

MIN_VEL = 0.08
MIN_VEL_ENABLE_DIST = 0.20

HEADING_SLOWDOWN_START = 0.70 
HEADING_STOP_THRESHOLD = 1.35  

CONTROLLER_YAW_SIGN = 1.0
LATERAL_CMD_SIGN = -1.0
FORWARD_CMD_SIGN = -1.0
ANGULAR_CMD_SIGN = 1.0

class StateMachine(Enum):
    IDLE = 0
    NAVIGATE = 1
    RETURN = 2
    PAUSED = 3

class RobotControl(Node):
    def __init__(self):
        super().__init__('robot_control_node')
        
        cb = ReentrantCallbackGroup()
        
        self.create_subscription(Odometry, '/current_odom', self._odom_callback, 10, callback_group=cb)
        self.create_subscription(WaypointBatch, '/waypoint', self._wp_callback, 10, callback_group=cb)
        self.create_subscription(UpdateWaypoint, '/update_wp', self._edit_callback, 10, callback_group=cb)
        self.create_subscription(Return, '/return_flag', self._return_callback, 10, callback_group=cb)
        
        self._vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self._reset_client = self.create_client(Trigger, '/reset_odometry', callback_group=cb)
        
        self.create_timer(0.01, self._timer_callback, callback_group=cb)
        
        self._state = StateMachine.IDLE
        
        self._waypoints: List[Waypoint] = []
        self._history: List[Waypoint] = []
        self._active_wp: Waypoint | None = None
        
        self._return_requested: bool = False
        self._pause_robot: bool = False
        self._pause_at_wp: bool = False
        self._arrival_time: float = 0.0
        
        self._x: float = 0.0
        self._y: float = 0.0
        self._yaw: float = 0.0
        self._odom_yaw_meas: float | None = None
        self._odom_yaw_unwrapped: float = 0.0
        
        self._prev_vx: float = 0.0
        self._prev_vy: float = 0.0
        self._prev_wz: float = 0.0
        self._yaw_aligned: bool = False
        self._prev_time: float = time.perf_counter()
        
        if self._reset_client.wait_for_service(timeout_sec=ODOM_RESET_TIMEOUT):
            self._reset_client.call_async(Trigger.Request())
            self.get_logger().info('Odometry reset requested')
        else:
            self.get_logger().warn('Odometry reset service unavailable')

    def _odom_callback(self, msg: Odometry) -> None:
        self._x = msg.pose.pose.position.x
        self._y = msg.pose.pose.position.y
        yaw_meas = CONTROLLER_YAW_SIGN * self._quaternion_to_yaw(msg.pose.pose.orientation)

        if self._odom_yaw_meas is None:
            self._odom_yaw_meas = yaw_meas
            self._odom_yaw_unwrapped = yaw_meas
        else:
            self._odom_yaw_unwrapped += self._wrap_angle(yaw_meas - self._odom_yaw_meas)
            self._odom_yaw_meas = yaw_meas

        self._yaw = self._odom_yaw_unwrapped
        
    def _wp_callback(self, msg: WaypointBatch) -> None:
        waypoints: List[Waypoint | None] = [None] * len(msg.waypoint)
        
        for wp in msg.waypoint:
            waypoints[wp.index] = {
                'index': wp.index,
                'x': wp.x,
                'y': wp.y,
                'version': wp.version
            }
        
        for wp in waypoints:
            if wp is not None:
                self._waypoints.append(wp)
        
        if self._state in (StateMachine.IDLE, StateMachine.PAUSED):
            if self._waypoints:
                self._activate_next_waypoint()
                
                self._state = StateMachine.NAVIGATE
            elif self._state == StateMachine.IDLE:
                self._active_wp = None
                
                self._state = StateMachine.IDLE
            
    def _edit_callback(self, msg: UpdateWaypoint) -> None:
        if not msg.edited:
            return
        
        idx = msg.index

        if idx < len(self._waypoints) and self._waypoints[idx] is not None:
            if msg.version <= self._waypoints[idx]['version']:
                self.get_logger().warn(f'Stale edit for waypoint {idx}, ignoring')
                return
            
            self._waypoints[idx]['x'] = msg.x
            self._waypoints[idx]['y'] = msg.y
            self._waypoints[idx]['version'] = msg.version

        if self._active_wp and self._active_wp['index'] == idx:
            if msg.version <= self._active_wp['version']:
                self.get_logger().warn(f'Stale edit for active waypoint {idx}, ignoring')
                return
            
            self._active_wp['x'] = msg.x
            self._active_wp['y'] = msg.y
            self._active_wp['version'] = msg.version
            
            self._arrival_time = 0.0
            
            self.get_logger().info(f'Active waypoint {idx} updated in-motion')
            
    def _return_callback(self, msg: Return) -> None:
        self._return_requested = msg.flag

    def _timer_callback(self) -> None:
            dt = self._tick_dt()
            self._run_state_machine(dt)
    
            vx, vy, wz, angular_error = self._compute_velocity()
            vx, vy, wz = self._apply_limits(vx, vy, wz, dt)
            vx, vy, wz = self._apply_deadzones(vx, vy, wz, angular_error)
    
            self._publish_vel(vx, vy, wz)
            self.get_logger().info(f'state: {self._state.name}, vx: {vx:.3f}, vy: {vy:.3f}, wz: {wz:.3f}')
 
    def _run_state_machine(self, dt: float) -> None:
        if self._state == StateMachine.IDLE:
            self._handle_idle()
        elif self._state == StateMachine.NAVIGATE:
            self._handle_navigate()
        elif self._state == StateMachine.RETURN:
            self._handle_return()
        elif self._state == StateMachine.PAUSED:
            self._handle_paused(dt)
 
    def _compute_velocity(self) -> Tuple[float, float, float, float]:
        if self._active_wp and self._state in (StateMachine.NAVIGATE, StateMachine.RETURN):
            vx, vy, wz, distance_to_goal, angular_error = self._p_controller()
 
            aligned_for_min_vel = abs(angular_error) < HEADING_SLOWDOWN_START
            far_enough_for_min_vel = distance_to_goal > MIN_VEL_ENABLE_DIST
 
            if aligned_for_min_vel and far_enough_for_min_vel:
                if abs(vx) > 0.001 and abs(vx) < MIN_VEL:
                    if vx > 0:
                        vx = MIN_VEL
                    else:
                        vx = -MIN_VEL
                        
                if abs(vy) > 0.001 and abs(vy) < MIN_VEL:
                    if vy > 0:
                        vy = MIN_VEL
                    else:
                        vy = -MIN_VEL
        else:
            vx, vy, wz, angular_error = 0.0, 0.0, 0.0, 0.0
 
        return vx, vy, wz, angular_error
 
    def _apply_limits(self, vx: float, vy: float, wz: float, dt: float) -> Tuple[float, float, float]:
        vx = self._velocity_limit(vx, LINEAR_VEL_MAX)
        vy = self._velocity_limit(vy, LINEAR_VEL_MAX)
        wz = self._velocity_limit(wz, ANGULAR_VEL_MAX)
 
        vx = self._rate_limit(vx, self._prev_vx, A_MAX, dt)
        vy = self._rate_limit(vy, self._prev_vy, A_MAX, dt)
        wz = self._rate_limit(wz, self._prev_wz, A_MAX, dt)

        self._prev_vx = vx
        self._prev_vy = vy
        self._prev_wz = wz
 
        return vx, vy, wz
 
    def _apply_deadzones(self, vx: float, vy: float, wz: float, angular_error: float) -> Tuple[float, float, float]:
        vx, vy, wz = self._position_deadzone(vx, vy, wz, angular_error, POSITION_DEADZONE, ANGULAR_POSITION_DEADZONE)
        vx, vy, wz = self._speed_deadzone(vx, vy, wz, SPEED_DEADZONE, ANGULAR_SPEED_DEADZONE)
        return vx, vy, wz

    def _handle_idle(self) -> None:
        if self._waypoints:
            self._activate_next_waypoint()
            
            self._state = StateMachine.NAVIGATE
        elif self._return_requested:
            self._return_requested = False
            
            if self._history:
                self._activate_return_waypoint()
                
                self._state = StateMachine.RETURN
            else:
                self._active_wp = None
                
                self._state = StateMachine.IDLE
                
                self._publish_stop()     
        elif self._state == StateMachine.RETURN and self._history:
            self._activate_return_waypoint()
        else:
            self._active_wp = None
            self._publish_stop()
            
    def _handle_navigate(self) -> None:
        if self._active_wp is None:
            self._state = StateMachine.IDLE
            return

        if self._reached_wp():
            self._history.append(self._active_wp)
            
            self._active_wp = None
            self._pause_at_wp = True
            self._arrival_time = 0.0
            
            self._reset_controller_state()

            self._prev_vx = 0.0
            self._prev_vy = 0.0
            self._prev_wz = 0.0

            self._publish_stop()
            
            self._state = StateMachine.PAUSED
            
            self.get_logger().info('Waypoint reached, pausing')
            
    def _handle_return(self) -> None:
        if self._active_wp is None:
            self._state = StateMachine.IDLE
            return

        if self._reached_wp():
            self._history.append(self._active_wp)
            
            self._active_wp = None
            self._pause_at_wp = True
            
            self._arrival_time = 0.0
            
            self._reset_controller_state()

            self._prev_vx = 0.0
            self._prev_vy = 0.0
            self._prev_wz = 0.0

            self._publish_stop()
            
            self._state = StateMachine.PAUSED
            
            self.get_logger().info('Return waypoint reached, pausing')
            
    def _handle_paused(self, dt: float) -> None:
        self._publish_stop()
        
        if self._pause_robot:
            return
        
        self._arrival_time += dt
        
        if self._pause_at_wp and self._arrival_time < PAUSE_DURATION:
            return
        
        self._pause_at_wp = False
        self._arrival_time = 0.0
        
        self.get_logger().info('Pause complete, resuming')
        
        self._handle_idle()

    def _p_controller(self) -> Tuple[float, float, float, float, float]:
        dx_g = self._active_wp['x'] - self._x
        dy_g = self._active_wp['y'] - self._y
            
        distance_to_goal = math.hypot(dx_g, dy_g)
    
        desired_yaw, vx_g, vy_g = self._compute_lookahead(dx_g, dy_g, distance_to_goal)
    
        angular_error = self._wrap_angle(desired_yaw - self._odom_yaw_unwrapped)
        abs_heading_error = abs(angular_error)
    
        c, s = math.cos(self._yaw), math.sin(self._yaw)   
             
        vx_l = c * vx_g + s * vy_g
        vy_l = -s * vx_g + c * vy_g
            
        vx_l *= FORWARD_CMD_SIGN
        vy_l *= LATERAL_CMD_SIGN
    
        heading_scale = self._compute_heading_scale(abs_heading_error)
            
        vx_l *= heading_scale
        vy_l *= heading_scale
            
        wz = ANGULAR_CMD_SIGN * K_P_ANGULAR * angular_error
    
        self.get_logger().info(f'error: {dx_g:.4f}, {dy_g:.4f}, {angular_error:.4f}')
    
        return vx_l, vy_l, wz, distance_to_goal, angular_error
 
    def _compute_lookahead(self, dx_g: float, dy_g: float, distance_to_goal: float) -> Tuple[float, float, float]:
        if distance_to_goal > LOOK_AHEAD_DISTANCE:
            ratio = LOOK_AHEAD_DISTANCE / distance_to_goal
            
            virtual_dx = dx_g * ratio
            virtual_dy = dy_g * ratio
            
            desired_yaw = math.atan2(virtual_dy, virtual_dx)
            
            vx_g = K_P_LINEAR * virtual_dx
            vy_g = K_P_LINEAR * virtual_dy
        else:
            desired_yaw = math.atan2(dy_g, dx_g)
            
            vx_g = K_P_LINEAR * dx_g
            vy_g = K_P_LINEAR * dy_g
            
        return desired_yaw, vx_g, vy_g
 
    def _compute_heading_scale(self, abs_heading_error: float) -> float:
        if abs_heading_error >= HEADING_STOP_THRESHOLD:
            return 0.0
        elif abs_heading_error <= HEADING_SLOWDOWN_START:
            return 1.0
        else:
            return (HEADING_STOP_THRESHOLD - abs_heading_error) / (HEADING_STOP_THRESHOLD - HEADING_SLOWDOWN_START)

    def _activate_next_waypoint(self) -> None:
        self._active_wp = self._waypoints.pop(0)
        self._reset_controller_state()
        self.get_logger().info(f"Activated waypoint {self._active_wp['index']}")
        
    def _activate_return_waypoint(self) -> None:
        self._active_wp = self._history.pop()
        self._reset_controller_state()
        self.get_logger().info(f"Returning to waypoint {self._active_wp['index']}")

    def _reset_controller_state(self) -> None:
        self._yaw_aligned = False
        self._prev_time = time.perf_counter()
        
    def _reached_wp(self) -> bool:
        if self._active_wp is None:
            return False
        dist = math.hypot(self._active_wp['x'] - self._x, self._active_wp['y'] - self._y)
        return dist < ARRIVAL_THRESHOLD

    def _tick_dt(self) -> float:
        now = time.perf_counter()
        dt = now - self._prev_time
        self._prev_time = now
        return dt
    
    def _publish_vel(self, vx: float, vy: float, wz: float) -> None:
        msg = Twist()
        msg.linear.x = vx
        msg.linear.y = vy
        msg.angular.z = wz
        self._vel_publisher.publish(msg)
        
    def _publish_stop(self) -> None:
        self._publish_vel(0.0, 0.0, 0.0)
        
    def resume(self) -> None:
        self._pause_robot = False
        self._pause_at_wp = False
        self._arrival_time = 0.0
        self.get_logger().info('Robot resumed')
        self._handle_idle()
            
    def _quaternion_to_yaw(self, q) -> float:
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y ** 2.0 + q.z ** 2.0))
    
    def _wrap_angle(self, a: float) -> float:
        return math.atan2(math.sin(a), math.cos(a))
    
    def _velocity_limit(self, v: float, v_max: float) -> float:
        if v > v_max:
            return v_max
        elif v < -v_max:
            return -v_max
        else:
            return v
    
    def _rate_limit(self, v: float, v_prev: float, a_max: float, dt: float) -> float:
        dv_max = a_max * dt
        dv = v - v_prev
        
        if dv > dv_max:
            dv = dv_max
        elif dv < -dv_max:
            dv = -dv_max
            
        return dv + v_prev

    def _position_deadzone(self, vx: float, vy: float, wz: float, angular_error: float, linear_threshold: float, angular_threshold: float) -> Tuple[float, float, float]:
        if self._active_wp is not None:
            dx_g = self._active_wp['x'] - self._x
            dy_g = self._active_wp['y'] - self._y
            
            c, s = math.cos(self._yaw), math.sin(self._yaw)
            
            dx_l =  c * dx_g + s * dy_g
            dy_l = -s * dx_g + c * dy_g
            
            if abs(dx_l) < linear_threshold:
                vx = 0.0
                
            if abs(dy_l) < linear_threshold:
                vy = 0.0
        else:
            vx = 0.0
            vy = 0.0
            
        if abs(angular_error) < angular_threshold:
            wz = 0.0
            
        return vx, vy, wz

    def _speed_deadzone(self, vx: float, vy: float, wz: float, linear_threshold: float, angular_threshold: float) -> Tuple[float, float, float]:
        if abs(vx) < linear_threshold:
            vx = 0.0
            
        if abs(vy) < linear_threshold:
            vy = 0.0
            
        if abs(wz) < angular_threshold:
            wz = 0.0
            
        return vx, vy, wz
        
def main():
    rclpy.init()
    robot_control = RobotControl()
    try:
        rclpy.spin(robot_control)
    except KeyboardInterrupt:
        pass
    finally:
        robot_control.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()