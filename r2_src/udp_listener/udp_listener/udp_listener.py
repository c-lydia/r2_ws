import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from custom_messages.msg import TargetSetter, UpdateWaypoint, Waypoint
import socket
import struct
import time

class UdpListener(Node):
    def __init__(self):
        super().__init__('udp_listener')

        self.wp_publisher = self.create_publisher(Waypoint, '/waypoint', 10)
        self.target_setter_publisher = self.create_publisher(TargetSetter, '/target_info', 10)
        self.update_wp_publisher  = self.create_publisher(UpdateWaypoint, '/update_wp', 10)

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
            target_msg.port = int(self.current_target_port)
            self.target_setter_publisher.publish(target_msg)

            self.get_logger().info(
                f'Locked control to {self.current_target_ip}:{self.current_target_port}'
            )

        processed = self.process_data(data)
        
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

    def process_data(self, data):
        data_len = len(data)
        
        if data_len == 25:
            edit_flag = bool(data[0])
            index, version = struct.unpack_from('<II', data, 1)  # uint32 little endian
            x, y = struct.unpack_from('<dd', data, 9)           # float64 little endian

            update_msg = UpdateWaypoint()
            update_msg.edited = edit_flag
            update_msg.index = index
            update_msg.version = version
            update_msg.x = x
            update_msg.y = y

            self.update_wp_publisher.publish(update_msg)
            self.get_logger().info(f'Edit received: idx={index}, ver={version}, x={x}, y={y}, edit={edit_flag}')
            return True
        elif data_len >= 12:
            if data_len < 12:
                self.get_logger().warn('Packet too small for waypoint data')
                return False

            offset = 0
            magic, count, plan_id = struct.unpack_from('<iii', data, offset)
            offset += 12

            if magic != 0xAA:
                self.get_logger().warn(f'Invalid magic: {hex(magic)}')
                return False

            expected_len = 12 + count * 16
            if len(data) != expected_len:
                self.get_logger().warn(f'Packet size mismatch: expected {expected_len}, got {len(data)}')
                return False

            for i in range(count):
                x, y = struct.unpack_from('<dd', data, offset)
                offset += 16

                wp_msg = Waypoint()
                wp_msg.index = count
                wp_msg.version = plan_id
                wp_msg.pose.pose.position.x = x
                wp_msg.pose.pose.position.y = y
                wp_msg.pose.pose.position.z = 0.0

                self.wp_publisher.publish(wp_msg)
                self.get_logger().info(f'WP[{i}] ({x}, {y})')

            return True
        else:
            self.get_logger().warn(f'Unknown packet length: {data_len}')
            return False

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
