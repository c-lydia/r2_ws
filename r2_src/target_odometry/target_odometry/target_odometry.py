import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry

class TargetOdometry(Node):
    def __init__(self):
        super().__init__('target_odometry')
        self.raw_target_odom_subscriber = self.create_subscription(Odometry, '/raw_target_odom', self.raw_target_odom_callback, 10)
        self.target_odom_publisher = self.create_publisher(Odometry, '/target_odom', 10)
        self.target_odom_timer = self.create_timer(0.1, self.target_odom_callback)
        self.current_raw_target_odom = None 
        
    def raw_target_odom_callback(self, raw_target_odom_msg):
        self.current_raw_target_odom = raw_target_odom_msg
        
    def target_odom_callback(self):
        if not self.current_raw_target_odom:
            return
        
        raw_target_odom_msg = self.current_raw_target_odom
        
        x = raw_target_odom_msg.pose.pose.position.x 
        y = raw_target_odom_msg.pose.pose.position.y 
        
        target_odom_msg = Odometry()
        target_odom_msg.pose.pose.position.x = x 
        target_odom_msg.pose.pose.position.y = y
        
        self.target_odom_publisher.publish(target_odom_msg)
        print(f'Publishing: position = ({x}, {y})')
        
def main():
    rclpy.init()
    target_odometry = TargetOdometry()
    rclpy.spin(target_odometry)
    target_odometry.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()