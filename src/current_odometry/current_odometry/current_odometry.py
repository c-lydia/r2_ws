import math
import time
import threading

import numpy as np 
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup

from geometry_msgs.msg import Quaternion
from nav_msgs.msg import Odometry 
from sensor_msgs.msg import Imu
from std_srvs.srv import Trigger

from custom_messages.msg import EncoderFeedback 
from typing import List, Tuple 

WHEEL_RADIUS_M = 0.127/2
HALF_TRACK_M = 0.662/2
ROTARY_RADIUS_M = 0.028613333

CAN_ID_MIN = 100
CAN_ID_MAX = 110

DRIVE_MOTOR_ID_OFFSET = 100
DRIVE_MOTOR_INDEX_BASE = 1
NUM_DRIVE_MOTORS = 4

ROTARY_X_MOTOR_ID = 10
ROTARY_Y_MOTOR_ID = 9

DEADZONE = 0.05

class OdomState:
    def __init__(self):
        self.x: float = 0.0
        self.y: float = 0.0
        
        self.x_start: float | None = None
        self.y_start: float | None = None
        
        self.x_odom: float = 0.0
        self.y_odom: float = 0.0
        
        self.current_yaw: float = 0.0
        self.yaw_start: float | None = None
        
        self.previous_time: float = 0.0
        
        self.motor_vel: List[float] = [0.0] * NUM_DRIVE_MOTORS
        self.motor_position: List[float] = [0.0] * NUM_DRIVE_MOTORS
        self.prev_motor_position: List[float | None] = [None] * NUM_DRIVE_MOTORS
        self.prev_encoder_time: List[float | None] = [None] * NUM_DRIVE_MOTORS
        
        self.vx_rotary: float = 0.0
        self.vy_rotary: float = 0.0
        
        self.rotary_received: np.ndarray = np.zeros(2, dtype = int)
        
    def reset(self) -> None:
        self.__init__()

