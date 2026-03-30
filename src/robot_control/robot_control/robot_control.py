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

# TODO: reconstruct control node:
# - data structure: for waypoint and edit message store in disctionary; for return logic need stack to store vistied waypoints
# - controller: P controller only, add deadzone, speed limiting, rate limiting
# - edit: need complementary filter to avoid sudden change in trajectory
# - need state machine definition

# UPDATE V0.3: 
# - correct kinematics (done)
# - change udp_listener to publishes in batch (done)
# - add state machine (deon)
# - simplify controller to P only with rate limit and velocity limit

# NOTE:
# - learn state machine
# - document the code properly for next report

K_P = 0.3
A_MAX = 0.2
ERROR_THRESHOLD = 0.02
ANGULAR_VEL_MAX = 0.5
LINEAR_VEL_MAX = 1.0
ARRIVAL_THRESHOLD = 0.05
PAUSE_DURATION = 0.5
ODOM_RESET_TIMEOUT = 2.0
CAN_RESET_TIMEOUT = 2.0 

class StateMachine(Enum):
    IDLE = 0
    NAVIGATE = 1
    RETURN = 2
    PAUSED = 3

class RobotControl(Node):
    def __init__(self):
        super().__init__('robot_control_node')
        
        cb = ReentrantCallbackGroup()
        
        self.create_subscription(Odometry, '/current_odom', self._odom_callback, 10, callback_group = cb)
        self.create_subscription(WaypointBatch, '/waypoint', self._wp_callback, 10, callback_group = cb)
        self.create_subscription(UpdateWaypoint, '/update_wp', self._edit_callback, 10, callback_group = cb)
        self.create_subscription(Return, '/return_flag', self._return_callback, 10, callback_group = cb)
        
        self._vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self._reset_client = self.create_client(Trigger, '/reset_odometry', callback_group = cb)
        self._reset_can = self.create_client(Trigger, '/reset_can_driver')
        
        self.create_timer(0.1, self._timer_callback, callback_group = cb)
        
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
        
        self._prev_vx: float = 0.0
        self._prev_vy: float = 0.0
        self._prev_wz: float = 0.0
        self._prev_time: float = time.perf_counter()
        
        if self._reset_client.wait_for_service(timeout_sec = ODOM_RESET_TIMEOUT):
            self._reset_client.call_async(Trigger.Request())
            self.get_logger().info(f'Odometry reset requested')
        else:
            self.get_logger().warn(f'Odometry reset service unavailable')
            
        if self._reset_can.wait_for_service(timeout_sec = CAN_RESET_TIMEOUT):
            self._reset_can.call_async(Trigger.Request())
            self.get_logger().info(f'Can reset requeted')
        else:
            self.get_logger().warn(f'Can reset not available')
            
    def _odom_callback(self, msg: Odometry) -> None:
        self._x = msg.pose.pose.position.x 
        self._y = msg.pose.pose.position.y 
        self._yaw = self._quaternion_to_yaw(msg.pose.pose.orientation)
        
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
        
        if self._waypoints:
            self._activate_next_waypoint()
            self._state = StateMachine.NAVIGATE
        else:
            self._active_wp = None
            self._state = StateMachine.IDLE 
            
    def _edit_callback(self, msg: UpdateWaypoint) -> None:
        if not msg.edited:
            return 
        
        idx = msg.index 
        
        if idx < len(self._waypoints) and self._waypoints[idx] is not None:
            self._waypoints[idx]['x'] = msg.x 
            self._waypoints[idx]['y'] = msg.y 
            
        if self._active_wp and self._active_wp['index'] == idx:
            self._active_wp['x'] = msg.x 
            self._active_wp['y'] = msg.y 
            self._arrival_time = 0.0
            self.get_logger().info(f'Active waypoint {idx} updated in-motion')
            
    def _return_callback(self, msg: Return) -> None:
        self._return_requested = msg.return_flag
        
    def _timer_callback(self) -> None:
        dt = self._tick_dt()
        
        if self._state == StateMachine.IDLE:
            self._handle_idle()
        elif self._state == StateMachine.NAVIGATE:
            self._handle_navigate()
        elif self._state == StateMachine.RETURN:
            self._handle_return()
        elif self._state == StateMachine.PAUSED:
            self._handle_paused(dt)
            
        if self._active_wp and self._state in (StateMachine.NAVIGATE, StateMachine.RETURN):
            vx, vy, wz = self._p_controller()
        else: 
            vx, vy, wz = 0.0, 0.0, 0.0
            
        vx, vy, wz = self._deadzone(vx, vy, wz, ERROR_THRESHOLD)
        
        vx = self._velocity_limit(vx, LINEAR_VEL_MAX)
        vy = self._velocity_limit(vy, LINEAR_VEL_MAX)
        wz = self._velocity_limit(wz, ANGULAR_VEL_MAX)
        
        vx = self._rate_limit(vx, self._prev_vx, A_MAX, dt)
        vy = self._rate_limit(vy, self._prev_vy, A_MAX, dt)
        wz = self._rate_limit(wz, self._prev_wz, A_MAX, dt)
        
        self._publish_vel(vx, vy, wz)
        
        self._prev_vx = vx
        self._prev_vy = vy
        self._prev_wz = wz
        
        self.get_logger().info(f'state: {self._state.name}, vx: {vx:.3f}, vy: {vy:.3f}, wz: {wz:.3f}')
        
    def _handle_idle(self) -> None:
        if self._waypoints:
            self._activate_next_waypoint()
            self._state = StateMachine.NAVIGATE
        elif self._return_requested and self._history:
            self._active_wp = self._history.pop()
            self._reset_controller_state()
            self._return_requested = False 
            self._state = StateMachine.RETURN
            self.get_logger().info(f"Returning to waypoint {self._active_wp['index']}")
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
            self._state = StateMachine.PAUSED
            self.get_logger().info(f'Waypoint reached, pausing')
            
    def _handle_return(self) -> None:
        self._handle_navigate()
        
        if self._active_wp is None and not self._history:
            self._state = StateMachine.IDLE
            
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
        
    def _p_controller(self) -> Tuple[float, float, float]:
        dx_g = self._active_wp['x'] - self._x
        dy_g = self._active_wp['y'] - self._y 
        
        if abs(dx_g) < ARRIVAL_THRESHOLD and abs(dy_g) < ARRIVAL_THRESHOLD:
            self.get_logger().info(f'error: {dx_g:.4f}, {dy_g:.4f} - STOPPING')
            return 0.0, 0.0, 0.0
        
        desired_yaw = math.atan2(dy_g, dx_g)
        yaw_error = self._wrap_angle(desired_yaw - self._yaw)
        
        vx_g = K_P * dx_g 
        vy_g = K_P * dy_g 
        wz = K_P * yaw_error 
        
        c, s = math.cos(self._yaw), math.sin(self._yaw)
        
        vx_l = c * vx_g + s * vy_g 
        vy_l = -s * vx_g + c * vy_g 
        
        self.get_logger().info(f'error: {dx_g:.4f}, {dy_g:4f}')
        
        return vx_l, vy_l, wz 
    
    def _activate_next_waypoint(self) -> None:
        self._active_wp = self._waypoints.pop(0)
        self._reset_controller_state()
        self.get_logger().info(f"Activated waypoint {self._active_wp['index']}")

    def _reset_controller_state(self) -> None: 
        self._prev_vx = 0.0
        self._prev_vy = 0.0
        self._prev_wz = 0.0
        self._prev_time = time.perf_counter()
        
    def _reached_wp(self) -> bool: 
        if self._active_wp is None:
            return False 
        
        dx = self._active_wp['x'] - self._x 
        dy = self._active_wp['y'] - self._y 
        
        return math.hypot(dx, dy) < ARRIVAL_THRESHOLD
    
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
        self.get_logger().info(f'Robot resumed')
        self._handle_idle()
            
    def _quaternion_to_yaw(self, q: float) -> float: 
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y ** 2.0 + q.z ** 2.0))
    
    def _wrap_angle(self, a: float) -> float:
        return math.atan2(math.sin(a), math.cos(a))
    
    def _velocity_limit(self, v: float, v_max: float) -> float:
        if abs(v) > v_max:
            if v > 0:
                v = v_max
            else:
                v = -v_max
                
        return v
    
    def _rate_limit(self, v: float, v_prev: float, a_max: float, dt: float) -> float:
        dv_max = a_max * dt 
        dv = v - v_prev 
        
        if abs(dv) > dv_max:
            if dv > 0:
                dv = dv_max
            else:
                dv = -dv_max
                
        return dv + v_prev
    
    def _deadzone(self, vx: float, vy: float, wz: float, threshold: float, k_w: float = 1.0) -> Tuple[float, float, float]:
        if math.hypot(vx, vy) + k_w * abs(wz) < threshold:
            return 0.0, 0.0, 0.0
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