import rclpy
from rclpy.node import Node 
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist 
from custom_messages.msg import UpdateWaypoint, Waypoint
import math 

class RobotControl(Node):
    def __init__(self):
        super().__init__('robot_control')
        self.wp_subscriber = self.create_subscription(Waypoint, '/waypoint', self.waypoint_callback, 10)
        self.current_odom_subscriber = self.create_subscription(Odometry, '/current_odom', self.current_odom_callback, 10)
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.update_subscriber = self.create_subscription(UpdateWaypoint, '/update_wp', self.update_wp_callback, 10)
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
        
        self.k_p = 0.2
        self.k_d = 0.0
        self.linear_vel_x_max = 1.0
        self.linear_vel_y_max = 1.0
        self.angular_vel_z_max = 0.5
        
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
        self.dt = 0.1
        
        self.waypoint_queue = []
        self.active_target = None
        self.goal_tolerance = 0.05
        
    def waypoint_callback(self, wp_msg):
        self.waypoint_index = wp_msg.index
        self.waypoint_version = wp_msg.version
        self.waypoint_x = wp_msg.x
        self.waypoint_y = wp_msg.y
        self.waypoint_yaw = math.atan2(self.waypoint_y, self.waypoint_x)
        
        self.get_logger().info(f'Receiving: Waypoint x = {self.waypoint_x}, Waypoint y = {self.waypoint_y}, Waypoint yaw = {self.waypoint_yaw}')
        self.new_target_received = True
        
        self.waypoint_queue.append((self.waypoint_x, self.waypoint_y, self.waypoint_yaw))
        self.get_logger().info(f'New waypoint added: ({self.waypoint_x}, {self.waypoint_y}, {self.waypoint_yaw})')
        
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

        updated_index = update_wp_msg.index
        updated_version = update_wp_msg.version
        updated_x = update_wp_msg.x
        updated_y = update_wp_msg.y
        updated_yaw = math.atan2(updated_y, updated_x)

        if self.active_target and self.waypoint_index == updated_index and self.waypoint_version == updated_version:
            self.active_target = (updated_x, updated_y, updated_yaw)
            self.get_logger().info(f'Active target updated: ({updated_x}, {updated_y}, {updated_yaw})')
            return

        for i, (x, y, yaw) in enumerate(self.waypoint_queue):
            if i == updated_index:  # or store index/version in queue for proper mapping
                self.waypoint_queue[i] = (updated_x, updated_y, updated_yaw)
                self.get_logger().info(f'Waypoint {updated_index} in queue updated: ({updated_x}, {updated_y}, {updated_yaw})')
                break

    def update_active_target(self):
        if not self.active_target and self.waypoint_queue:
            self.active_target = self.waypoint_queue.pop(0)
            self.get_logger().info(f'Active target: {self.active_target}')

    def timer_callback(self):
        self.update_active_target()
        
        if not self.active_target:
            cmd_vel_msg = Twist()
            cmd_vel_msg.linear.x = 0.0
            cmd_vel_msg.linear.y = 0.0
            cmd_vel_msg.angular.z = 0.0
            self.cmd_vel_publisher.publish(cmd_vel_msg)
            self.get_logger().info('No active target: publishing zero velocity')
            return
        
        self.desired_x = self.active_target[0]
        self.desired_y = self.active_target[1]
        self.desired_yaw = self.active_target[2]
        self.desired_z = 0.0
        
        if self.x_start is None:
            self.x_start = self.current_odom_x
            
        if self.y_start is None:
            self.y_start = self.current_odom_y
            
        if self.yaw_start is None:
            self.yaw_start = self.yaw 
            self.previous_yaw_odom = self.yaw
            
        difference_yaw_odom = self.yaw - self.previous_yaw_odom
        
        if abs(difference_yaw_odom) >  math.pi:
            if difference_yaw_odom > 0.0:
                self.overflow_counter -= 1
            else:
                self.overflow_counter += 1
        
        self.current_x = self.current_odom_x
        self.current_y = self.current_odom_y
            
        self.current_x -= self.x_start
        self.current_y -= self.y_start
        self.current_yaw = self.normalize_angle(self.yaw - self.yaw_start + 2 * math.pi * self.overflow_counter)
        
        current_x_p_error_global = self.desired_x - self.current_x
        current_y_p_error_global = self.desired_y - self.current_y
        current_yaw_p_error = self.normalize_angle(self.desired_yaw - self.current_yaw)
        
        current_x_p_error_local = math.cos(self.current_yaw) * current_x_p_error_global + math.sin(self.current_yaw) * current_y_p_error_global 
        current_y_p_error_local = -math.sin(self.current_yaw) * current_x_p_error_global + math.cos(self.current_yaw) * current_y_p_error_global 
        
        current_x_d_error = (current_x_p_error_local - self.previous_x_p_error)/self.dt 
        current_y_d_error = (current_y_p_error_local - self.previous_y_p_error)/self.dt
        current_yaw_d_error = (current_yaw_p_error - self.previous_yaw_p_error)/self.dt
        
        difference_yaw = self.desired_yaw - self.current_yaw
        
        if self.reached_active_target() and abs(difference_yaw) < self.goal_tolerance:
            self.get_logger().info(f'Reached target: {self.active_target}')
            
            if self.waypoint_queue:
                self.active_target = self.waypoint_queue.pop(0)
                self.get_logger().info(f'Next target: {self.active_target}')
            else:
                self.active_target = None
                self.get_logger().info('All waypoints completed')
        
        linear_vel_x = self.k_p * current_x_p_error_local + self.k_d * current_x_d_error
        linear_vel_y = self.k_p * current_y_p_error_local + self.k_d * current_y_d_error
        angular_vel_z = self.k_p * current_yaw_p_error + self.k_d * current_yaw_d_error
        
        self.previous_x = self.current_x
        self.previous_y = self.current_y
        self.previous_yaw = self.current_yaw
        
        self.previous_x_p_error = current_x_p_error_local
        self.previous_y_p_error = current_y_p_error_local
        self.previous_yaw_p_error = current_yaw_p_error
        
        if angular_vel_z > self.angular_vel_z_max:
            angular_vel_z = self.angular_vel_z_max
        elif angular_vel_z < -self.angular_vel_z_max:
            angular_vel_z = -self.angular_vel_z_max
        else:
            pass 
        
        if linear_vel_x > self.linear_vel_x_max:
            linear_vel_x = self.linear_vel_x_max
        elif linear_vel_x < -self.linear_vel_x_max:
            linear_vel_x = -self.linear_vel_x_max
        else:
            pass 
        
        if linear_vel_y > self.linear_vel_y_max:
            linear_vel_y = self.linear_vel_y_max
        elif linear_vel_y < -self.linear_vel_y_max:
            linear_vel_y = -self.linear_vel_y_max
        else:
            pass
        
        cmd_vel_msg = Twist()
        cmd_vel_msg.linear.x = linear_vel_x
        cmd_vel_msg.linear.y = linear_vel_y
        cmd_vel_msg.angular.z = angular_vel_z
        
        self.cmd_vel_publisher.publish(cmd_vel_msg)
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
        return distance < self.goal_tolerance
        
def main():
    rclpy.init()
    robot_control = RobotControl()
    rclpy.spin(robot_control)
    robot_control.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    
