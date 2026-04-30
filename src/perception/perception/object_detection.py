import rclpy 
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 as cv
import numpy as np
from inference import get_model
import os

class ObjectDetection(Node):
    def __init__(self):
        super().__init__('object_detection_node')
        self.bridge = CvBridge()
        self.sub = self.create_subscription(
            Image, '/image_raw', self.callback, 10)
        self.pub = self.create_publisher(Image, '/cv_bridge_test/output', 10)

        os.environ["INFERENCE_DEVICE"] = "cuda"
        self.model = get_model(model_id="project-mamra-king/2", api_key = "G5APCSh23WuiAtf16uUD")
        
        if hasattr(self.model, 'onnx_session'):
            self.model.onnx_session.set_providers(['CPUExecutionProvider'])
    
        self.frame_count = 0
        self.rf_results = []

        self.get_logger().info('cv_bridge test node started')

    def callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        self.frame_count += 1
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        kernel = np.ones((15, 15), np.uint8)

        lower_red    = np.array([2,   40,  50])
        upper_red    = np.array([15,  140, 180])
        lower_blue   = np.array([85,  45,  40])
        upper_blue   = np.array([105, 130, 140])
        lower_purple = np.array([130, 30,  40])
        upper_purple = np.array([160, 150, 120])

        if self.frame_count % 5 == 0:
            results = self.model.infer(frame)[0]
            self.rf_results = [
                p for p in results.predictions
                if p.class_name != 'car'
            ]

        for pred in self.rf_results:
            x = int(pred.x)
            y = int(pred.y)
            w = int(pred.width / 2)
            h = int(pred.height / 2)
            cv.rectangle(frame, (x-w, y-h), (x+w, y+h), (0, 255, 0), 2)
            cv.putText(frame, f"RF:{pred.class_name} {pred.confidence:.2f}",
                       (x-w, y-h-10),
                       cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv.imshow('Camera', frame)
        cv.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = ObjectDetection()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()