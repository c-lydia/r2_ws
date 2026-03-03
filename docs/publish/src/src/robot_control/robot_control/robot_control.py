import rclpy
from rclpy.node import Node 
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist 
from custom_messages.msg import UpdateWaypoint, Waypoint, Return
import math  
import time
import pynput 
from enum import Enum

ALPHA = 0.2
MIN_LINEAR_VEL = 0.05
MIN_ANGULAR_VEL = 0.05
MAX_LINEAR_VEL = 1.0
MAX_ANGULAR_VEL = 0.5
ERROR_THRESHOLD = 0.05
ALPHA_D = 0.3

class StateMachine(Enum):
    IDLE = 0
    NAVIGATING = 1
    EDIT = 2
    PAUSED = 3
    RETURNING = 4
    
class RobotControl(Node):
    def __init__(self):
        super().__init__('robot_control')
        self.wp_subscriber = self.create_subscription(Waypoint, '/waypoint', self.waypoint_callback, 10)
        self.current_odom_subscriber = self.create_subscription(Odometry, '/current_odom', self.current_odom_callback, 10)
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.update_subscriber = self.create_subscription(UpdateWaypoint, '/update_wp', self.update_wp_callback, 10)
        self.return_subscriber = self.create_subscription(Return, '/return_flag', self.return_callback, 10)
        self.cmd_vel_timer = self.create_timer(0.1, self.timer_callback)
        
        self.current_odom_x = 0.0
        self.current_odom_y = 0.0
        self.current_odom_z = 0.0
        self.yaw = 0.0
        
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.current_yaw = 0.0
        
        self.waypoint_x = 0.0
        self.waypoint_y = 0.0
        self.waypoint_z = 0.0
        self.waypoint_yaw = 0.0
        
        self.desired_x = 0.0
        self.desired_y = 0.0
        self.desired_yaw = 0.0
        self.desired_z = 0.0
        
        self.k_p_linear = 0.1
        self.k_p_yaw = 0.08
        self.k_d = 0.08
        self.k_d_yaw = 0.06
        
        self.previous_x = None
        self.previous_y = None
        self.previous_yaw = None
        
        self.yaw_start = None
        self.x_start = None
        self.y_start = None
        self.overflow_counter = 0.0
        
        self.previous_x_p_error = 0.0
        self.previous_y_p_error = 0.0
        self.previous_yaw_p_error = 0.0
        self.dt = 0.0
        self.previous_time = 0.0
        
        self.waypoint_queue = []
        self.active_target = None
        self.goal_tolerance_pos = 0.05
        self.goal_tolerance_yaw = 0.01
        self.visited_wp = []
        self.wp = None 
        self.return_ = False
        self.arrival_time = 0.0
        
        self.pause_at_target = False
        self.pause_duration = 1.0
        self.pause_start_time = None
        self.pause_robot = False
        
        self.previous_x_d_error = 0.0
        self.previous_y_d_error = 0.0
        self.previous_yaw_d_error = 0.0
        
        self.scale = 0.0
        
        self.listener = pynput.keyboard.Listener(on_press = self.on_press)
        self.listener.start()
        
        self.cmd_vel_msg = Twist()
        
        self.in_return_mode = False 
        self.startup_time = 0.0
        
        self.state = StateMachine.IDLE

    def waypoint_callback(self, wp_msg):
        self.wp = {
            'index': wp_msg.index,
            'version': wp_msg.version,
            'x': wp_msg.x,
            'y': wp_msg.y,
            'yaw': 0.0
        }
        
        self.get_logger().info(
            f"Receiving waypoint: x = {self.wp['x']}, y = {self.wp['y']}"
        )
        
        self.waypoint_queue.append(self.wp)
        self.get_logger().info(f"Added to queue. Queue size = {len(self.waypoint_queue)}")

        if self.active_target is None:
            self.active_target = dict(self.wp)
            self.get_logger().info(f"Activating first target: {self.active_target}")

    def current_odom_callback(self, current_odom_msg):
        self.current_odom_x = current_odom_msg.pose.pose.position.x
        self.current_odom_y = current_odom_msg.pose.pose.position.y
        self.current_odom_z = current_odom_msg.pose.pose.position.z
        
        current_q = current_odom_msg.pose.pose.orientation 
        self.yaw = self.calculate_yaw(current_q)
        self.get_logger().info(f'Receiving: Current x = {self.current_odom_x}, Current y = {self.current_odom_y}, Current Yaw = {self.yaw}')
        
    def update_wp_callback(self, update_wp_msg):
        if not update_wp_msg.edited:
            return
        
        if self.pause_at_target or self.pause_robot:
            self.publish_stop()
            return
        
        if not self.active_target:
            self.publish_stop()
            self.get_logger().info("No active target")
            return

        update_wp = {
            'updated_index': update_wp_msg.index,
            'updated_version': update_wp_msg.version,
            'updated_x': update_wp_msg.x,
            'updated_y': update_wp_msg.y,
            'updated_yaw': 0.0
        }
        
        if self.active_target['index'] == update_wp['updated_index']:
            if self.active_target['version'] != update_wp['version']:
                self.state = StateMachine.EDIT
                self.edit_wp = update_wp
                self.get_logger().info(f"Preparing to edit active waypoint: {self.active_target}")
            return
        
        for i, wp in enumerate(self.waypoint_queue):
            if wp['index'] == update_wp['index'] and wp['version'] != update_wp['version']:
                self.get_logger().info(f"Editing queued waypoint: {wp}")
                wp['x'] = (1 - ALPHA) * wp['x'] + ALPHA * update_wp['x']
                wp['y'] = (1 - ALPHA) * wp['y'] + ALPHA * update_wp['y']
                
                if self.active_target is None:
                    dx = update_wp['x'] - self.current_x
                else:
                    dx = update_wp['x'] - self.active_target['x']
                    
                if self.active_target is None:
                    dy = update_wp['y'] - self.current_y
                else:
                    dy = update_wp['y'] - self.current_y
                    
                edit_yaw = math.atan2(dy, dx)
                wp['yaw'] = (1 - ALPHA) * wp['yaw'] + ALPHA * edit_yaw
                
                wp['version'] = update_wp['version']
                self.get_logger().info(f"Waypoint updated in queue: {wp}")
                break
    
    def return_callback(self, return_msg):
        self.return_ = return_msg.flag
        
    def handle_idle(self):
        if self.waypoint_queue:
            self.active_target = self.waypoint_queue.pop()
            self.reset_controller_state()
            self.state = StateMachine.NAVIGATING
            self.get_logger().info(f"Next target activated: {self.active_target}")
        elif self.return_ and self.visited_wp:
            self.active_target = self.visited_wp.pop()
            self.reset_controller_state()
            self.state = StateMachine.RETURNING
            self.return_ = False
            self.get_logger().info(f'Retruning to {self.active_target}')
        else:
            self.publish_stop()
            
    def handle_navigation(self):
        if self.active_target is None:
            self.state = StateMachine.IDLE
            return
        
        if self.reached_active_target():
            self.visited_wp.append(self.active_target)
            self.active_target = None
            self.state = StateMachine.IDLE
            
    def handle_returning(self):
        self.handle_navigation()
        
        if self.active_target is None and not self.visited_wp:
            self.state = StateMachine.IDLE
            
    def handle_paused(self):
        self.publish_stop()
        
        if not self.pause_robot:
            self.state = StateMachine.IDLE
            
    def handle_edit(self):
        self.publish_stop()
        
        self.active_target['x'] = (1 - ALPHA) * self.active_target['x'] + ALPHA * self.edit_wp['x']
        self.active_target['y'] = (1 - ALPHA) * self.active_target['y'] + ALPHA * self.edit_wp['y']
        
        edit_dx = self.edit_wp['x'] - self.current_x
        edit_dy = self.edit_wp['y'] - self.current_y
        
        self.edit_yaw = math.atan2(edit_dy, edit_dx)
        
        self.active_target['yaw'] = (1 - ALPHA) * self.active_target['yaw'] + ALPHA * self.edit_yaw
        
        self.reset_controller_state()
        
        self.get_logger().info(f"Waypoint edited safely: {self.active_target}")
        
        self.state = StateMachine.NAVIGATING
            
    def pd_control(self):
        self.desired_x = self.active_target['x']
        self.desired_y = self.active_target['y']
        self.desired_z = 0.0
        
        self.current_x = self.current_odom_x
        self.current_y = self.current_odom_y
        
        self.current_yaw = self.normalize_angle(self.yaw)
        
        current_x_error_g = self.desired_x - self.current_x
        current_y_error_g = self.desired_y - self.current_y
        
        self.desired_yaw = math.atan2(current_y_error_g, current_x_error_g)

        current_yaw_p_error = self.normalize_angle(self.desired_yaw - self.current_yaw)
        
        current_time = time.perf_counter()
        
        if self.previous_time == 0.0:
            self.previous_time = current_time
            return 0.0, 0.0, 0.0
        
        self.dt = current_time - self.previous_time
        self.previous_time = current_time
        
        current_yaw_d_error = (current_yaw_p_error - self.previous_yaw_p_error)/self.dt
        current_x_d_error = (current_x_error_g - self.previous_x_p_error)/self.dt
        current_y_d_error = (current_y_error_g - self.previous_y_p_error)/self.dt
        
        current_x_d_error = ALPHA_D * current_x_d_error + (1 - ALPHA_D) * self.previous_x_d_error
        current_y_d_error = ALPHA_D * current_y_d_error + (1 - ALPHA_D) * self.previous_y_d_error
        current_yaw_d_error = ALPHA_D * current_yaw_d_error + (1 - ALPHA_D) * self.previous_yaw_d_error

        self.previous_x_d_error = current_x_d_error
        self.previous_y_d_error = current_y_d_error
        self.previous_yaw_d_error = current_yaw_d_error

        linear_vel_x_g = self.k_p_linear * current_x_error_g + self.k_d * current_x_d_error
        linear_vel_y_g = self.k_p_linear * current_y_error_g + self.k_d * current_y_d_error
        angular_vel_z_g = self.k_p_yaw * current_yaw_p_error + self.k_d_yaw * current_yaw_d_error
        
        linear_vel_x_l = math.cos(self.current_yaw) * linear_vel_x_g + math.sin(self.current_yaw) * linear_vel_y_g
        linear_vel_y_l = -math.sin(self.current_yaw) * linear_vel_x_g + math.cos(self.current_yaw) * linear_vel_y_g
        
        self.previous_x = self.current_x
        self.previous_y = self.current_y
        self.previous_yaw = self.current_yaw
        
        self.previous_x_p_error = current_x_error_g
        self.previous_y_p_error = current_y_error_g
        self.previous_yaw_p_error = current_yaw_p_error
        
        return linear_vel_x_l, linear_vel_y_l, angular_vel_z_g
    
    def speed_limit(self, v, v_max):
        if v > v_max:
            v = v_max
        elif v < -v_max:
            v = -v_max
        else:
            pass
        
        return v
    
    def dead_reckoning(self, v, threshold):
        """
        Apply a deadzone to a velocity.
        Returns 0 if |v| < threshold, else returns v unchanged.
        """
        
        if abs(v) < threshold:
            return 0.0
        
        return v

    def timer_callback(self):
        linear_vel_x = 0.0
        linear_vel_y = 0.0
        angular_vel_z = 0.0
        
        if self.pause_robot or (self.pause_at_target and (time.perf_counter() - self.pause_start_time < self.pause_duration)):
            if self.pause_at_target and (time.perf_counter() - self.pause_start_time >= self.pause_duration):
                self.pause_at_target = False
                self.get_logger().info("Pause finished, resuming next target")
                
            self.publish_stop()
        else:
            if self.state == StateMachine.IDLE:
                self.handle_idle()
            elif self.state == StateMachine.NAVIGATING:
                self.handle_navigation()
            elif self.state == StateMachine.RETURNING:
                self.handle_returning()   
            elif self.state == StateMachine.EDIT:
                self.handle_edit()
                
                self.edit_override_time = time.perf_counter()
                
                if self.active_target:
                    self.state = StateMachine.NAVIGATING
            elif self.state == StateMachine.PAUSED:
                self.handle_paused()
                self.state = StateMachine.IDLE
        
        edit_override = hasattr(self, "edit_override_time") and \
                (time.perf_counter() - self.edit_override_time < 0.5)
                
        if not edit_override and self.active_target and self.state in [
            StateMachine.NAVIGATING, StateMachine.RETURNING
        ]:
            linear_vel_x, linear_vel_y, angular_vel_z = self.pd_control()
            
        linear_vel_x = self.dead_reckoning(linear_vel_x, ERROR_THRESHOLD)
        linear_vel_y = self.dead_reckoning(linear_vel_y, ERROR_THRESHOLD)
        angular_vel_z = self.dead_reckoning(angular_vel_z, ERROR_THRESHOLD)
        
        linear_vel_x = self.speed_limit(linear_vel_x, MAX_LINEAR_VEL)
        linear_vel_y = self.speed_limit(linear_vel_y, MAX_LINEAR_VEL)
        angular_vel_z = self.speed_limit(angular_vel_z, MAX_ANGULAR_VEL)
                    
        self.cmd_vel_msg.linear.x = linear_vel_x
        self.cmd_vel_msg.linear.y = linear_vel_y
        self.cmd_vel_msg.angular.z = angular_vel_z
        
        self.cmd_vel_publisher.publish(self.cmd_vel_msg)
        
        self.get_logger().info(f"Cmd: Vx = {linear_vel_x:.3f}, Vy = {linear_vel_y:.3f}, Wz = {angular_vel_z:.3f}, state = {self.state}")
        
    def calculate_yaw(self, q):
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_sinp = 1 - 2 * (q.y**2 + q.z**2)
        return math.atan2(siny_cosp, cosy_sinp)
    
    def counter(self, w_z):
        if w_z > 2 * math.pi:
            return -1
        elif w_z < -2 * math.pi:
            return 1
        else:
            return 0 
        
    def normalize_angle(self, a):
        return math.atan2(math.sin(a), math.cos(a))
    
    def reached_active_target(self):
        if not self.active_target:
            return False

        dx = self.desired_x - self.current_x
        dy = self.desired_y - self.current_y

        distance = math.hypot(dx, dy)

        if distance < self.goal_tolerance_pos:
            self.arrival_time += self.dt
        else:
            self.arrival_time = 0.0

        return self.arrival_time > 0.5
    
    def reset_controller_state(self):
        self.previous_time = 0.0
        self.previous_x_p_error = 0.0
        self.previous_y_p_error = 0.0
        self.previous_yaw_p_error = 0.0

        self.previous_x_d_error = 0.0
        self.previous_y_d_error = 0.0
        self.previous_yaw_d_error = 0.0
        
    def on_press(self, key):
        try:
            if key == pynput.keyboard.KeyCode.from_char('p'):
                self.pause_robot = True
            elif key == pynput.keyboard.KeyCode.from_char('c'):
                self.pause_robot = False 
        except AttributeError:
            pass 
        
    def publish_stop(self):
        self.cmd_vel_msg.linear.x = 0.0
        self.cmd_vel_msg.linear.y = 0.0
        self.cmd_vel_msg.angular.z = 0.0
        
def main():
    rclpy.init()
    robot_control = RobotControl()
    rclpy.spin(robot_control)
    robot_control.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    