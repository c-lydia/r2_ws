import rclpy
from rclpy.node import Node
from robot_interface.msg import TargetSetter, UpdateWaypoint, WaypointBatch, Return, Waypoint, GripperCmd
import socket
import struct
import time

MAGIC_WAYPOINT = 0xAA
MAGIC_EDIT = 0xBB
MAGIC_RETURN = 0xCC
MAGIC_GRIPPER = 0xDD

TIMEOUT_WARN_S = 780.0
TIMEOUT_DROP_S = 900.0

class UdpListener(Node):
    def __init__(self):
        super().__init__('udp_listener_node')

        self.wp_publisher = self.create_publisher(WaypointBatch, '/waypoint', 10)
        self.target_publisher = self.create_publisher(TargetSetter, '/target_info', 10)
        self.update_publisher = self.create_publisher(UpdateWaypoint, '/update_wp', 10)
        self.return_publisher = self.create_publisher(Return, '/return_flag', 10)
        self.gripper_publisher = self.create_publisher(GripperCmd, '/gripper_cmd', 10)

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

        self.get_logger().info('UDP Listener initialized on port 5050')

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

        new_ip, new_port = addr

        if self.robot_busy:
            if new_ip != self.current_target_ip:
                self.get_logger().warn(
                    f'Rejected packet from {new_ip}:{new_port} — '
                    f'control locked to {self.current_target_ip}:{self.current_target_port}'
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
            self.target_publisher.publish(target_msg)

            self.get_logger().info(
                f'Locked control to {self.current_target_ip}:{self.current_target_port}'
            )

        if self.process_data(data):
            self.last_packet_time = now

    def _check_connection_timeout(self, now=None):
        if not self.robot_busy:
            return

        if now is None:
            now = time.monotonic()

        interval = now - self.last_packet_time

        if TIMEOUT_WARN_S < interval <= TIMEOUT_DROP_S:
            self.get_logger().warn(f'No packet for {interval:.1f}s, connection unhealthy')
        elif interval > TIMEOUT_DROP_S:
            self.get_logger().warn(f'No packets for {interval:.1f}s, terminating connection')
            self.current_target_ip = ''
            self.current_target_port = None
            self.robot_busy = False
            self.last_packet_time = 0.0

            terminate_msg = TargetSetter()
            terminate_msg.ip = ''
            terminate_msg.port = 0
            self.target_publisher.publish(terminate_msg)
            self.get_logger().info('Connection terminated')

    def process_data(self, data: bytes) -> bool:
        if len(data) < 1:
            self.get_logger().warn('Empty packet received')
            return False

        magic = data[0]

        if magic == MAGIC_RETURN:
            return self._parse_return(data)
        elif magic == MAGIC_GRIPPER:
            return self._parse_gripper(data)
        elif magic == MAGIC_EDIT:
            return self._parse_edit(data)
        elif magic == MAGIC_WAYPOINT:
            return self._parse_waypoints(data)
        else:
            self.get_logger().warn(f'Unknown magic byte: {hex(magic)}')
            return False

    def _parse_return(self, data: bytes) -> bool:
        # [0xCC][flag:1] = 2 bytes
        if len(data) != 2:
            self.get_logger().warn(f'Return: expected 2 bytes, got {len(data)}')
            return False

        msg = Return()
        msg.flag = bool(data[1])
        self.return_publisher.publish(msg)
        self.get_logger().info(f'Return flag = {msg.flag}')
        return True

    def _parse_gripper(self, data: bytes) -> bool:
        # [0xDD][open:1] = 2 bytes
        if len(data) != 2:
            self.get_logger().warn(f'Gripper: expected 2 bytes, got {len(data)}')
            return False

        msg = GripperCmd()
        msg.open = bool(data[1])
        self.gripper_publisher.publish(msg)
        self.get_logger().info(f'Gripper open = {msg.open}')
        return True

    def _parse_edit(self, data: bytes) -> bool:
        # [0xBB][edited:1][index:4][version:4][x:8][y:8] = 26 bytes
        if len(data) != 26:
            self.get_logger().warn(f'Edit: expected 26 bytes, got {len(data)}')
            return False

        edited = bool(data[1])
        index, version = struct.unpack_from('<II', data, 2)
        x, y = struct.unpack_from('<dd', data, 10)

        msg = UpdateWaypoint()
        msg.edited = edited
        msg.index = index
        msg.version = version
        msg.x = x
        msg.y = y

        self.update_publisher.publish(msg)
        self.get_logger().info(
            f'Edit: idx={index}, ver={version}, x={x:.3f}, y={y:.3f}, edited={edited}'
        )
        return True

    def _parse_waypoints(self, data: bytes) -> bool:
        # [0xAA][count:4][plan_id:4][wp×N: x:8 y:8 each] = 9 + count×16 bytes
        if len(data) < 9:
            self.get_logger().warn(f'Waypoint: packet too short ({len(data)} bytes)')
            return False

        count, plan_id = struct.unpack_from('<ii', data, 1)

        expected = 9 + count * 16
        if len(data) != expected:
            self.get_logger().warn(
                f'Waypoint: size mismatch — expected {expected}, got {len(data)}'
            )
            return False

        batch = WaypointBatch()
        batch.version = plan_id
        batch.waypoint = []

        offset = 9
        for i in range(count):
            x, y = struct.unpack_from('<dd', data, offset)
            offset += 16

            wp = Waypoint()
            wp.index = i
            wp.x = x
            wp.y = y
            wp.version = plan_id
            batch.waypoint.append(wp)

        self.wp_publisher.publish(batch)
        self.get_logger().info(
            f'Waypoints: {count} wps, version={plan_id}'
        )
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
