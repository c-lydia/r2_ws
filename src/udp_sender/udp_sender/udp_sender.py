import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from custom_messages.msg import TargetSetter 
import socket
import struct
import math 

class UdpSender(Node):
    def __init__(self):
        super().__init__('udp_sender')
        self.current_odom_subscriber = self.create_subscription(Odometry, '/current_odom', self.current_odom_callback, 10)
        self.target_setter_subscriber = self.create_subscription(TargetSetter, '/target_info', self.target_callback, 10)
        self.sender_timer = self.create_timer(0.1, self.sender_timer_callback)
        self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.current_target_ip = ''
        self.current_target_port = 5050
        self.current_odom = None
        self.prev_current_odom = None

    def current_odom_callback(self, msg):
        q = msg.pose.pose.orientation
        self.current_odom = {
            'x': msg.pose.pose.position.x,
            'y': msg.pose.pose.position.y,
            'z': msg.pose.pose.position.z,
            'yaw': self.calculate_yaw(q)
        }

    def target_callback(self, msg):
        self.current_target_ip = msg.ip
        self.current_target_port = msg.port

    def sender_timer_callback(self):
        if not self.current_odom or self.current_target_ip == '':
            return

        def has_moved(curr, prev, eps=1e-4):
            if not prev:
                return True
            for k in curr:
                if abs(curr[k] - prev[k]) > eps:
                    return True
            return False

        if has_moved(self.current_odom, self.prev_current_odom):
            try:
                app_msg = struct.pack(
                    '<ddd',
                    self.current_odom['x'],
                    self.current_odom['y'],
                    self.current_odom['yaw']
                )

                self.sender_socket.sendto(
                    app_msg,
                    (self.current_target_ip, self.current_target_port)
                )

                self.get_logger().info(
                    f"Sent odom x={self.current_odom['x']:.3f}, "
                    f"y={self.current_odom['y']:.3f}, "
                    f"yaw={self.current_odom['yaw']:.3f}"
                )

                self.prev_current_odom = self.current_odom.copy()

            except Exception as e:
                self.get_logger().warn(f'Error sending UDP data: {e}')


    def calculate_yaw(self, q):
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_sinp = 1 - 2 * (q.y**2 + q.z**2)
        return math.atan2(siny_cosp, cosy_sinp)

    def destroy_node(self):
        self.sender_socket.close()
        super().destroy_node()
    
def main():
    rclpy.init()
    udp_sender = UdpSender()
    rclpy.spin(udp_sender)
    udp_sender.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()