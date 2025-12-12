import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from custom_messages.msg import TargetSetter
import socket
import json
import time


class UdpListener(Node):
    def __init__(self):
        super().__init__('udp_listener')

        self.raw_odom_publisher = self.create_publisher(Odometry, '/raw_target_odom', 10)
        self.target_setter_publisher = self.create_publisher(TargetSetter, '/target_info', 10)

        self.udp_timer = self.create_timer(0.1, self.udp_timer_callback)

        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.receive_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        except Exception as e:
            self.get_logger().warn(f'Could not set socket RCVBUF: {e}')

        self.receive_socket.bind(('0.0.0.0', 5050))
        self.receive_socket.settimeout(0.1)

        self.current_target_ip = ''
        self.current_target_port = None   
        self.robot_busy = False
        self.last_packet_time = 0.0

        self.new_waypoint = False

        print('UDP Listener initialized on port 5050')

    def udp_timer_callback(self):
        now = time.monotonic()

        try:
            data, addr = self.receive_socket.recvfrom(4096)
        except socket.timeout:
            if self.robot_busy:
                self._check_connection_timeout(now)
            return
        except Exception as e:
            self.get_logger().warn(f'Error receiving data: {e}')
            return

        try:
            msg = data.decode('utf-8')
        except Exception as e:
            self.get_logger().warn(f'Failed to decode incoming packet: {e}')
            return

        new_ip = addr[0]
        new_port = addr[1]

        if self.robot_busy:
            if new_ip != self.current_target_ip:
                self.get_logger().warn(
                    f'Rejected packet from {new_ip}:{new_port}: control locked to {self.current_target_ip}:{self.current_target_port}'
                )
                self._check_connection_timeout(now)
                return
        else:
            self.current_target_ip = new_ip
            self.current_target_port = new_port
            self.robot_busy = True
            self.last_packet_time = now

            target_msg = TargetSetter()
            target_msg.ip = self.current_target_ip
            target_msg.port = int(self.current_target_port) if isinstance(self.current_target_port, int) else self.current_target_port
            self.target_setter_publisher.publish(target_msg)

            self.get_logger().info(f'Locked control to {self.current_target_ip}:{self.current_target_port}')

        try:
            json_data = json.loads(msg)
        except json.JSONDecodeError:
            self.get_logger().warn('Invalid JSON received')
            return

        processed = self.process_data(json_data)
        if processed:
            self.last_packet_time = now

    def _check_connection_timeout(self, now=None):
        """
        Check connection health and terminate if too long without valid packets.
        """
        if not self.robot_busy:
            return

        if now is None:
            now = time.monotonic()

        interval = now - self.last_packet_time
        if interval > 780.0 and interval <= 900.0:
            self.get_logger().warn(f'No packet for {interval:.1f}s, connection unhealthy')
        elif interval > 900.0:
            self.get_logger().warn(f'No packets for {interval:.1f}s, terminate connection')
            self.current_target_ip = ''
            self.current_target_port = None
            self.robot_busy = False
            self.last_packet_time = 0.0

            terminate_msg = TargetSetter()
            terminate_msg.ip = self.current_target_ip
            terminate_msg.port = 0
            self.target_setter_publisher.publish(terminate_msg)
            self.get_logger().info('Connection terminated')

    def process_data(self, json_data):
        """
        Validate JSON fields, publish Odometry, return True if processed successfully.
        """
        required_keys = ['ID', 'X', 'Y', 'qX', 'qY', 'qZ', 'qW']
        for k in required_keys:
            if k not in json_data:
                self.get_logger().warn(f'Missing key {k} in JSON')
                return False

        try:
            x = float(json_data['X'])
            y = float(json_data['Y'])
            q_x = float(json_data['qX'])
            q_y = float(json_data['qY'])
            q_z = float(json_data['qZ'])
            q_w = float(json_data['qW'])
            id_val = json_data['ID']
        except Exception as e:
            self.get_logger().warn(f'Non-numeric JSON fields: {e}')
            return False

        raw_target_odom_msg = Odometry()
        raw_target_odom_msg.pose.pose.position.x = x
        raw_target_odom_msg.pose.pose.position.y = y
        raw_target_odom_msg.pose.pose.position.z = 0.0

        raw_target_odom_msg.pose.pose.orientation.x = q_x
        raw_target_odom_msg.pose.pose.orientation.y = q_y
        raw_target_odom_msg.pose.pose.orientation.z = q_z
        raw_target_odom_msg.pose.pose.orientation.w = q_w

        self.raw_odom_publisher.publish(raw_target_odom_msg)
        self.get_logger().info(f'ID: {id_val}, position: ({x}, {y}, 0.0), orientation: ({q_x}, {q_y}, {q_z}, {q_w})')

        return True


def main():
    rclpy.init()
    udp_listener = UdpListener()
    try:
        rclpy.spin(udp_listener)
    except KeyboardInterrupt:
        pass
    finally:
        udp_listener.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
