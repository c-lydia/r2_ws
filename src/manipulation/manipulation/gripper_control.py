import rclpy 
from rclpy.node import Node

from robot_interface.msg import GripperCmd, GripperJoint, MotorCommand, DigitalAndSolenoidCommand, EncoderFeedback

import math 

GRIPPER_CMD_MAX = math.pi/2.0
GRIPPER_CMD_MIN = 0.0

MAX_SPEED = 1.0
A_MAX = 20.0

class GripperControl(Node):
    def __init__(self):
        super().__init__('gripper_control_node')
        
        self.gripper_subscriber = self.create_subscription(GripperCmd, '/gripper_cmd', self._gripper_cb, 10)
        self.joint_subscriber = self.create_subscription(GripperJoint, '/gripper_joint', self._joint_cb, 10)
        self.joint_feedback_subscriber = self.create_subscription(EncoderFeedback, '/gripper_feedback', self._joint_feedback_cb, 10)
        
        self.gripper_motor_publisher = self.create_publisher(MotorCommand, '/publish_motor', 10)
        self.solenoid_publisher = self.create_publisher(DigitalAndSolenoidCommand, '/solenoid', 10)
        
        self.timer = self.create_timer(0.01, self._timer_cb)
        
        self.open = False  
        
        self.desired_angle = None 
        self.current_position = None 
        self.prev_time = None 
        
    def _gripper_cb(self, msg: GripperCmd):
        self.open = msg.open 
        
        if self.open: 
            self.desired_angle = GRIPPER_CMD_MAX
        else:
            self.desired_angle = GRIPPER_CMD_MIN
            
    def _joint_cb(self, msg: GripperJoint):
        self.desired_position = msg.joint_position 
        
    def _joint_feedback_cb(self, msg: EncoderFeedback):
        self.current_position = msg.position 
        
    def _timer_cb(self):
        self._p_controller()
        self._solenoid_actuation()
        
    def _p_controller(self):
        dt = self._timer()
        
        error = self.desired_position - self.current_position 
        self.motor_speed = K_P * error 
        
        self.motor_speed = self._speed_limit(self.motor_speed, MAX_SPEED)
        self.motor_speed = self._rate_limit(self.motor_speed, prev_motor_speed, A_MAX, dt)
        
        prev_motor_speed = self.motor_speed
        
        self._publish_motor()
        
    def _solenoid_actuation(self):
        msg = DigitalAndSolenoidCommand()
        msg.can_id = YOUR_CAN_ID # replace can_id 
        msg.solenoid1_value = self.open
        self.solenoid_publisher.publish(msg)
        
    def _publish_motor(self):
        motor_msg = MotorCommand()
        motor_msg.can_id = 105
        motor_msg.speedmode  = True
        motor_msg.goal = self.motor_speed
        self.gripper_motor_publisher.publish(motor_msg)
        
    def _rate_limit(self, v, v_prev, a_max, dt):
        dv_max = a_max * dt 
        dv = v - v_prev 
        
        if abs(dv) > dv_max:
            if dv > 0:
                dv = dv_max
            else:
                dv = -dv_max
                
        return dv + v_prev
    
    def _speed_limit(self, v, max_speed):
        if abs(v) > max_speed:
            if v > 0.0:
                v = max_speed
            else:
                v = -max_speed
        return v
        
    def _timer(self):
        current_time = self.get_clock().now()
        dt = (current_time - self.prev_time).nanoseconds * 1e-9
        self.prev_time = current_time 
        
        if dt <= 0.0:
            return 
        return dt
    
def main():
    rclpy.init()
    gripper_control = GripperControl()
    try:
        rclpy.spin(gripper_control)
    except KeyboardInterrupt:
        pass
    finally:
        gripper_control.destroy_node()
        rclpy.shutdown()
 
if __name__ == '__main__':
    main()