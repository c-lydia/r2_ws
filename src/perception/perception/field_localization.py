import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import math 
import numpy as np 

from robot_interface.srv import FieldPose 

CAM_HEIGHT_M = 0.0
CAM_PITCH_RAD = 0.0
CAM_TO_ROBOT_X_M = 0.0
CAM_IMAGE_HEIGHT_PX = 480
CAM_IMAGE_WIDTH_PX = 640

WALL_MIN_DIST_M = 0.1
WALL_MAX_DIST_M = 3.0
STABLE_READING_COUNT = 5
CLUTTER_STD_TOLERANCE_M = 0.15
SAMPLE_ROW_FRACTION = 0.75
SAMPLE_ROW_BAND = 20

ROTATION_SPEED_RAD_S = 0.3
SCAN_SAMPLE_INTERVAL_S = 0.05
SCAN_COMPLETE_RAD = 2.0 * math.pi
 
WALL_MATCH_TOLERANCE_M = 0.20
ANGULAR_OPPOSITE_TOL = math.radians(25.0)
HEADING_BUCKET_DEG = 5.0

class FieldLocalization(Node):
    def __init__(self):
        super().__init__('field_localization_node')
        
        self._cb_group = ReentrantCallbackGroup()
        
        self.declare_parameter('field_width', 3.92)
        self.declare_parameter('field_height', 4.65)
        
        self.field_width = self.get_parameter('field_width').value
        self.field_height = self.get_parameter('field_height').value 
        
        self.cv_bridge = CvBridge()
        
        self.depth_image = None
        self.current_yaw = 0.0
        self.yaw_start = None
        self.prev_yaw = None 
        self.scan_readings = []
        self.aligned = False 
        
        self.depth_subscriber = self.create_subscription(Image, '/camera/image_rect_raw', self._depth_cb, 10)
        self.odom_subscriber = self.create_subscription(Odometry, '/odometry_local', self._odom_cb, 10)
        
        self.cmd_vel_publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.alignment_publisher = self.create_publisher(Bool, '/alignment', 10)
        
        self.init_pose_client = self.create_client(FieldPose, '/field_pose', callback_group = self._cb_group)
        
        self.scan_timer = self.create_timer(SCAN_SAMPLE_INTERVAL_S, self._scan_cb, callback_group = self._cb_group)
        
        self.get_logger().info(f'FieldLocalization node started - field {self.field_width} x {self.field_height}')

    def _depth_cb(self, msg: Image):
        self.depth_image = self.cv_bridge.imgmsg_to_cv2(msg, desired_encoding = 'passthrough')
        
    def _odom_cb(self, msg: Odometry):
        q = msg.pose.pose.orientation 
        self.current_yaw = math.atan2(2.0 * (q.w * q.z + q.z * q.y), 1.0 - 2.0 * (q.y**2 + q.z**2))
        
    def _scan_cb(self):
        if self.aligned:
            return 
        
        if self.depth_image is None:
            self.get_logger().warn('Waiting for depth image ...')
            return 
        
        if not self.init_pose_client.wait_for_service(timeout_sec = 0.1):
            self.get_logger().warn('Waiting for /field_pose service ....')
            return 
        
        if self.prev_yaw is not None:
            delta_yaw = self._wrap_yaw(self.current_yaw - self.prev_yaw)
            self.total_rotation += abs(delta_yaw)
            
        self.prev_yaw = self.current_yaw
        
        if self.total_rotation >= 2.0 * math.pi:
            self.scan_completed = True  
            
        if not self.scan_completed:
            self._publish_yaw(ROTATION_SPEED_RAD_S)
            distance = self._sample_distance()
            if distance is not None:
                self.scan_readings.append((self.current_yaw, distance))
        else:
            self._publish_yaw(0.0)
            self.get_logger().info(f'Scan completed - {len(self.scan_readings)} readings')
            self._compute_pose()
            
    def _sample_distance(self):
        if self.depth_image is None:
            return None 
        
        center_row = int(CAM_IMAGE_HEIGHT_PX * SAMPLE_ROW_FRACTION)
        row_start = max(0, center_row - SAMPLE_ROW_BAND)
        row_end = min(CAM_IMAGE_HEIGHT_PX, center_row + SAMPLE_ROW_BAND)
        
        strip = self.depth_image[row_start:row_end, :]
        strip_m = strip.astype(np.float32)/1000.0
        valid = strip_m[(strip_m > WALL_MIN_DIST_M) & (strip_m < WALL_MAX_DIST_M)]
        
        if valid.size < STABLE_READING_COUNT:
            return None
        
        closest = float(np.min(valid))
        std = float(np.std(valid))
        
        if std > CLUTTER_STD_TOLERANCE_M * 3.0:
            return None 
        
        ground_distance = closest * math.cos(CAM_PITCH_RAD) - CAM_TO_ROBOT_X_M
        
        if ground_distance <= 0.0:
            return None 
        
        return ground_distance
    
    def _compute_pose(self):
        if len(self.scan_readings) < 4:
            self.get_logger().error(f'Not enough scan readings ({len(self.scan_readings)}) - retrying ...')
            self._retry_scan()
            return
        
        x, y, yaw = self._match_wall_pairs()
        
        if x is None:
            self.get_logger().error('Could not match wall pairs - retrying ...')
            self._retry_scan()
            return 
        
        self.get_logger().info(f'Alignment computed: x = {x:.3f}, y = {y:.3f}, yaw = {math.degrees(yaw):.3f}')
        
        request = FieldPose.Request()
        request.x = x
        request.y = y
        request.yaw = yaw
        
        future = self.init_pose_client.call_async(request)
        future.add_done_callback(self._on_pose_set)
        
    def _match_wall_pairs(self):
        bucket_size_rad = math.radians(5.0)
        num_buckets = int(math.ceil(2.0 * math.pi/bucket_size_rad))
        
        for _ in range(num_buckets):
            buckets = []
            
        for yaw, distance in self.scan_readings:
            yaw_norm = yaw % (2.0 * math.pi)
            bucket_idx = int(yaw_norm/bucket_size_rad) % num_buckets
            buckets[bucket_idx].append((yaw, distance))
            
        bucket_mins = []
        
        for bucket in buckets:
            if bucket:
                best = min(bucket, key = lambda r: r[1])
                bucket_mins.append(best)
                
        if len(bucket_mins) < 4:
            return None, None, None
        
        best_x_pair = None
        best_y_pair = None 
        
        best_x_error = float('inf')
        best_y_error = float('inf')
        
        for i in range(len(bucket_mins)):
            yaw_i, distance_i = bucket_mins[i]
            
            for j in range(i + 1, len(bucket_mins)):
                yaw_j, distance_j = bucket_mins[j]
                
                yaw_diff = abs(self._wrap_yaw(yaw_i - yaw_j))
                
                if abs(yaw_diff - math.pi) > ANGULAR_OPPOSITE_TOL:
                    continue
                
                pair_sum = distance_i + distance_j 
                
                width_error = abs(pair_sum - self.field_width)
                
                if width_error < WALL_MATCH_TOLERANCE_M and width_error < best_x_error:
                    best_x_error = width_error 
                    best_x_pair = (yaw_i, distance_i, yaw_j, distance_j)
                    
                height_error = abs(pair_sum - self.field_height)
                
                if height_error < WALL_MATCH_TOLERANCE_M and height_error < best_y_error:
                    best_y_error = height_error
                    best_y_pair = (yaw_i, distance_i, yaw_j, distance_j)
                    
            if best_x_pair is None or best_y_pair is None:
                return None, None, None 
            
            yaw_x_i, distance_x_i, yaw_x_j, distance_x_j = best_x_pair
            yaw_y_i, distance_y_i, yaw_y_j, distance_y_j = best_y_pair
            
            if abs(self._wrap_yaw(yaw_x_i)) < abs(self._wrap_yaw(yaw_x_j)):
                x = distance_x_i
            else:
                x = self.field_width - distance_x_i
                
            if abs(self._wrap_yaw(yaw_y_i - math.pi/2.0)) < abs(self._wrap_yaw(yaw_y_j - math.pi/2.0)):
                y = distance_y_i 
            else:
                y = self.field_height - distance_y_i
                
            field_yaw = self._wrap_yaw(yaw_x_i)
                
        return float(x), float(y), float(field_yaw)
        
    def _on_pose_set(self, future):
        result = future.result()
        
        if result is not None and result.success:
            self.get_logger().info('Initial pose set - alignment complete')
            self.aligned = True 
            
            msg = Bool()
            msg.data = True 
            
            self.alignment_publisher.publish(msg)
            self.scan_timer.cancel()
            
    def _retry_scan(self):
        self.total_rotation = 0.0
        self.prev_yaw = None 
        self.scan_readings = []
        
    def _publish_yaw(self, wz):
        msg = Twist()
        msg.angular.z = wz
        self.cmd_vel_publisher.publish(msg)
    
    @staticmethod
    def _wrap_yaw(yaw):
        if abs(yaw) > math.pi:
            if yaw > 0.0:
                yaw -= 2 * math.pi
            else :
                yaw += 2 * math.pi 
        return yaw 
    
def main():
    rclpy.init()
    field_localization = FieldLocalization()
    executor = MultiThreadedExecutor
    executor.add_node(field_localization)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
            pass
    finally:
        field_localization.destroy_node()
        rclpy.shutdown()
        
if __name__ == '__main__':
    main()