import rclpy
from rclpy.node import Node
from robot_interface.msg import TargetSetter, UpdateWaypoint, WaypointBatch, Return, Waypoint, GripperCmd
import socket
import struct
import time

MAGIC_HELLO = 0x01
MAGIC_HELLO_RESPONSE = 0x02
MAGIC_WAYPOINT_BATCH = 0x03
MAGIC_WAYPOINT_UPDATE = 0x04
MAGIC_RETURN = 0x05
MAGIC_ESTOP = 0x06
MAGIC_HEARTBEAT = 0x07
MAGIC_GOODBYE = 0x08
MAGIC_GRIPPER = 0x10
MAGIC_STATUS = 0x0A

PROTOCOL_VERSION = 2
HEARTBEAT_TIMEOUT_S = 2.0

STATUS_OK = 0x00
STATUS_REJECT = 0x01
STATUS_OVERFLOW = 0x02
STATUS_STALE = 0x03

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

        self.session_id = 0
        self.client_ip = None
        self.client_port = None
        self.prev_heartbeat = 0.0

        self.get_logger().info('UDP Listener initialized on port 5050')

    def udp_timer_callback(self):
        current_time = time.monotonic()
        
        if self.session_id != 0:
            if current_time - self.prev_heartbeat > HEARTBEAT_TIMEOUT_S:
                self.get_logger().warn(f'Heartbeat timeout - deopping session')
                return 
            
        try:
            data, addr = self.receive_socket.recvfrom(4096)
        except socket.timeout:
            return
        except Exception as e:
            self.get_logger().warn(f'Socket error: {e}')
            return

        self._handle_packet(data, addr, current_time)
            
    def _handle_packet(self, data: bytes, addr, now: float):
        if len(data) < 3:
            self.get_logger().warn('Packet too short for header')
            return
        
        ptype = data[0]
        length = struct.unpack_from('>H', data, 1)[0]
        payload = data[:3]
        
        if len(payload) < length:
            self.get_logger().warn(f'Truncated payload: expected {length}, got {len(payload)}')
            return
        
        payload = payload[:length]
        
        if ptype == MAGIC_HELLO:
            self._handle_hello(payload, addr)
            return 
        
        if self.session_id == 0:
            self.get_logger().warn(f'No session — dropping packet type 0x{ptype:02X}')
            return
        
        ip, port = addr
        
        if ip != self.client_id:
            self.get_logger().warn(f'Packet from unknown source {ip} — ignoring')
            return 
        
        if len(payload) < 4:
            self.get_logger().warn('Payload too short for session_id')
            return
        
        rx_session = struct.unpack_from('>I', payload, 0)[0]
        
        if rx_session != self.session_id:
            self.get_logger().warn(f'Session ID mismatch: got {rx_session:#010x}')
            return
        
        if ptype == MAGIC_HEARTBEAT:
            self.prev_heartbeat = now
        elif ptype == MAGIC_WAYPOINT_BATCH:
            self._parse_waypoints(payload)
        elif ptype == MAGIC_WAYPOINT_UPDATE:
            self._parse_update_wp(payload)
        elif ptype == MAGIC_RETURN:
            self._parse_return(payload)
        elif ptype == MAGIC_ESTOP:
            self._parse_estop()
        elif ptype == MAGIC_GRIPPER:
            self._parse_gripper()
        elif ptype == MAGIC_GOODBYE:
            self.get_logger().info('Client sent GOODBYE — dropping session')
            self._drop_session()
        else:
            self.get_logger().warn(f'Unknown packet type: 0x{ptype:02X}')
            
    def _handle_hello(self, payload, addr):
        if len(payload) < 5:
            self.get_logger().warn('Hello payload too short')
            return 
        
        version = payload[0]
        client_id = struct.unpack_from('>I', payload, 1)[0]
        
        if version != PROTOCOL_VERSION:
            self.get_logger().warn(f'Protocol version mismatch: got {version}')
            self._send_hello_response(addr, session_id = 0, status = STATUS_REJECT)
            return 
        
        if self.session_id != 0 and addr[0] != self.client_ip:
            self.get_logger().warn('Session already active — rejecting new HELLO')
            self._send_hello_response(addr, session_id = 0, status = STATUS_REJECT)
            return 
        
        self.session_id = client_id & 0xFFFFFFFF
        self.client_ip = addr[0]
        self.client_port = addr[1]
        self.prev_heartbeat = time.monotonic()
        
        self._send_hello_response(addr, self.session_id, status = STATUS_OK)
        
        target_msg = TargetSetter()
        target_msg.ip   = self.client_ip
        target_msg.port = self.client_port
        self.target_publisher.publish(target_msg)

        self.get_logger().info(
            f'Session established: {self.client_ip}:{self.client_port} '
            f'session_id = {self.session_id:#010x}'
        )
        
    def _send_hello_response(self, addr, session_id: int, status: int):
        payload = struct.pack('>IB', session_id, status)
        header = struct.pack('>BH', MAGIC_HELLO_RESPONSE, len(payload))
        self.receive_socket.sendto(header + payload, addr)
        
    def _drop_session(self):
        self.session_id = 0
        self.client_ip = None
        self.client_port = None
        self.prev_heartbeat = 0.0
        
        terminate = TargetSetter()
        terminate.ip   = ''
        terminate.port = 0
        self.target_publisher.publish(terminate)
        
    def _parse_waypoints(self, payload: bytes):
        if len(payload) < 12:
            self.get_logger().warn('WAYPOINT_BATCH too short')
            return 
        
        plan_id, count = struct.unpack_from('>II', payload, 4)
        expected = 12 + count * 17
        
        if len(payload) < expected:
            self.get_logger().warn(f'WAYPOINT_BATCH truncated: expected {expected}, got {len(payload)}')
            return 
        
        batch = WaypointBatch()
        batch.version  = plan_id
        batch.waypoint = []
        
        offset = 12
        
        for i in range(count):
            x, y = struct.unpack_from('>dd', payload, offset)
            wp_type = payload[offset + 16]
            offset += 17
            
            wp = Waypoint()
            wp.index = i
            wp.version = plan_id
            wp.x = x
            wp.y = y
            wp.type = wp_type
            batch.waypoint.append(wp)
            
        self.wp_publisher.publish(batch)
        self.get_logger().info(f'WAYPOINT_BATCH: {count} waypoints plan_id={plan_id}')
        
    def _parse_update_wp(self, payload: bytes):
        if len(payload) < 30:
            self.get_logger().warn(f'UPDATE_WAYPOINT too short: {len(payload)}')
            return
        
        seq = struct.unpack_from('>I', payload, 4)[0]
        flag = payload[8]
        index = struct.unpack_from('>I', payload, 9)[0]
        x, y = struct.unpack_from('>dd', payload, 13)
        wp_type = payload[29]
        
        edit_msg = UpdateWaypoint()
        edit_msg.edited = bool(flag)
        edit_msg.index = index
        edit_msg.x = x
        edit_msg.y = y
        edit_msg.type = wp_type 
        self.update_publisher.publish(edit_msg)
        self.get_logger().info(f'UPDATE_WAYPOINT: idx={index} seq={seq} x={x:.3f} y={y:.3f} type={wp_type}')
        
    def _parse_return(self, payload: bytes):
        return_msg = Return()
        return_msg.flag = True
        self.return_publisher.publish(return_msg)
        self.get_logger().info('RETURN received')
        
    def _parse_estop(self):
        estop_msg = Estop()
        estop_msg.data = True
        self.estop_publisher.publish(estop_msg)
        self.get_logger().warn('ESTOP received')

    def _parse_gripper(self, payload: bytes):
        if len(payload) < 5:
            self.get_logger().warn(f'GRIPPER too short: {len(payload)}')
            return

        open_cmd = bool(payload[4])

        msg = GripperCmd()
        msg.open = open_cmd
        self.gripper_publisher.publish(msg)
        self.get_logger().info(f'GRIPPER: {"OPEN" if open_cmd else "CLOSE"}')

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
