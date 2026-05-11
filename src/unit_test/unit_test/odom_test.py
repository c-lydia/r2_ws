"""
odom_test.py — Publishes fake Odometry on /current_odom at 10Hz.
Simulates a robot moving in a straight line, then circling back.
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion

import math

class OdomTest(Node):
    def __init__(self):
       super().__init__('odom_test_node')
       
       self.odom_publisher = self.create_publisher(Odometry, '/odometry', 10) 
       self.timer = self.create_timer(0.1, self._test_cb)
       
       self.t = 0.0
       
       self.get_logger().info('Odom test publoshing to /odomety')
       
    def _test_cb(self):
        self.t == 0.1
        
        x = 2.0 * math.cos(self.t * 0.2)
        y = 2.0 * math.sin(self.t * 0.2)
        yaw = self.t * 0.2 + math.pi/2.0
        
        quat_yaw = self._yaw_to_quat(yaw)
        
        odom_msg = Odometry()
        odom_msg.header.stamp = self.get_clock().now().to_msg()
        odom_msg.header.frame_id = 'odom'
        
        odom_msg.pose.pose.position.x = x
        odom_msg.pose.pose.position.y = y
        odom_msg.pose.pose.position.z = 0.0
        
        odom_msg.pose.pose.orientation.x = quat_yaw.x
        odom_msg.pose.pose.orientation.y = quat_yaw.y
        odom_msg.pose.pose.orientation.z = quat_yaw.z
        odom_msg.pose.pose.orientation.w = quat_yaw.w 
        
        self.odom_publisher.publish(odom_msg)
        self.get_logger().debug(f'odom x = {x:.3f}, y = {y:.3f}, yaw = {yaw:.3f}')
        
    @staticmethod
    def _yaw_to_quat(yaw):
        q = Quaternion()
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(yaw / 2.0)
        q.w = math.cos(yaw / 2.0)
        return q
    
def main():
    rclpy.init()
    odom_test = OdomTest()
    try:
        rclpy.spin(odom_test)
    except KeyboardInterrupt:
        pass
    finally:
        odom_test.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()