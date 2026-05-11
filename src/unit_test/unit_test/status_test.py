"""
status_test.py — Publishes fake RobotStatus on /robot_status at 10Hz.
 
Cycles through a realistic state sequence:
    IDLE → NAVIGATE (ticking wp index) → PAUSED/DOCK_STABLE → PAUSED/GRIPPER_READY → NAVIGATE → IDLE
"""

MOTION_IDLE = 0x00
MOTION_NAVIGATE = 0x01
MOTION_RETURN = 0x02
MOTION_PAUSED = 0x03

DOCK_NONE = 0x00
DOCK_STABLE = 0x04
DOCK_GRIPPER_READY = 0x05

GRIPPER_INITIALIZE = 0x00
GRIPPER_LIFTING = 0x01
GRIPPER_OPEN = 0x02
GRIPPER_CLOSE = 0x03
GRIPPER_DROPPING = 0x04
GRIPPER_IDLE = 0x05

PHASES = [
    (20, MOTION_IDLE, DOCK_NONE, GRIPPER_IDLE),
    (30, MOTION_NAVIGATE, DOCK_NONE, GRIPPER_IDLE),
    (30, MOTION_NAVIGATE, DOCK_NONE, GRIPPER_IDLE),
    (15, MOTION_PAUSED, DOCK_STABLE, GRIPPER_IDLE),
    (15, MOTION_PAUSED, DOCK_GRIPPER_READY, GRIPPER_INITIALIZE),
    (10, MOTION_PAUSED, DOCK_GRIPPER_READY, GRIPPER_LIFTING),
    (10, MOTION_PAUSED, DOCK_GRIPPER_READY, GRIPPER_OPEN),
    (10, MOTION_PAUSED, DOCK_GRIPPER_READY, GRIPPER_DROPPING),
    (30, MOTION_NAVIGATE, DOCK_NONE, GRIPPER_IDLE),
    (20, MOTION_RETURN, DOCK_NONE, GRIPPER_IDLE), 
    (20, MOTION_IDLE, DOCK_NONE, GRIPPER_IDLE),
]

import rclpy
from rclpy.node import Node

from robot_interface.msg import Status, WaypointBatch, Return, Estop, GripperCmd 

class StatusTest(Node):
    def __init__(self):
        super().__init__('status_test_node')
        
        self.status_test_pub = self.create_publisher(Status, '/robot_status', 10)
        
        self.wp_subscriber = self.create_subscription(WaypointBatch, '/waypoint', self.wp_cb, 10) 
        self.return_sub  = self.create_subscription(Return, '/return_flag', self._return_callback, 10)
        self.estop_sub   = self.create_subscription(Estop, '/e_stop', self._estop_callback, 10)
        self.gripper_sub = self.create_subscription(GripperCmd, '/gripper_cmd', self._gripper_callback, 10)
        
        self.timer = self.create_timer(0.1, self._status_test_cb)
        
        self.phase_index = 0
        self.phase_tick = 0
        self.wp_index = 0
        self.total_waypoints = 0
        
        self.get_logger().info('Status test publishing to /robot_status')
        
    def wp_cb(self, msg: WaypointBatch):
        self.total_wp = len(msg.waypoint)
        self.wp_index = 0
        self.phase_index = 0
        self.phase_tick = 0
        self.get_logger().info(f'WAYPOINT_BATCH received: {self.total_waypoints} waypoints — resetting')
 
    def _return_callback(self, msg: Return):
        if not msg.flag:
            return
        
        self.phase_idx = 9
        self.phase_ticks = 0
        self.get_logger().info('RETURN received — jumping to RETURN phase')
 
    def _estop_callback(self, msg: Estop):
        if not msg.data:
            return
        
        self.phase_idex = 0
        self.phase_tick = 0
        self.wp_index = 0
        self.total_waypoints = 0
        self.get_logger().warn('ESTOP received — resetting to IDLE')
 
    def _gripper_callback(self, msg: GripperCmd):
        self.phase_idx = 4
        self.phase_ticks = 0
        self.get_logger().info(f'GRIPPER {"OPEN" if msg.open else "CLOSE"} received — jumping to gripper sequence')
            
        
    def _status_test_cb(self):
        if self.phase_index >= len(PHASES):
            self.phase_index = 0
            
        duration, motion, dock, gripper = PHASES[self.phase_index]
        
        if motion == MOTION_NAVIGATE:
            advanced = self.phase_index//2
            
            if advanced < self.total_waypoints - 1:
                self.wp_index = advanced
            else:
                self.wp_index = self.total_waypoints - 1
                
        remaining = self.total_waypoints - self.wp_index - 1
        
        if remaining < 0:
            remaining = 0
            
        status_msg = Status()
        status_msg.motion_state = motion
        status_msg.dock_state = dock
        status_msg.gripper_state = gripper
        status_msg.active_wp_index = self.wp_index
        status_msg.remaining_count = remaining 
        
        self.status_test_pub.publish(status_msg)
        
        self.get_logger().debug(
            f'STATUS motion = {motion}, dock = {dock}, gripper = {gripper}, '
            f'wp = {self.wp_index}, remaining = {remaining}'
        )
        
        self.phase_tick += 1
        
        if self.phase_tick >= duration:
            self.phase_tick = 0
            self.phase_index += 1
            
def main():
    rclpy.init()
    status_test = StatusTest()
    try:
        rclpy.spin(status_test)
    except KeyboardInterrupt:
        pass
    finally:
        status_test.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()