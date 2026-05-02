import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from robot_interface.msg import DetectionArray
from geometry_msgs.msg import Transform

import numpy as np

DEPTH_SAMPLE_RADIUS = 2 
DEPTH_STALENESS_THRESHOLD_MS = 50.0 

class DistanceEstimationNode(Node):
    def __init__(self):
        super().__init__('distance_estimation_node')

        callback_group = ReentrantCallbackGroup()

        self.cv_bridge = CvBridge()

        self.current_depth_image = None
        self.current_depth_timestamp = None

        self.depth_image_subscription = self.create_subscription(
            Image,
            '/camera/depth/image_rect_raw',
            self.depth_image_callback,
            10,
            callback_group = callback_group
        )

        self.detection_subscription = self.create_subscription(
            DetectionArray,
            '/detection',
            self.detection_callback,
            10,
            callback_group = callback_group
        )

        self.detection_with_distance_publisher = self.create_publisher(
            DetectionArray,
            '/detections_3d',
            10
        )

        self.get_logger().info('Distance Estimation Node has started')

    def depth_image_callback(self, image_message: Image):
        self.current_depth_image = self.cv_bridge.imgmsg_to_cv2(
            image_message,
            desired_encoding='passthrough'
        )

        self.current_depth_timestamp = self.get_clock().now()

    def detection_callback(self, detection_message: DetectionArray):
        if self.current_depth_image is None:
            self.get_logger().warn('No depth image available yet')
            return

        current_time = self.get_clock().now()
        age_in_milliseconds = (
            current_time - self.current_depth_timestamp
        ).nanoseconds / 1e6

        if age_in_milliseconds > DEPTH_STALENESS_THRESHOLD_MS:
            self.get_logger().warn(
                f'Depth image is stale: {age_in_milliseconds:.2f} ms old'
            )
            return

        output_message = DetectionArray()
        output_message.header = detection_message.header

        for detection in detection_message.detections:

            distance_in_meters = self._sample_depth_region(
                self.current_depth_image,
                int(detection.center_x),
                int(detection.center_y)
            )

            detection.distance = (
                distance_in_meters if distance_in_meters is not None else -1.0
            )

            detection.valid = distance_in_meters is not None

            output_message.detections.append(detection)

        self.detection_with_distance_publisher.publish(output_message)

        self._log_detections(output_message)

    def _sample_depth_region(self, depth_image, center_x, center_y):
        image_height, image_width = depth_image.shape

        y_start = max(0, center_y - DEPTH_SAMPLE_RADIUS)
        y_end = min(image_height, center_y + DEPTH_SAMPLE_RADIUS + 1)

        x_start = max(0, center_x - DEPTH_SAMPLE_RADIUS)
        x_end = min(image_width, center_x + DEPTH_SAMPLE_RADIUS + 1)

        depth_region = depth_image[y_start:y_end, x_start:x_end]

        valid_depth_values = depth_region[depth_region > 0]

        if valid_depth_values.size == 0:
            return None

        median_depth_in_millimeters = np.median(valid_depth_values)

        return float(median_depth_in_millimeters) / 1000.0

    def _log_detections(self, detection_message: DetectionArray):
        for detection in detection_message.detections:
            self.get_logger().info(
                f'Class: {detection.class_name} | '
                f'Confidence: {detection.confidence:.2f} | '
                f'Distance: {detection.distance:.2f} meters | '
                f'Valid: {detection.valid}'
            )

def main():
    rclpy.init()
    distance_estimation_node = DistanceEstimationNode()
    rclpy.spin(distance_estimation_node)
    distance_estimation_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()