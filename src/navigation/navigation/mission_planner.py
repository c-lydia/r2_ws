import rclpy
from rclpy.node import Node

from robot_interface.msg import WaypointBatch, UpdateWaypoint, Return, Estop, ActiveWaypoint, Status

from sensor_msgs.msg import Odometry

class MissionPlanner(Node):
    def __init__(self):
        super().__init__('mission_planner_node')
        
        self.wp_subscriber = self.create_subscription(WaypointBatch, '/waypoint', self.waypoint_cb, 10)
        self.update_subscriber = self.create_subscription(UpdateWaypoint, '/update_wp', self.update_wp, 10)
        self.return_subscriber = self.create_subscription(Return, '/return_flag', self.return_cb, 10)
        self.estop_subscriber = self.create_subscription(Estop, '/e_stop', self.estop_cb, 10)
        self.odom_subscriber = self.create_subscription(Odometry, '/odometry', self.odom_cb, 10)
        
        self.active_wp_publisher = self.create_publisher(ActiveWaypoint, '/active_wp', 10)
        self.status_publisher = self.create_publisher(Status, '/robot_status', 10)
        
        self.active_wp_timer = self.create_timer(0.01, self.active_wp_cb)
        self.status_timer = self.create_timer(0.1, self.status_cb)
        
    def waypoint_cb(self, msg: WaypointBatch):
        self.wp = []
        
        for i in range(msg.count):
            self.wp.append({
                'x': msg.waypoints[i * 3 + 0],
                'y': msg.waypoints[i * 3 + 1],
                'type': msg.waypoints[i * 3 + 2]
            })
            
