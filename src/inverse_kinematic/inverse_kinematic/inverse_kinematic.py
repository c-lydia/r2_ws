import rclpy
from rclpy.node import Node
from custom_messages.msg import MotorCommand 
from geometry_msgs.msg import Twist 
import math

class kinematicPublisher(Node): 
    def __init__(self): 
        super().__init__('kinematic_publisher')
        self.cmd_vel_subscriber = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.kinematic_publisher = self.create_publisher(MotorCommand, '/publish_motor', 10)
        
        self.linear_vel_x = 0.0
        self.linear_vel_y = 0.0
        self.angular_vel_z = 0.0
        
        self.l = 66.2 * 0.01 / 2
        self.r = 127.0 * 0.001 / 2
        
    def cmd_vel_callback(self, cmd_vel_msg):
        self.linear_vel_x = cmd_vel_msg.linear.x
        self.linear_vel_y = cmd_vel_msg.linear.y
        self.angular_vel_z = cmd_vel_msg.angular.z 
        
        motor_speed = self.inverse_kinematic(self.linear_vel_x, self.linear_vel_y, self.angular_vel_z)
        motor_polarity = [-1, -1, -1, -1]
        
        for i in range(4):
            motor_msg = MotorCommand()
            motor_msg.speedmode = True
            motor_msg.can_id = i + 1
            motor_msg.goal = -motor_polarity[i] * motor_speed[i]
            self.kinematic_publisher.publish(motor_msg)
            self.get_logger().info(f'Publishing: {motor_msg}')
        
    def inverse_kinematic(self, vx, vy, wz):
        vel_motor = [
            ((math.sqrt(2)/(2 * self.r)) * (vx - vy)) - ((self.l/self.r) * wz),
            ((math.sqrt(2)/(2 * self.r)) * (vx + vy)) + ((self.l/self.r) * wz),
            ((math.sqrt(2)/(2 * self.r)) * (vx - vy)) + ((self.l/self.r) * wz),
            ((math.sqrt(2)/(2 * self.r)) * (vx + vy)) - ((self.l/self.r) * wz)
        ]
        
        return vel_motor
            
def main():
    rclpy.init()
    kinematic_publisher = kinematicPublisher()
    rclpy.spin(kinematic_publisher)
    kinematic_publisher.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()