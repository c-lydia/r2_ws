import rclpy
from rclpy.node import Node

from robot_interface.msg import WaypointBatch, UpdateWaypoint, Return, Estop, ActiveWaypoint, Status, DetectionArray, TargetSetter, GripperCmd, EncoderFeedback

from sensor_msgs.msg import Odometry

from enum import Enum

import math
import time

ARRIVAL_RADIUS_M = 0.15
DOCK_THRESHOLD_M = 0.05
GRIPPER_MAX_DIST = 0.5
GRIPPER_MIN_RAD = 0.0
GRIPPER_MAX_RAD = math.pi
GRIPPER_TIMEOUT_S = 5.0
NAV_WAYPOINT_TIMEOUT_S = 60.0
NAV_STUCK_TIMEOUT_S = 5.0
NAV_STUCK_DIST_M = 0.05
DOCK_TIMEOUT_S = 30.0
DOCK_DIVERGE_MARGIN_M = 0.05

CAM_X_OFFSET_M = 0.0 
CAM_Y_OFFSET_M = 0.0
CAM_IMAGE_WIDTH_PX = 640
CAM_HFOV_RAD = math.radians(87.0)

class MotionState(Enum):
    IDLE = 0
    NAVIGATE = 1
    RETURN = 2
    PAUSED = 3
    FAULT = 4

class DockingState(Enum):
    NONE = 0
    DOCK_STABLE = 4
    GRIPPER_READY = 5

class GripperState(Enum):
    INITIALIZE = 0
    MOVING = 1
    OPEN = 2
    CLOSE = 3
    IDLE = 4
    UNKNOWN = 5

class NavFault(Enum):
    NONE = 0
    STUCK = 1
    TIMEOUT = 2
    OBSTACLE = 3


class DockFault(Enum):
    NONE = 0
    DIVERGE = 1
    LOST_TARGET = 2
    TIMEOUT = 3

class GripperFault(Enum):
    NONE = 0
    TIMEOUT = 1
    NO_FEEDBACK = 2
    DROPPED = 3

class WpType(Enum):
    PICKUP = 0
    NAVIGATE = 1
    DROPOFF = 2

