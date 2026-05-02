import rclpy
from rclpy.node import Node 
from rclpy.callback_groups import ReentrantCallbackGroup

from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from robot_interface.msg import DetectionArray, Detection

import time
from shm_bridge import ShmFrameWriter, ShmDetReader

STALENESS_MS = 50.0

CLASS_NAMES = {
    0: 'R', 
    1: 'B', 
    2: 'P',
    3: 'S'
}

class ObjectDetection(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        
        cb = ReentrantCallbackGroup()
        self.bridge = CvBridge()
        
        self.color_subscriber = self.create_subscription(Image, '/camera/color/image_raw', self.color_callback, 10, callback_group = cb)
        self.detection_publisher = self.create_publisher(DetectionArray, '/detection', 10)

        self.frame_writer = ShmFrameWriter()
        self.det_reader = ShmDetReader()
        
        self.frame_count = 0
        self.current_det_time = time.time()
        
        self.get_logger().info('ObjectDetection node started')
        
    def color_callback(self, msg: Image):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')

        self.frame_writer.write(self.frame_id, frame)
        self.frame_id += 1

        raw_dets = self.det_reader.read()

        if raw_dets:
            self.last_det_time = time.time()

        age_ms = (time.time() - self.last_det_time) * 1000
        
        if age_ms > STALENESS_MS:
            self.get_logger().warn(f'Stale detections: {age_ms:.0f}ms')
            return
                
        det_array = DetectionArray()
        det_array.header = msg.header

        for d in raw_dets:
            x1, y1, x2, y2, conf, class_id, _ = d

            det = Detection()
            det.header = msg.header
            det.x1 = float(x1)
            det.y1 = float(y1)
            det.x2 = float(x2)
            det.y2 = float(y2)
            det.cx = float((x1 + x2) / 2)
            det.cy = float((y1 + y2) / 2)
            det.confidence = float(conf)
            det.class_name = CLASS_NAMES.get(int(class_id), str(int(class_id)))
            det.distance = -1.0
            det.valid = True
            det_array.detections.append(det)

        self.det_pub.publish(det_array)
        
def main():
    rclpy.init()
    object_detection_node = ObjectDetection()
    rclpy.spin(object_detection_node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
