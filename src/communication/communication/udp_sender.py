import rclpy 
from rclpy.node import Node
from nav_msgs.msg import Odometry
from robot_interface.msg import TargetSetter, Status

import socket
import struct
import math 

MAGIC_HEARTBEAT = 0x07
MAGIC_ODOMETRY = 0x09
MAGIC_GOODBYE = 0x08
MAGIC_STATUS = 0x0

ODOM_TIMER = 10.0
HEARTBEAT_TIMER = 2.0
STATUS_TIMER = 10.0

class UdpSender(Node):
    def __init__(self):
        super().__init__('udp_sender_node')
        
        self.odometry_subscriber = self.create_subscription(Odometry, '/odometry', self._odom_callback, 10)
        self.target_subscriber = self.create_subscription(TargetSetter, '/target_info', self._target_callback, 10)
        self.status_subscriber = self.create_subscription(Status, '/robot_status', self._status_callback, 10)
        
        self.odometry_timer = self.create_timer(1.0/ODOM_TIMER, self._odom_timer_cb)
        self.heartbeat_timer = self.create_timer(1.0/HEARTBEAT_TIMER, self._heartbeat_timer_cb)
        self.status_timer = self.create_timer(1.0/STATUS_TIMER, self._status_timer_cb)
        
        self.sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.client_ip = ''
        self.client_port = 0
        self.session_id = 0
        
        self.get_logger().info(f'UDP sender initialized')
        
    def _odom_callback(self, msg: Odometry):
        q = msg.pose.pose.orientation
        
        self.current_odom = {
            'x': msg.pose.pose.position.x,
            'y': msg.pose.pose.position.y,
            'yaw': self.quat_to_yaw(q)
        }
        
    def _target_callback(self, msg:TargetSetter):
        if msg.ip == '':
            self.get_logger().info('Target clearted - sending GOODBYE and dropping session')
            self._send_goodbye()
            self.client_ip = ''
            self.client_port = 0
            self.session_id = 0
        else:
            self.client_ip = msg.ip
            self.client_port = msg.port
            self.session_id = msg.session_id 
            self.get_logger().info(f'Taget set: {self.client_ip}:{self.client_port}, session id = {self.session_id:#010x}')
            
    def _status_callback(self, msg: Status):
        self.current_status = msg
            
    def _odom_timer_cb(self):
        if not self._session_active() or self.current_odom is None:
            return
        
        payload = struct.pack('>ddd', self.current_odom['x'], self.current_odom['y'], self.current_odom['yaw'])
        self._send(MAGIC_ODOMETRY, payload)
        self.get_logger().info(
            f'ODOMETRY x = {self.current_odom['x']:.3f}, '
            f'y = {self.current_odom['y']:.3f}, '
            f'yaw = {self.current_odom['yaw']:.3f}'
        )
        
    def _heartbeat_timer_cb(self):
        if not self._session_active():
            return 
        
        timestamp_ms = self._now_ms()
        payload = struct.pack('>II', self.session_id, timestamp_ms)
        self._send(MAGIC_HEARTBEAT, payload)
        self.get_logger().info(f'HEARTBEAT ts = {timestamp_ms}')
        
    def _status_timer_cb(self, msg: Status):
        if not self._session_active() or self.current_status is None:
            return 
        
        s = self.current_status 
        payload = struct.pack('>IBBBII', self.session_id, s.motion_state, s.dock_state, s.gripper_state, s.active_wp_index, s.remaining_count)
        self._send(MAGIC_STATUS, payload)
        self.get_logger().info(
            f'STATUS motion = {s.motion_state}, dock = {s.dock_state}, '
            f'gripper = {s.gripper_state}, wp = {s.active_wp_index}, remaining = {s.remaining_count}'
        )
        
    def _session_active(self):
        return self.client_ip != '' and self.client_port != 0 and self.session-id != 0
    
    def _send_goodbye(self):
        if not self._session_active():
            return 
        
        payload = struct.pack('>I', self.session_id)
        self._send(MAGIC_GOODBYE, payload)
        self.get_logger().info(f'GOODBYE sent - session id = {self.session_id:#010x}')
        
    def _send(self, ptype: int, payload: bytes):
        header = struct.pack('BH', ptype, len(payload))
        
        try:
            self.sender_socket.sendto(header + payload, (self.client_ip, self.client_port))
        except Exception as e:
                self.get_logger().warn(f'Send error: {e}')
                
    def _now_ms(self):
        return int(self.get_clock().now().nanoseconds//1_000_000) & 0xFFFFFFFF
        
    @staticmethod
    def _quat_to_yaw(q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y ** 2.0 + q.z ** 2.0)
        return math.atan2(siny_cosp, cosy_cosp)
    
    def destroy_node(self):
        self._send_goodbye()
        self.sender_socket.close()
        super().destroy_node()
        
def main():
    rclpy.init()
    udp_sender = UdpSender()
    try:
        rclpy.spin(udp_sender)
    except KeyboardInterrupt:
        pass
    finally:
        udp_sender.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()