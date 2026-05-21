import rclpy
from rclpy.node import Node
from robot_interface.msg import ActiveWaypoint
from geometry_msgs.msg import Twist 
from nav_msgs.msg import Odometry
import math

KP = 0.6
KP_YAW = 0.1

MAX_VEL = 1.5
MAX_VEL_ANGULAR = 1.0

A_MAX = 20.0
A_MAX_ANGULAR = 15.0

THRESHOLD = 0.05
ANGULAR_THRESHOLD = 0.1

class RobotControl(Node):
    def __init__(self):
        super().__init__('robot_control_node')
        self.active_wp_sub = self.create_subscription(ActiveWaypoint, '/active_wp', self._active_wp_cb, 10)
        self.odome_sub = self.create_subscription(Odometry, '/odometry_local', self._odom_callback, 10)
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.01, self._timer_callback)
        
        self.prev_time = self.get_clock().now()
        
        self.current_x = None
        self.current_y = None
        self.current_yaw = None 
        
        self.desired_x = None
        self.desired_y = None
        self.desired_yaw = None 
        
    def _active_wp_cb(self, msg: ActiveWaypoint):
        self.desired_x = msg.x
        self.desired_y = msg.y 
        self.desired_yaw = msg.yaw 
        
    def _odom_callback(self, msg: Odometry):
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        orientation = msg.pose.pose.orientation
        self.current_yaw = self._quaternion_to_yaw(orientation)
        
    def _p_controller(self, error, kp):
        return kp * error
    
    def _speed_limit(self, v, max_speed):
        if abs(v) > max_speed:
            if v > 0.0:
                v = max_speed
            else:
                v = -max_speed
        return v
    
    def _rate_limit(self, v, v_prev, a_max, dt):
        dv_max = a_max * dt 
        dv = v - v_prev 
        
        if abs(dv) > dv_max:
            if dv > 0:
                dv = dv_max
            else:
                dv = -dv_max
                
        return dv + v_prev
    
    def _wrap_yaw(self, yaw):
        if abs(yaw) > math.pi:
            if yaw > 0.0:
                yaw -= 2 * math.pi
            else:
                yaw += 2 * math.pi 
        return yaw
    
    def _deadzone(self, vx, vy, wz, threshold, angular_threshold):
        if abs(vx) < threshold:
            vx = 0.0 
        if abs(vy) < threshold:
            vy = 0.0 
        if abs(wz) < angular_threshold:
            wz = 0.0 
        return vx, vy, wz
    
    def _quaternion_to_yaw(self, q): 
        return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y ** 2.0 + q.z ** 2.0))
    
    def _compute_dt(self):
        current_time = self.get_clock().now()
        dt = (current_time - self.prev_time).nanoseconds * 1e-9
        self.prev_time = current_time
        return max(dt, 1e-3)
    
    def _apply_controller(self, dx, dy, dyaw):
        vx = self._p_controller(dx, KP)
        vy = self._p_controller(dy, KP)
        wz = self._p_controller(dyaw, KP_YAW)
        return vx, vy, wz
    
    def _apply_speed_limit(self, vx, vy, wz):
        vx = self._speed_limit(vx, MAX_VEL)
        vy = self._speed_limit(vy, MAX_VEL)
        wz = self._speed_limit(wz, MAX_VEL_ANGULAR)
        return vx, vy, wz 
    
    def _apply_rate_limit(self, vx, vy, wz, dt):    
        vx = self._rate_limit(vx, self.prev_vx, A_MAX, dt)
        vy = self._rate_limit(vy, self.prev_vy, A_MAX, dt)
        wz = self._rate_limit(wz, self.prev_wz, A_MAX_ANGULAR, dt)
        
        self.prev_vx = vx
        self.prev_vy = vy
        self.prev_wz = wz
        
        return vx, vy, wz
    
    def _timer_callback(self):
        if None in [self.current_x, self.current_y, self.current_yaw,
            self.desired_x, self.desired_y, self.desired_yaw]:
            return

        x_error = self.desired_x - self.current_x
        y_error = self.desired_y - self.current_y
        yaw_error = self._wrap_yaw(self.desired_yaw - self.current_yaw)
        
        vx, vy, wz = self._apply_controller(x_error, y_error, yaw_error)
        
        distance = math.sqrt(x_error**2 + y_error**2)
        rotation_gain = min(distance / 0.5, 1.0)
        
        wz *= rotation_gain
        
        vx, vy, wz = self._apply_speed_limit(vx, vy, wz)
        
        dt = self._compute_dt()
        
        vx, vy, wz = self._apply_rate_limit(vx, vy, wz, dt)
        vx, vy, wz = self._deadzone(vx, vy, wz, THRESHOLD, ANGULAR_THRESHOLD)
        
        cmd = Twist()
        cmd.linear.x = vx
        cmd.linear.y = vy
        cmd.angular.z = wz
        self.cmd_vel_pub.publish(cmd)
        
def main():
    rclpy.init()
    robot_control = RobotControl()
    rclpy.spin(robot_control)
    robot_control.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()