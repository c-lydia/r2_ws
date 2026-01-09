import rclpy
from rclpy.node import Node 
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist 
from custom_messages.msg import UpdateWaypoint, Waypoint, Return
import math  
import time 

ALPHA = 0.2
MIN_LINEAR_VEL = 0.05
MIN_ANGULAR_VEL = 0.05
MAX_LINEAR_VEL = 1.0
MAX_ANGULAR_VEL = 0.5

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
        
        self.k_p_linear = 0.2
        self.k_p_yaw = 0.1
        self.k_d = 0.05
        
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
        self.goal_tolerance_yaw = 0.1
        self.visited_wp = []
        self.wp = None 
        self.return_ = False
        self.arrival_time = 0.0
        
        self.pause_at_target = False
        self.pause_duration = 0.5 # seconds to pause at each waypoint
        self.pause_start_time = None

    def waypoint_callback(self, wp_msg):
        self.wp = {
            'index': wp_msg.index,
            'version': wp_msg.version,
            'x': wp_msg.x,
            'y': wp_msg.y,
            'yaw': 0.0
        }
        
        dx = self.wp['x'] - self.current_x
        dy = self.wp['y'] - self.current_y
        self.wp['yaw'] = math.atan2(dy, dx)
        
        self.get_logger().info(
            f"Receiving waypoint: x = {self.wp['x']}, y = {self.wp['y']}, yaw = {self.wp['yaw']}"
        )
        
        self.waypoint_queue.append(self.wp)
        self.get_logger().info(f"Added to queue. Queue size = {len(self.waypoint_queue)}")

        if self.active_target is None:
            self.active_target = self.waypoint_queue.pop(0)
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

        update_wp = {
            'updated_index': update_wp_msg.index,
            'updated_version': update_wp_msg.version,
            'updated_x': update_wp_msg.x,
            'updated_y': update_wp_msg.y,
            'updated_yaw': 0.0
        }
        
        for self.wp in self.waypoint_queue:
            if self.wp is self.active_target:
                if self.active_target['index'] == update_wp['updated_index'] and self.active_target['version'] != update_wp['updated_version']:
                    self.active_target['index'] = update_wp['updated_index']
                    self.active_target['x'] = (1 - ALPHA) * self.wp['x'] + ALPHA * update_wp['updated_x']
                    self.active_target['y'] = (1 - ALPHA) * self.wp['y'] + ALPHA * update_wp['updated_y']
                    
                    dx_update = self.active_target['x'] - self.current_x
                    dy_update = self.active_target['y'] - self.current_y
                    
                    yaw_update = math.atan2(dy_update, dx_update)
                    update_wp['updated_yaw'] = yaw_update
                    
                    self.active_target['yaw'] = (1 - ALPHA) * self.wp['yaw'] + ALPHA * update_wp['updated_yaw']
                    self.active_target['version'] = update_wp['updated_version']
                    self.get_logger().info(f'Active waypoint updated: {self.active_target}')
            elif self.wp['index'] == update_wp['updated_index'] and self.wp['version'] != update_wp['updated_version']:
                self.wp['index'] = update_wp['updated_index']
                self.wp['x'] = update_wp['updated_x']
                self.wp['y'] = update_wp['updated_y']
                
                dx_update = update_wp['updated_x'] - self.current_x
                dy_update = update_wp['updated_y'] - self.current_y
                
                yaw_update = math.atan2(dy_update, dx_update)
                update_wp['updated_yaw'] = yaw_update
                
                self.wp['yaw'] = update_wp['updated_yaw']
                self.wp['version'] = update_wp['updated_version']
                self.get_logger().info(f'Waypoint updated: {self.wp}')
                
    def return_callback(self, return_msg):
        self.return_ = return_msg.flag
        
        if self.return_:
            self.get_logger().info("Return flag received")

        if self.return_ and self.visited_wp:
            wp = self.visited_wp.pop()

            if 'return_yaw' in wp:
                wp['yaw'] = wp['return_yaw']

            self.active_target = wp
            mode = 'Return' if self.return_ else 'Forward'
            self.get_logger().info(f'{mode} to waypoint: {self.active_target}')
            self.get_logger().info(f"Returning to previous waypoint: {self.active_target}")
            self.return_ = False

    def update_active_target(self):
        if self.return_ and self.visited_wp:
            wp = self.visited_wp.pop()
            if 'return_yaw' in wp:
                wp['yaw'] = wp['return_yaw']
            self.active_target = wp
            self.return_ = False
            self.get_logger().info(f'Returning to previous waypoint: {self.active_target}')
        elif not self.active_target and self.waypoint_queue:
            self.active_target = self.waypoint_queue.pop(0)
            self.get_logger().info(f'Next target: {self.active_target}')

    def timer_callback(self):
        self.update_active_target()
        
        if not self.active_target:
            if self.waypoint_queue:
                self.active_target = self.waypoint_queue.pop(0)
                self.reset_controller_state()
                self.get_logger().info(f'Activated new target: {self.active_target}')
            else:
                cmd_vel_msg = Twist()
                cmd_vel_msg.linear.x = 0.0
                cmd_vel_msg.linear.y = 0.0
                cmd_vel_msg.angular.z = 0.0
                self.cmd_vel_publisher.publish(cmd_vel_msg)
                self.get_logger().info('No active target: publishing zero velocity')
                return
        
        self.desired_x = self.active_target['x']
        self.desired_y = self.active_target['y']
        self.desired_z = 0.0
        self.desired_yaw = self.active_target['yaw']
        
        self.current_x = self.current_odom_x
        self.current_y = self.current_odom_y
        
        
        self.current_yaw = self.normalize_angle(self.yaw)
        
        current_x_p_error_global = self.desired_x - self.current_x
        current_y_p_error_global = self.desired_y - self.current_y
        current_yaw_p_error = self.normalize_angle(self.desired_yaw - self.current_yaw)
        
        current_x_p_error_local = math.cos(self.current_yaw) * current_x_p_error_global + math.sin(self.current_yaw) * current_y_p_error_global 
        current_y_p_error_local = -math.sin(self.current_yaw) * current_x_p_error_global + math.cos(self.current_yaw) * current_y_p_error_global 
        
        if abs(current_x_p_error_local) < 0.05:
            current_x_p_error_local = 0.0

        if abs(current_y_p_error_local) < 0.05:
            current_y_p_error_local = 0.0
            
        if abs(current_yaw_p_error) < 0.2:
            current_yaw_p_error = 0.0
            
        current_time = time.perf_counter()
        
        if self.previous_time == 0.0:
            self.previous_time = current_time
            return
        
        self.dt = current_time - self.previous_time
        
        current_x_d_error = (current_x_p_error_local - self.previous_x_p_error)/self.dt 
        current_y_d_error = (current_y_p_error_local - self.previous_y_p_error)/self.dt
        current_yaw_d_error = (current_yaw_p_error - self.previous_yaw_p_error)/self.dt
        
        distance = math.hypot(current_x_p_error_local, current_y_p_error_local)

        if distance < 0.5:
            scale = distance/0.5
        else:
            scale = 1.0

        linear_vel_x = (self.k_p_linear * current_x_p_error_local + self.k_d * current_x_d_error) * scale
        linear_vel_y = (self.k_p_linear * current_y_p_error_local + self.k_d * current_y_d_error) * scale
        angular_vel_z = self.k_p_yaw * current_yaw_p_error + self.k_d * current_yaw_d_error
        
        self.previous_time = current_time
        
        self.previous_x = self.current_x
        self.previous_y = self.current_y
        self.previous_yaw = self.current_yaw
        
        self.previous_x_p_error = current_x_p_error_local
        self.previous_y_p_error = current_y_p_error_local
        self.previous_yaw_p_error = current_yaw_p_error

        if angular_vel_z > MAX_ANGULAR_VEL:
            angular_vel_z = MAX_ANGULAR_VEL
        elif angular_vel_z < -MAX_ANGULAR_VEL:
            angular_vel_z = -MAX_ANGULAR_VEL
        else:
            pass 
        
        if linear_vel_x > MAX_LINEAR_VEL:
            linear_vel_x = MAX_LINEAR_VEL
        elif linear_vel_x < -MAX_LINEAR_VEL:
            linear_vel_x = -MAX_LINEAR_VEL
        else:
            pass 
            
        if linear_vel_y > MAX_LINEAR_VEL:
            linear_vel_y = MAX_LINEAR_VEL
        elif linear_vel_y < -MAX_LINEAR_VEL:
            linear_vel_y = -MAX_LINEAR_VEL
        else:
            pass
        
        if abs(linear_vel_x) < MIN_LINEAR_VEL:
            linear_vel_x = 0.0
            
        if abs(linear_vel_y) < MIN_LINEAR_VEL:
            linear_vel_y = 0.0
            
        if abs(angular_vel_z) < MIN_ANGULAR_VEL:
            angular_vel_z = 0.0
            
        # Inside timer_callback, after calculating distance to target
        distance = math.hypot(current_x_p_error_local, current_y_p_error_local)

        if distance < self.goal_tolerance_pos and not self.pause_at_target:
            # Reached the target, start pause
            self.get_logger().info(f'Reached target: {self.active_target}')
            self.reset_controller_state()

            # Stop robot immediately
            cmd_vel_msg = Twist()
            cmd_vel_msg.linear.x = 0.0
            cmd_vel_msg.linear.y = 0.0
            cmd_vel_msg.angular.z = 0.0
            self.cmd_vel_publisher.publish(cmd_vel_msg)

            # Start pause
            self.pause_at_target = True
            self.pause_start_time = time.perf_counter()

            # Save visited waypoint
            wp_copy = dict(self.active_target)
            wp_copy['return_yaw'] = self.current_yaw
            self.visited_wp.append(wp_copy)
        
            return  # exit callback so robot stays stopped

        # Handle pause at waypoint
        if self.pause_at_target:
            elapsed = time.perf_counter() - self.pause_start_time
            
            if elapsed >= self.pause_duration:
                # Move to next waypoint
                if self.waypoint_queue:
                    self.active_target = self.waypoint_queue.pop(0)
                    self.reset_controller_state()
                    self.get_logger().info(f'Next target: {self.active_target}')
                else:
                    self.active_target = None
                    self.get_logger().info('All waypoints completed')
                self.pause_at_target = False
            else:
                # Still pausing, keep publishing zero velocity
                cmd_vel_msg = Twist()
                cmd_vel_msg.linear.x = 0.0
                cmd_vel_msg.linear.y = 0.0
                cmd_vel_msg.angular.z = 0.0
                self.cmd_vel_publisher.publish(cmd_vel_msg)
                return

        cmd_vel_msg = Twist()
        cmd_vel_msg.linear.x = linear_vel_x
        cmd_vel_msg.linear.y = linear_vel_y
        cmd_vel_msg.angular.z = angular_vel_z
        
        self.cmd_vel_publisher.publish(cmd_vel_msg)
        mode = 'Return' if self.return_ else 'Forward'
        self.get_logger().info(f'{mode} navigation: Vx = {linear_vel_x}, Vy = {linear_vel_y}, Wz = {angular_vel_z}')
        self.get_logger().info(f'Publishing: Vx = {cmd_vel_msg.linear.x}, Vy = {cmd_vel_msg.linear.y}, Wz = {cmd_vel_msg.angular.z}')
        
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
        
def main():
    rclpy.init()
    robot_control = RobotControl()
    rclpy.spin(robot_control)
    robot_control.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    