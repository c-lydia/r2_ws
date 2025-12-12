import rclpy
from rclpy.node import Node
from custom_messages.msg import EncoderFeedback
from sensor_msgs.msg import Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion
import math

class CurrentOdometry(Node):
    def __init__(self):
        super().__init__('current_odometry')
        self.can_driver_subscriber = self.create_subscription(EncoderFeedback, '/encoder_feedback', self.encoder_feedback_callback, 10)
        self.sensor_imu_subscriber = self.create_subscription(Imu, '/imu/data_raw', self.sensor_imu_callback, 10)
        self.current_odom_publisher = self.create_publisher(Odometry, '/current_odom', 10)
        self.current_yaw = 0.0
        self.prev_yaw = 0.0
        self.yaw_start = None
        self.motor_vel = [0, 0, 0, 0]
        self.motor_position = [0, 0, 0, 0]
        self.R = 0.0625
        self.l_x = 0.52
        self.l_y = 0.52
        self.dt = 0.1 
        self.x_odom = 0.0
        self.y_odom = 0.0
        self.yaw = 0.0
        self.x = 0.0
        self.y = 0.0
        self.z_orientation = 0.0
        self.x_start = None
        self.y_start = None
        self.overflow_counter = 0.0
        self.previous_yaw_odom = None
        self.difference_yaw = 0.0
        
    def sensor_imu_callback(self, sensor_msg):
        q_x = sensor_msg.orientation.x 
        q_y = sensor_msg.orientation.y 
        q_z = sensor_msg.orientation.z 
        q_w = sensor_msg.orientation.w
        
        self.yaw = self.calculate_yaw(q_x, q_y, q_z, q_w)
        
        if self.yaw_start == None:
            self.yaw_start = self.yaw
            self.previous_yaw_odom = self.yaw
            
        self.difference_yaw = self.yaw - self.previous_yaw_odom
        
        if abs(self.difference_yaw) > math.pi:
            if self.yaw > 0.0:
                self.overflow_counter -= 1
            else:
                self.overflow_counter += 1
            
        self.current_yaw = self.yaw - self.yaw_start + 2 * math.pi * self.overflow_counter
        self.prev_yaw = self.current_yaw 
        
    def encoder_feedback_callback(self, encoder_msg):
        motor_id = encoder_msg.can_id - 102
        self.get_logger().info(f"CAN ID: {encoder_msg.can_id}, mapped index = {motor_id}")
        self.motor_vel[motor_id] = encoder_msg.speed
        self.motor_position[motor_id] = encoder_msg.position 
            
        linear_vel_x_local = (self.R/4) * (self.motor_vel[0] + self.motor_vel[1] + self.motor_vel[2] + self.motor_vel[3])
        linear_vel_y_local = (self.R/4) * (self.motor_vel[0] - self.motor_vel[1] + self.motor_vel[2] - self.motor_vel[3])
        w_z = (self.R * (-self.motor_vel[0] + self.motor_vel[1] + self.motor_vel[2] - self.motor_vel[3]))/(2 * (self.l_x + self.l_y))
        
        v_x_global = math.cos(self.current_yaw) * linear_vel_x_local - math.sin(self.current_yaw) * linear_vel_y_local
        v_y_gloabl = math.sin(self.current_yaw) * linear_vel_x_local + math.cos(self.current_yaw) * linear_vel_y_local
        
        self.x += v_x_global * self.dt 
        self.y += v_y_gloabl * self.dt
        
        if self.x_start == None:
            self.x_start = self.x
            
        if self.y_start == None:
            self.y_start = self.y
            
        self.x_odom = self.x - self.x_start
        self.y_odom = self.y - self.y_start
        self.z_orientation += w_z * self.dt 
        
        theta = self.publish_yaw(self.current_yaw)
        
        current_odom_msg = Odometry()
        current_odom_msg.twist.twist.linear.x = v_x_global
        current_odom_msg.twist.twist.linear.y = v_y_gloabl
        current_odom_msg.twist.twist.angular.z = w_z
        
        current_odom_msg.pose.pose.position.x = self.x_odom
        current_odom_msg.pose.pose.position.y = self.y_odom
        current_odom_msg.pose.pose.orientation = theta
        
        self.current_odom_publisher.publish(current_odom_msg)
        
        self.get_logger().info(f'Publishing: Velocity = ({v_x_global}, {v_y_gloabl}, {w_z}), Position = ({self.x_odom}, {self.y_odom}), Orientation = {theta}')
        
    def calculate_yaw(self, q_x, q_y, q_z, q_w):
        siny_cosp = 2 * (q_w * q_z + q_x * q_y)
        cosy_sinp = 1 - 2 * (q_y**2 + q_z**2)
        return -math.atan2(siny_cosp, cosy_sinp)
    
    def publish_yaw(self, yaw):
        q = Quaternion()
        q.w = math.cos(yaw/2)
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(yaw/2)
        return q
    
def main():
    rclpy.init()
    current_odometry = CurrentOdometry()
    rclpy.spin(current_odometry)
    current_odometry.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
