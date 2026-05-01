"""
Runs on Host (native ROS2).
Captures frames, writes to shared memory,
reads detections back, publishes to /detections.
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2 as cv
import numpy as np
import json, time
from shm_bridge import ShmFrameWriter, ShmDetReader

STALENESS_MS = 50

class ObjectDetection(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        self.bridge = CvBridge()
        self.frame_writer = SHMFrameWriter()
        self.det_reader = SHMDetReader()

        self.sub = self.create_subscription(
            Image, '/image_raw', self.image_cb, 10)
        self.pub = self.create_publisher(String, '/detections', 10)

        self.frame_id = 0
        self.last_det_time = time.time()
        self.get_logger().info('ObjectDetection node started')

    def image_cb(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.frame_writer.write(self.frame_id, frame)
        self.frame_id += 1

        dets = self.det_reader.read()
        age_ms = (time.time() - self.last_det_time) * 1000

        if dets:
            self.last_det_time = time.time()

        if age_ms > STALENESS_MS:
            self.get_logger().warn(f'Stale detections: {age_ms:.0f}ms')
            return

        payload = [
            {'x1': d[0], 'y1': d[1], 'x2': d[2], 'y2': d[3],
             'conf': d[4], 'class_id': int(d[5]), 'distance': d[6]}
            for d in dets
        ]
        out = String()
        out.data = json.dumps(payload)
        self.pub.publish(out)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetection()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()