class CurrentOdometry(Node):
    def __init__(self):
        super().__init__('current_odometry')

        self._cb_group = ReentrantCallbackGroup()
        
        self._lock = threading.Lock()
        self._state = OdomState()
        
        self.can_driver_subscriber = self.create_subscription(EncoderFeedback, '/encoder_feedback', self._encoder_feedback_callback, 10, callback_group = self._cb_group)
        self.sensor_imu_subscriber = self.create_subscription(Imu, '/imu/data_raw', self._imu_callback, 10, callback_group = self._cb_group)
        self.current_odom_publisher = self.create_publisher(Odometry, '/current_odom', 10)
        
        self.reset_srv = self.create_service(Trigger, '/reset_odometry', self._reset_callback, callback_group = self._cb_group)
        
        self.get_logger().info('CurentOdometry node initialized')

    def _imu_callback(self, msg: Imu) -> None:
        raw_yaw = self._quaternion_to_yaw(
            msg.orientation.x, 
            msg.orientation.y,
            msg.orientation.z,
            msg.orientation.w
        ) 
        
        with self._lock:
            s = self._state 
            
            if s.yaw_start is None:
                s.yaw_start = raw_yaw 
            
            s.current_yaw = raw_yaw - s.yaw_start 

    def _encoder_feedback_callback(self, msg: EncoderFeedback) -> None:
        slot = self._classify_can_id(msg.can_id)
        
        if slot is None:
            return 
        
        with self._lock:
            s = self._state 
            self._update_motor_state(s, slot, msg)
            vx_local, vy_local = self._select_valocity_source(s)
            yaw_snapshot = s.current_yaw
            vx_global, vy_global = self._frame_transform(vx_local, vy_local, yaw_snapshot)
            result = self._integrate_position(s, vx_global, vy_global, yaw_snapshot)
            
        if result is not None:
            self._publish_odometry(*result)
    
    def _classify_can_id(self, can_id: int) -> int:
        if DRIVE_MOTOR_ID_OFFSET <= can_id <= DRIVE_MOTOR_ID_OFFSET + NUM_DRIVE_MOTORS:
            return can_id - DRIVE_MOTOR_ID_OFFSET
        else:
            self.get_logger().info(f'Unknonw CAN ID: {can_id}')
            
    def _update_motor_state(self, s: OdomState, slot: int, msg: EncoderFeedback) -> None:
        if 0 <= slot < NUM_DRIVE_MOTORS:
            idx = slot
            motor_position_meters = self._unit_conversion(s, idx, msg)
            
            if msg.speed != 0.0:
                s.motor_vel[idx] = WHEEL_RADIUS_M * msg.speed 
                
                if abs(s.motor_vel[idx]) < DEADZONE:
                    s.motor_vel[idx] = 0.0
                        
                s.prev_motor_position[idx] = motor_position_meters
                s.prev_encoder_time[idx] = time.perf_counter()
            else:
                self._estimate_motor_velocity(s, idx, motor_position_meters)
                
            self.get_logger().debug(f'Drive motor CAN {msg.can_id}, idx {idx}, speed {s.motor_vel[idx]:.4f}, pos {msg.position:.4f}')
        elif msg.can_id == ROTARY_X_MOTOR_ID:
            s.vx_rotary = ROTARY_RADIUS_M * msg.speed 
            
            if abs(s.vx_rotary) < DEADZONE:
                s.vx_rotary = 0.0
                
            s.rotary_received[0] = 1
            self.get_logger().debug(f'Rotary X speed: {s.vx_rotary:.4f}')
        elif msg.can_id == ROTARY_Y_MOTOR_ID:
            s.vy_rotary = ROTARY_RADIUS_M * msg.speed 
            
            if abs(s.vy_rotary) < DEADZONE:
                s.vy_rotary = 0.0
                
            s.rotary_received[1] = 1
            self.get_logger().debug(f'Rotary Y speed: {s.vy_rotary:.4f}')
            
        if s.rotary_received.sum() == 2:
            s.rotary_received[:] = 0
    
    def _select_valocity_source(self, s: OdomState):
        return self._forward_kinematics(s.motor_vel)
    
    def _integrate_position(self, s: OdomState, vx_global: float, vy_global: float, yaw: float) -> Tuple[float, float, float, float, Quaternion]:
        current_time = time.perf_counter()
        
        if s.previous_time == 0.0:
            s.previous_time = current_time
            return None
        
        dt = current_time - s.previous_time 
        s.previous_time = current_time
        
        s.x += vx_global * dt 
        s.y += vy_global * dt 
        
        if s.x_start is None:
            s.x_start = s.x
            
        if s.y_start is None:
            s.y_start = s.y 
            
        s.x_odom = s.x - s.x_start 
        s.y_odom = s.y - s.y_start
        
        return vx_global, vy_global, s.x_odom, s.y_odom, self._yaw_to_quaternion(yaw)
    
    def _publish_odometry(self, vx: float, vy: float, x: float, y: float, yaw_q: Quaternion) -> None:
        odom_msg = Odometry()
        odom_msg.twist.twist.linear.x = vx
        odom_msg.twist.twist.linear.y = vy
        odom_msg.pose.pose.position.x = x
        odom_msg.pose.pose.position.y = y
        odom_msg.pose.pose.orientation = yaw_q
        self.current_odom_publisher.publish(odom_msg)
        self.get_logger().info(f'Odom: vel ({vx:.4f}, {vy:.4f}), pos ({x:.4f}, {y:.4f}), yaw: {yaw_q}')
    
    def _reset_callback(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        with self._lock:
            self._state.reset()
            
        response.success = True
        response.message = "Odometry reset"
        self.get_logger().info('Odometry reset via service call')
        return response
    
    @staticmethod
    def _estimate_motor_velocity(state: OdomState, index: int, position: float) -> None:
        now = time.perf_counter()
        prev_pos = state.prev_motor_position[index]
        prev_time = state.prev_encoder_time[index]

        if prev_pos is not None and prev_time is not None:
            dt = now - prev_time
            
            if dt > 0.0 and dt >= 0.001:
                state.motor_vel[index] = (position - prev_pos)/dt

        state.prev_motor_position[index] = position
        state.prev_encoder_time[index] = now
        
    @staticmethod 
    def _quaternion_to_yaw(qx: float, qy: float, qz: float, qw: float) -> float:
        siny_cosp = 2.0 * (qw * qz + qx * qy)
        cosy_cosp = 1.0 - 2.0 * (qy**2.0 + qz**2.0)
        return math.atan2(siny_cosp, cosy_cosp)
    
    @staticmethod
    def _yaw_to_quaternion(yaw: float) -> Quaternion:
        q = Quaternion()
        q.w = math.cos(yaw/2.0)
        q.x = 0.0
        q.y = 0.0
        q.z = math.sin(yaw/2.0)
        return q 
    
    @staticmethod
    def _frame_transform(vx_local: float, vy_local: float, yaw: float) -> Tuple[float, float]:
        c = math.cos(yaw)
        s = math.sin(yaw)
        return c * vx_local - s * vy_local, s * vx_local + c * vy_local
    
    @staticmethod
    def _forward_kinematics(motor_vel: List[float]) -> Tuple[float, float]:
        k = 1.0/(2.0 * math.sqrt(2.0))
        
        corrected_vel = [
            motor_vel[0],
            motor_vel[1],
            motor_vel[2],
            motor_vel[3]
        ]
        
        vx = k * (corrected_vel[0] + corrected_vel[1] + corrected_vel[2] + corrected_vel[3])
        vy = k * (-corrected_vel[0] + corrected_vel[1] - corrected_vel[2] + corrected_vel[3])

        return vx, vy
    
    @staticmethod
    def _unit_conversion(s: OdomState, idx: int, msg: EncoderFeedback) -> float:
        s.motor_position[idx] = msg.position
        wheel_pose_meters = WHEEL_RADIUS_M * s.motor_position[idx]
        return wheel_pose_meters 

def main():
    rclpy.init()
    current_odometry = CurrentOdometry()
    
    executor = MultiThreadedExecutor()
    executor.add_node(current_odometry)
    
    try: 
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        current_odometry.destroy_node()
        rclpy.shutdown()
    
if __name__ == '__main__': 
    main()
