import rclpy
import cv2
import numpy as np
import math

from collections import deque
from dataclasses import dataclass

from rclpy.node import Node
from cv_bridge import CvBridge
from sensor_msgs.msg import Image, CameraInfo

from robot_interface.msg import FieldPose

@dataclass
class CameraConfig:
    fx = 600.0
    fy = 600.0
    
    cx = 320.0
    cy = 240.0
    
    height_m = 0.30    
    tilt_deg = 30.0 

@dataclass
class DetectionConfig:
    canny_low = 50
    canny_high = 150
    hough_rho = 1.0
    hough_theta = np.pi / 180
    hough_thresh = 80
    hough_min_len = 40
    hough_max_gap = 10
    line_angle_tol = 20.0

@dataclass
class StabilityConfig:
    buffer_size = 25
    required_n = 10
    std_xy_thresh = 0.15
    std_yaw_thresh = 0.25
    min_confidence = 0.7

@dataclass
class Corner:
    u: float    
    v: float

@dataclass
class PoseEstimate:
    x: float
    y: float
    yaw: float
    confidence: float

class FieldLocalization(Node):
    def __init__(self):
        super().__init__('field_localization_node')

        self.bridge = CvBridge()

        self.cam_cfg = CameraConfig()
        self.det_cfg = DetectionConfig()
        self.stab_cfg = StabilityConfig()

        self.buffer = deque(maxlen = self.stab_cfg.buffer_size)

        self.current_depth = None
        self.published = False

        self.create_subscription(CameraInfo, '/camera/camera_info', self._on_camera_info, 10)
        self.create_subscription(Image, '/camera/depth/image_raw', self._on_depth, 10)
        self.create_subscription(Image, '/camera/color/image_raw', self._on_color, 10)

        self._pose_pub = self.create_publisher(FieldPose, '/field_pose', 10)
        self._debug_pub = self.create_publisher(Image, '/field_pose/debug', 10)

        self.get_logger().info('FieldLocalization node started')

    def _on_camera_info(self, msg: CameraInfo):
        self.cam_cfg.fx = msg.k[0]
        self.cam_cfg.fy = msg.k[4]
        
        self.cam_cfg.cx = msg.k[2]
        self.cam_cfg.cy = msg.k[5]

    def _on_depth(self, msg: Image):
        self.current_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

    def _on_color(self, msg: Image):
        if self.published:
            return

        bgr = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        debug = bgr.copy()

        estimate = self._process_frame(bgr, debug)

        if estimate is not None:
            self.buffer.append(estimate)
            self._try_publish()

        self._publish_debug(debug)

    def _process_frame(self, bgr, debug):
        edges = self._edges(bgr)
        lines = self._detect_lines(edges)

        if lines is None:
            return None

        h_lines, v_lines = self._classify_lines(lines, debug)

        if not h_lines or not v_lines:
            return None

        best_h = max(h_lines, key = _line_length)
        best_v = max(v_lines, key = _line_length)

        self._draw_line(debug, best_h, color=(0, 255, 0))
        self._draw_line(debug, best_v, color=(0, 0, 255))
        
        corner = _line_intersection(best_h, best_v)

        if corner is None:
            return None

        h, w = bgr.shape[:2]
        if not _corner_in_frame(corner, w, h, margin = 20):
            return None

        self._draw_corner(debug, corner)

        x, y = self._pixel_to_world(corner)
        yaw = self._estimate_yaw(best_h, best_v)
        confidence = _corner_confidence(corner, w, h)

        return PoseEstimate(x = x, y = y, yaw = yaw, confidence = confidence)

    def _edges(self, bgr):
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        return cv2.Canny(blur, self.det_cfg.canny_low, self.det_cfg.canny_high)

    def _detect_lines(self, edges):
        return cv2.HoughLinesP(
            edges,
            self.det_cfg.hough_rho,
            self.det_cfg.hough_theta,
            self.det_cfg.hough_thresh,
            minLineLength=self.det_cfg.hough_min_len,
            maxLineGap=self.det_cfg.hough_max_gap
        )

    def _classify_lines(self, lines, debug):
        h_lines, v_lines = [], []
        tol = math.radians(self.det_cfg.line_angle_tol)

        for seg in lines:
            x1, y1, x2, y2 = seg[0]
            theta = abs(math.atan2(y2 - y1, x2 - x1))

            cv2.line(debug, (x1, y1), (x2, y2), (100, 200, 0), 1)

            if theta < tol:
                h_lines.append(seg[0])
            elif abs(theta - math.pi / 2) < tol:
                v_lines.append(seg[0])

        return h_lines, v_lines

    def _pixel_to_world(self, corner):
        tilt = math.radians(self.cam_cfg.tilt_deg)

        if self.current_depth is not None:
            depth = self._sample_depth(corner)

            if depth is not None and depth > 0.0:
                x_n = (corner.u - self.cam_cfg.cx) / self.cam_cfg.fx
                y_n = (corner.v - self.cam_cfg.cy) / self.cam_cfg.fy

                x_cam =  depth * x_n
                y_cam =  depth * y_n
                z_cam =  depth

                x_robot =  x_cam
                y_robot =  z_cam * math.sin(tilt) - y_cam * math.cos(tilt)

                return x_robot, y_robot

        x_n = (corner.u - self.cam_cfg.cx) / self.cam_cfg.fx
        y_n = (corner.v - self.cam_cfg.cy) / self.cam_cfg.fy

        angle_v = tilt + math.atan(y_n)
        if abs(angle_v) < 1e-3:
            return 0.0, 0.0

        forward  = self.cam_cfg.height_m / math.tan(angle_v)
        lateral  = forward * x_n

        return lateral, forward

    def _sample_depth(self, corner, window = 5):
        d = self.current_depth
        h, w = d.shape[:2]

        u = int(round(corner.u))
        v = int(round(corner.v))

        u0, u1 = max(0, u - window), min(w, u + window + 1)
        v0, v1 = max(0, v - window), min(h, v + window + 1)

        patch = d[v0:v1, u0:u1].astype(np.float32)

        if patch.max() > 100:
            patch /= 1000.0

        valid = patch[patch > 0.0]
        
        if valid.size > 0:
            return float(np.median(valid))
        else:
            return None

    def _estimate_yaw(self, h_line, v_line):
        x1,  y1,  x2,  y2  = h_line
        x1v, y1v, x2v, y2v = v_line

        theta_h = math.atan2(y2  - y1,  x2  - x1)
        theta_v = math.atan2(y2v - y1v, x2v - x1v) - math.pi / 2

        return math.atan2(
            0.5 * (math.sin(theta_h) + math.sin(theta_v)),
            0.5 * (math.cos(theta_h) + math.cos(theta_v))
        )

    def _try_publish(self):
        cfg = self.stab_cfg

        if len(self.buffer) < cfg.required_n:
            return

        xs   = []
        ys   = []
        yaws = []
        conf = []

        for p in self.buffer:
            xs.append(p.x)
            ys.append(p.y)
            yaws.append(p.yaw)
            conf.append(p.confidence)

        xs   = np.array(xs)
        ys   = np.array(ys)
        yaws = np.array(yaws)
        conf = np.array(conf)

        if (np.std(xs)   > cfg.std_xy_thresh or
                np.std(ys)   > cfg.std_xy_thresh or
                np.std(yaws) > cfg.std_yaw_thresh):
            return

        w = conf / np.sum(conf)

        msg = FieldPose()
        msg.x = float(np.sum(xs * w))
        msg.y = float(np.sum(ys * w))
        msg.yaw = math.atan2(
            float(np.sum(np.sin(yaws) * w)),
            float(np.sum(np.cos(yaws) * w))
        )
        msg.confidence = float(np.mean(conf))
        msg.valid = True

        self._pose_pub.publish(msg)
        self.published = True

        self.get_logger().info(
            f"[FIELD POSE] x={msg.x:.3f}m  y={msg.y:.3f}m  "
            f"yaw={math.degrees(msg.yaw):.1f}°  conf={msg.confidence:.2f}"
        )

    def _draw_line(self, img, seg, color):
        x1, y1, x2, y2 = seg
        cv2.line(img, (x1, y1), (x2, y2), color, 2)

    def _draw_corner(self, img, corner):
        pt = (int(corner.u), int(corner.v))
        cv2.circle(img, pt, 8, (0, 255, 255), -1)
        cv2.putText(img, f"({corner.u:.0f}, {corner.v:.0f})",
                    (pt[0] + 10, pt[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    def _publish_debug(self, img):
        self._debug_pub.publish(self.bridge.cv2_to_imgmsg(img, encoding='bgr8'))

def _line_length(seg):
    return math.hypot(seg[2] - seg[0], seg[3] - seg[1])

def _line_intersection(seg1, seg2):
    x1, y1, x2, y2 = seg1
    x3, y3, x4, y4 = seg2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom

    return Corner(
        u = x1 + t * (x2 - x1),
        v = y1 + t * (y2 - y1)
    )

def _corner_in_frame(corner, w, h, margin):
    if corner.u <= margin or corner.u >= w - margin:
        return False
    if corner.v <= margin or corner.v >= h - margin:
        return False
    return True

def _corner_confidence(corner, w, h):
    dist = math.hypot(corner.u - w / 2, corner.v - h / 2)
    return float(1.0 - dist / math.hypot(w / 2, h / 2))

def main():
    rclpy.init()
    node = FieldLocalization()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()