class MissionPlanner(Node):
    def __init__(self):
        super().__init__('mission_planner_node')

        self.wp_subscriber = self.create_subscription(WaypointBatch, '/waypoint', self._waypoint_cb, 10)
        self.update_subscriber = self.create_subscription(UpdateWaypoint, '/update_wp', self._update_wp_cb, 10)
        self.return_subscriber = self.create_subscription(Return, '/return_flag', self._return_cb, 10)
        self.estop_subscriber = self.create_subscription(Estop, '/e_stop', self._estop_cb, 10)
        self.odom_subscriber = self.create_subscription(Odometry, '/odometry', self._odom_cb, 10)
        self.distance_subscriber = self.create_subscription(DetectionArray, '/detections_3d', self._detection_cb, 10)
        self.target_subscriber = self.create_subscription(TargetSetter, '/target_info', self._target_cb, 10)
        self.joint_feedback_subscriber = self.create_subscription(EncoderFeedback, '/gripper_feedback', self._joint_feedback_cb, 10)

        self.active_wp_publisher = self.create_publisher(ActiveWaypoint, '/active_wp', 10)
        self.status_publisher = self.create_publisher(Status, '/robot_status', 10)
        self.gripper_cmd_publisher = self.create_publisher(GripperCmd, '/gripper_cmd', 10)

        self.active_wp_timer = self.create_timer(0.01, self._active_wp_cb)
        self.status_timer = self.create_timer(0.1, self._status_cb)
        self.gripper_cmd_timer = self.create_timer(0.01, self._gripper_cmd_cb)

        self._init_state()

    def _init_state(self):
        self.wp = []
        self.wp_version = 0
        self.wp_index = 0
        self.history = []
        self.session_id = 0

        self.motion_state = MotionState.IDLE
        self.docking_state = DockingState.NONE
        self.gripper_state = GripperState.IDLE

        self.pending_gripper_action = GripperState.CLOSE

        self.nav_fault = NavFault.NONE
        self.dock_fault = DockFault.NONE
        self.gripper_fault = GripperFault.NONE
        self.fault_origin = ''

        self.estop = False
        self._return = False

        self.current_x = 0.0
        self.current_y = 0.0
        self.current_yaw = 0.0

        self.dock_distance = float('inf')
        self.prev_dock_distance = float('inf')
        self.dock_cx = 0.0
        self.dock_valid = False
        self.dock_start = None
        self.dock_lost_since = None

        self.joint_position = 0.0
        self.gripper_state_start = None

        self.carrying = False
        self._pending_update = False

        self.nav_wp_start = None
        self.stuck_check_start = None
        self.stuck_snapshot_x = 0.0
        self.stuck_snapshot_y = 0.0

    def _waypoint_cb(self, msg: WaypointBatch):
        self.wp = list(msg.waypoint)
        self.wp_version = msg.version
        self.wp_index = 0
        self.history = []

        self.docking_state = DockingState.NONE
        self.gripper_state = GripperState.IDLE
        self.motion_state = MotionState.NAVIGATE

        self.nav_fault = NavFault.NONE
        self.dock_fault = DockFault.NONE
        self.gripper_fault = GripperFault.NONE
        self.fault_origin = ''

        self._reset_nav_fault_timer()
        self.dock_start = None
        self.dock_lost_since = None

    def _update_wp_cb(self, msg: UpdateWaypoint):
        if not msg.edited:
            return

        if msg.version != self.wp_version:
            self.get_logger().warn('Waypoint update version mismatch — ignored.')
            return

        idx = msg.index

        if 0 <= idx < len(self.wp):
            self.wp[idx].x = msg.x
        else:
            self.get_logger().warn(f'Update index {idx} out of range.')

    def _return_cb(self, msg: Return):
        self._return = msg.flag

        if msg.flag and self.motion_state not in (MotionState.FAULT, MotionState.RETURN):
            self.motion_state = MotionState.RETURN

    def _estop_cb(self, msg: Estop):
        self.estop = msg.data

        if msg.data:
            self.motion_state = MotionState.FAULT
            self.fault_origin = 'estop'
            self.get_logger().error('E_STOP activated')

    def _odom_cb(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.current_yaw = self._quat_to_yaw(q)

    def _detection_cb(self, msg: DetectionArray):
        valid = [d for d in msg.detections if d.valid and d.distance > 0]
        if not valid:
            self.dock_valid = False
            return
        nearest = min(valid, key=lambda d: d.distance)
        self.prev_dock_distance = self.dock_distance
        self.dock_distance = nearest.distance
        self.dock_cx = nearest.cx
        self.dock_valid = True

    def _target_cb(self, msg: TargetSetter):
        self.session_id = msg.session_id

    def _joint_feedback_cb(self, msg: EncoderFeedback):
        self.joint_position = msg.position

    def _active_wp_cb(self):
        self._dispatch_motion()

    def _status_cb(self):
        self._publish_status()

    def _gripper_cmd_cb(self):
        self._publish_gripper_cmd()

    def _dispatch_motion(self):
        if self.motion_state == MotionState.NAVIGATE:
            self._handle_navigate()
        elif self.motion_state == MotionState.RETURN:
            self._handle_return()
        elif self.motion_state == MotionState.PAUSED:
            self._handle_paused()
            self._dispatch_docking()
        elif self.motion_state == MotionState.IDLE:
            self._handle_idle()
        elif self.motion_state == MotionState.FAULT:
            self._handle_fault()

    def _dispatch_docking(self):
        if self.docking_state == DockingState.NONE:
            self._handle_none()
        elif self.docking_state == DockingState.DOCK_STABLE:
            self._handle_dock_stable()
        elif self.docking_state == DockingState.GRIPPER_READY:
            self._handle_gripper()
            self._dispatch_gripper()

    def _dispatch_gripper(self):
        if self.gripper_state == GripperState.INITIALIZE:
            self._handle_initialize()
        elif self.gripper_state == GripperState.MOVING:
            self._handle_moving()
        elif self.gripper_state == GripperState.OPEN:
            self._handle_open()
        elif self.gripper_state == GripperState.CLOSE:
            self._handle_close()
        elif self.gripper_state == GripperState.UNKNOWN:
            self._handle_unknown()

    def _handle_navigate(self):
        if not self.wp or self.wp_index >= len(self.wp):
            self.motion_state = MotionState.IDLE
            self._publish_stop()
            return

        active_wp = self.wp[self.wp_index]

        dx = active_wp.x - self.current_x
        dy = active_wp.y - self.current_y

        if math.hypot(dx, dy) < ARRIVAL_RADIUS_M:
            self._reset_nav_fault_timer()
            self._on_arrived(active_wp)
            return

        if self._nav_wp_timeout():
            self.nav_fault = NavFault.TIMEOUT
            self.fault_origin = 'navigation'
            self.motion_state = MotionState.FAULT
            self.get_logger().error(f'Nav timeout on waypoint {self.wp_index}')
            return

        if self._nav_stuck():
            self.nav_fault = NavFault.STUCK
            self.fault_origin = 'navigation'
            self.motion_state = MotionState.FAULT
            self.get_logger().error(f'Robot stuck at waypoint {self.wp_index}')
            return

        if self.carrying and not self.dock_valid:
            self.gripper_fault = GripperFault.DROPPED
            self.fault_origin = 'gripper'
            self.motion_state = MotionState.FAULT
            self.get_logger().error('Object dropped during transition')
            return

        self._publish_nav_cmd(active_wp)

    def _handle_return(self):
        if not self.history:
            self.motion_state = MotionState.IDLE
            self._publish_stop()
            return

        active_wp = self.history[-1]

        dx = active_wp.x - self.current_x
        dy = active_wp.y - self.current_y

        if math.hypot(dx, dy) < ARRIVAL_RADIUS_M:
            self.history.pop()
            if not self.history:
                self.motion_state = MotionState.IDLE
            self._publish_stop()
            return

        self._publish_nav_cmd(active_wp)

    def _handle_paused(self):
        if not self.wp or self.wp_index >= len(self.wp):
            self.motion_state = MotionState.IDLE
            return
        self._publish_stop()

    def _handle_idle(self):
        self._publish_stop()

    def _handle_fault(self):
        self._publish_stop()
        self._publish_status()
        self.get_logger().error(
            f'FAULT — origin: {self.fault_origin} | '
            f'nav: {self.nav_fault} | '
            f'dock: {self.dock_fault} | '
            f'gripper: {self.gripper_fault}'
        )

    def _handle_none(self):
        self._publish_stop()

    def _handle_dock_stable(self):
        if not self.dock_valid:
            if self.dock_lost_since is None:
                self.dock_lost_since = time.perf_counter()
                return
            self.dock_fault = DockFault.LOST_TARGET
            self.fault_origin = 'docking'
            self.motion_state = MotionState.FAULT
            self.get_logger().error('Docking fault: target lost')
            return
        else:
            self.dock_lost_since = None

        if self.dock_start is None:
            self.dock_start = time.perf_counter()

        if (time.perf_counter() - self.dock_start) > DOCK_TIMEOUT_S:
            self.dock_fault = DockFault.TIMEOUT
            self.fault_origin = 'docking'
            self.motion_state = MotionState.FAULT
            self.get_logger().error('Docking fault: timeout')
            return

        if self.dock_distance > self.prev_dock_distance + DOCK_DIVERGE_MARGIN_M:
            self.dock_fault = DockFault.DIVERGE
            self.fault_origin = 'docking'
            self.motion_state = MotionState.FAULT
            self.get_logger().error('Docking fault: diverging from target')
            return

        if self.dock_distance < DOCK_THRESHOLD_M:
            self.docking_state = DockingState.GRIPPER_READY
            self._set_gripper_state(GripperState.INITIALIZE)
            return

        self._publish_dock_cmd()

    def _handle_gripper(self):
        self._publish_stop()

    def _handle_initialize(self):
        init_position = 2.0 * math.pi
        if abs(self.joint_position - init_position) > 0.01:
            self._set_gripper_open(False)
        else:
            self._set_gripper_state(self.pending_gripper_action)

    def _handle_moving(self):
        if not self.dock_valid:
            self._set_gripper_state(GripperState.UNKNOWN)
            return
        if self.dock_distance < DOCK_THRESHOLD_M:
            self._set_gripper_state(self.pending_gripper_action)

    def _handle_open(self):
        if self._gripper_timeout():
            self.gripper_fault = GripperFault.TIMEOUT
            self._set_gripper_state(GripperState.UNKNOWN)
            return
        self._set_gripper_open(True)
        if abs(self.joint_position - GRIPPER_MAX_RAD) < 0.05:
            self._complete_docking()

    def _handle_close(self):
        if self._gripper_timeout():
            self.gripper_fault = GripperFault.TIMEOUT
            self._set_gripper_state(GripperState.UNKNOWN)
            return
        self._set_gripper_open(False)
        if abs(self.joint_position - GRIPPER_MIN_RAD) < 0.05:
            self._complete_docking()

    def _handle_unknown(self):
        self.gripper_fault = GripperFault.NO_FEEDBACK
        self.fault_origin = 'gripper'
        self.motion_state = MotionState.FAULT

    def _complete_docking(self):
        wp_type = self.wp[self.wp_index].type

        if wp_type == WpType.PICKUP.value:
            self.carrying = True
        elif wp_type == WpType.DROPOFF.value:
            self.carrying = False

        self.docking_state = DockingState.NONE
        self.dock_start = None
        self.dock_lost_since = None
        self._set_gripper_state(GripperState.IDLE)
        self._advance_wp()

        if self.motion_state != MotionState.IDLE:
            self.motion_state = MotionState.NAVIGATE

    def _set_gripper_state(self, state: GripperState):
        self.gripper_state = state
        self.gripper_state_start = None

    def _set_gripper_open(self, open_cmd: bool):
        self._gripper_open_cmd = open_cmd

    def _reset_nav_fault_timer(self):
        self.nav_wp_start = time.perf_counter()
        self.stuck_check_start = time.perf_counter()
        self.stuck_snapshot_x = self.current_x
        self.stuck_snapshot_y = self.current_y

    def _nav_wp_timeout(self):
        if self.nav_wp_start is None:
            self.nav_wp_start = time.perf_counter()
            return False
        return (time.perf_counter() - self.nav_wp_start) > NAV_WAYPOINT_TIMEOUT_S

    def _nav_stuck(self):
        if self.stuck_check_start is None:
            self.stuck_check_start = time.perf_counter()
            self.stuck_snapshot_x = self.current_x
            self.stuck_snapshot_y = self.current_y
            return False

        if (time.perf_counter() - self.stuck_check_start) < NAV_STUCK_TIMEOUT_S:
            return False

        moved = math.hypot(
            self.current_x - self.stuck_snapshot_x,
            self.current_y - self.stuck_snapshot_y
        )

        self.stuck_check_start = time.perf_counter()
        self.stuck_snapshot_x = self.current_x
        self.stuck_snapshot_y = self.current_y

        return moved < NAV_STUCK_DIST_M

    def _gripper_timeout(self):
        current_time = time.perf_counter()
        if self.gripper_state_start is None:
            self.gripper_state_start = current_time
            return False
        return (current_time - self.gripper_state_start) > GRIPPER_TIMEOUT_S

    def _on_arrived(self, wp):
        if wp.type == WpType.NAVIGATE.value:
            self._advance_wp()
        elif wp.type == WpType.PICKUP.value:
            self.pending_gripper_action = GripperState.CLOSE
            self.motion_state = MotionState.PAUSED
            self.docking_state = DockingState.DOCK_STABLE
        elif wp.type == WpType.DROPOFF.value:
            self.pending_gripper_action = GripperState.OPEN
            self.motion_state = MotionState.PAUSED
            self.docking_state = DockingState.DOCK_STABLE

    def _advance_wp(self):
        self.history.append(self.wp[self.wp_index])
        self.wp_index += 1
        if self.wp_index >= len(self.wp):
            self.motion_state = MotionState.IDLE

    def _active_wp_yaw(self, wp_x, wp_y):
        dx = wp_x - self.current_x
        dy = wp_y - self.current_y
        return math.atan2(dy, dx)

    def _global_to_local(self, gx, gy):
        dx = gx - self.current_x
        dy = gy - self.current_y
        cos_yaw = math.cos(-self.current_yaw)
        sin_yaw = math.sin(-self.current_yaw)
        lx = cos_yaw * dx - sin_yaw * dy
        ly = sin_yaw * dx + cos_yaw * dy
        return lx, ly

    def _camera_to_local(self, distance, cx):
        px_from_center = cx - (CAM_IMAGE_WIDTH_PX / 2.0)
        bearing = px_from_center * (CAM_HFOV_RAD / CAM_IMAGE_WIDTH_PX)

        lx = distance * math.cos(bearing) + CAM_X_OFFSET_M
        ly = distance * math.sin(bearing) + CAM_Y_OFFSET_M
        return lx, ly, bearing

    def _distance_to_joint_angle(self, distance):
        span = GRIPPER_MAX_DIST - DOCK_THRESHOLD_M
        if span > 0:
            t = (distance - DOCK_THRESHOLD_M) / span
        else:
            t = 0.0
        t = max(0.0, min(1.0, t))
        return GRIPPER_MIN_RAD + t * (GRIPPER_MAX_RAD - GRIPPER_MIN_RAD)

    def _publish_nav_cmd(self, wp):
        msg = ActiveWaypoint()
        msg.x, msg.y = self._global_to_local(wp.x, wp.y)
        msg.yaw = self._active_wp_yaw(wp.x, wp.y) - self.current_yaw
        self.active_wp_publisher.publish(msg)

    def _publish_stop(self):
        msg = ActiveWaypoint()
        msg.x = 0.0
        msg.y = 0.0
        msg.yaw = 0.0
        self.active_wp_publisher.publish(msg)

    def _publish_dock_cmd(self):
        lx, ly, bearing = self._camera_to_local(self.dock_distance, self.dock_cx)
        msg = ActiveWaypoint()
        msg.x = lx
        msg.y = ly
        msg.yaw = bearing
        self.active_wp_publisher.publish(msg)

    def _publish_status(self):
        status_msg = Status()
        status_msg.session_id = self.session_id
        status_msg.motion_state = self.motion_state.value
        status_msg.dock_state = self.docking_state.value
        status_msg.gripper_state = self.gripper_state.value
        status_msg.active_wp_index = self.wp_index
        status_msg.remaining_count = len(self.wp) - self.wp_index
        self.status_publisher.publish(status_msg)

    def _publish_gripper_cmd(self):
        msg = GripperCmd()
        msg.open = (self.gripper_state == GripperState.OPEN)
        self.gripper_cmd_publisher.publish(msg)

    @staticmethod
    def _quat_to_yaw(q):
        return math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y ** 2 + q.z ** 2)
        )

def main():
    rclpy.init()
    mission_planner = MissionPlanner()
    try:
        rclpy.spin(mission_planner)
    except KeyboardInterrupt:
        pass
    finally:
        mission_planner.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()