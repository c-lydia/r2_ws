# System Architecture - Target_Setter_v2.0

## System Diagram

![alt text](img/image.png)

Last updated: 2026-05-27 (v2.0)

## Packages and Nodes

The current ROS2 packages under `src/` are:

- `communication`
- `control`
- `hardware_interface`
- `manipulation`
- `navigation`
- `perception`
- `robot_interface`
- `target_setter`
- `unit_test`

Each package follows the standard ROS2 Python package layout (package.xml, setup.cfg/setup.py, tests). Key runtime nodes and entry scripts (from `src/`) are listed below so this document is an accurate, code-first system map.

Key nodes (package / script — node name):

- `communication`
  - `src/communication/communication/udp_listener.py` — `udp_listener_node` (binds 0.0.0.0:5050, parses HELLO/WAYPOINT/UPDATE/GRIPPER/ESTOP)
  - `src/communication/communication/udp_sender.py` — `udp_sender_node` (sends ODOM/HEARTBEAT/STATUS to client IP:5051)
- `navigation`
  - `src/navigation/navigation/mission_planner.py` — `mission_planner_node` (planning, STATUS publisher, active waypoint publisher)
- `control`
  - `src/control/control/robot_control.py` — `robot_control_node` (local motion controller, publishes `/cmd_vel`)
- `manipulation`
  - `src/manipulation/manipulation/gripper_control.py` — `gripper_control_node` (gripper motor + solenoid publisher)
- `hardware_interface`
  - `src/hardware_interface/hardware_interface/odometry.py` — `current_odometry` (publishes `/odometry`, `/odometry_local`, `/gripper_feedback`)
  - `src/hardware_interface/hardware_interface/can_driver.py` — `can_driver_node` (subscribes to motor/servo/pwm/solenoid topics, publishes `/encoder_feedback`)
  - `src/hardware_interface/hardware_interface/inverse_kinematic.py` — `kinematicPublisher` (subscribes `/cmd_vel`, publishes motor commands)
  - `src/hardware_interface/hardware_interface/hfi_a9.py` — `ImuPublisher` (publishes `/imu/data_raw`)
- `perception`
  - `src/perception/perception/object_detection.py` — `object_detection_node` (subscribes camera, publishes `/detection`)
  - `src/perception/perception/distance_estimation.py` — `distance_estimation_node` (subscribes `/detection` and depth, publishes `/detections_3d`)
- `robot_interface`
  - Message definitions under `src/robot_interface/msg/` (see Messages section)
- `unit_test`
  - Basic test nodes: `src/unit_test/unit_test/odom_test.py`, `status_test.py` (publish/subscribe test fixtures)

If you want, I can expand each entry with exact topics published/subscribed and a one-line description of the runtime behavior for each node.

## TS-Link Communication

All TS-Link UDP communication runs between the Android app and the robot over Wi-Fi on port `5050`.

Protocol documentation:

- **[ts_link_v2.0](ts_link_v2.0.md)** — current wire format (v2)
- **[ts_link_v1.0](ts_link_v1.0.md)** — legacy format (v1.0, superseded)

Implementation details:

- The robot UDP listener binds to `0.0.0.0:5050` and expects the app to send HELLO packets to that port.
- Protocol: `PROTOCOL_VERSION = 2` (robot enforces this on HELLO).
- On successful HELLO, the robot derives `session_id` from the app `client_id`, sets `client_port = 5051`, and will send HELLO_RESPONSE and other robot→app packets back to the app's IP on UDP port `5051`. Ensure the Android client listens on UDP port `5051` for responses.
- Heartbeat: the robot will consider the session alive only while it receives HEARTBEAT packets from the app. The listener uses `HEARTBEAT_TIMEOUT_S = 2.0` and will drop sessions after ~2s of no heartbeat. In practice the robot also sends HEARTBEAT packets every 0.5s (robot-side timer), so the app should send heartbeats at ~500ms intervals to maintain a stable session.

### App → Robot

| Packet          | ROS topic      | Description                        |
|-----------------|----------------|------------------------------------|
| HELLO           | —              | Session handshake                  |
| WAYPOINT_BATCH  | `/waypoint`    | Ordered list of waypoints          |
| UPDATE_WAYPOINT | `/update_wp`   | Edit a waypoint by index           |
| RETURN          | `/return_flag` | Return to last visited waypoint    |
| ESTOP           | `/e_stop`      | Emergency stop                     |
| GRIPPER         | `/gripper_cmd` | Open/close gripper command         |
| HEARTBEAT       | —              | Keepalive                          |
| GOODBYE         | —              | Clean session termination          |

### Robot → App

| Packet    | ROS topic        | Description                        |
|-----------|------------------|------------------------------------|
| HELLO     | —                | Session ID + status response       |
| ODOMETRY  | `/odometry`      | Position at ~10Hz (robot pose: x,y,yaw) |
| STATUS    | `/robot_status`  | State machine snapshot + active waypoint |
| HEARTBEAT | —                | Keepalive response                 |
| GOODBYE   | —                | Session termination acknowledgement|

## Interfaces Definitions

### ROS2 Topics

| Topic | Type | Publisher(s) | Subscriber(s) | Description |
|-------|------|--------------|---------------|-------------|
| `/camera/color/image_raw` | `sensor_msgs/msg/Image` | camera driver (e.g. realsense) | `object_detection` | RGB frame |
| `/camera/depth/image_rect_raw` | `sensor_msgs/msg/Image` | camera driver (e.g. realsense) | `distance_estimation` | Aligned depth frame |
| `/detection` | `robot_interface/msg/DetectionArray` | `object_detection` | `distance_estimation` | 2D detections (no distance) |
| `/detections_3d` | `robot_interface/msg/DetectionArray` | `distance_estimation` | `mission_planner`, other consumers | Detections augmented with distance |
| `/imu/data_raw` | `sensor_msgs/msg/Imu` | `hfi_a9` | odometry node | IMU measurements |
| `/encoder_feedback` | `robot_interface/msg/EncoderFeedback` | `can_driver` | various consumers | CAN encoder feedback |
| `/odometry` | `nav_msgs/msg/Odometry` | `hardware_interface/odometry` | `mission_planner`, `udp_sender` | Robot pose (x,y,yaw) |
| `/odometry_local` | `nav_msgs/msg/Odometry` | `hardware_interface/odometry` | `robot_control` | Local odometry (frame-local) |
| `/waypoint` | `robot_interface/msg/WaypointBatch` | `udp_listener` | `mission_planner` | Waypoint plan from app |
| `/update_wp` | `robot_interface/msg/UpdateWaypoint` | `udp_listener` | `mission_planner` | Single-waypoint edit |
| `/return_flag` | `robot_interface/msg/Return` | `udp_listener` | `mission_planner` | Trigger return behavior |
| `/e_stop` | `robot_interface/msg/Estop` | `udp_listener` | `robot_control`, unit tests | Emergency stop signal (`Estop.data`) |
| `/target_info` | `robot_interface/msg/TargetSetter` | `udp_listener` | `mission_planner`, `udp_sender` | Client IP/port and `session_id` (set on HELLO) |
| `/gripper_cmd` | `robot_interface/msg/GripperCmd` | `udp_listener`, `mission_planner` | `gripper_control` | Gripper open/close command |
| `/gripper_feedback` | `robot_interface/msg/EncoderFeedback` | `hardware_interface/odometry` | `gripper_control` | Joint encoder feedback for gripper |
| `/active_wp` | `robot_interface/msg/ActiveWaypoint` | `mission_planner` | `robot_control` | Local active waypoint (x,y,yaw) |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `robot_control`, `gripper_control` | `hardware_interface/inverse_kinematic` | Velocity command (vx,vy,wz) |
| `/publish_motor` | `robot_interface/msg/MotorCommand` | `manipulation/gripper_control`, `hardware_interface/inverse_kinematic` | `hardware_interface/can_driver` | Motor/CAN command topic used across controller layers |
| `/publish_digital_solenoid` | `robot_interface/msg/DigitalAndSolenoidCommand` | (intended) actuator publishers | `hardware_interface/can_driver` | CAN solenoid actuation (see mismatch note) |

Note: codebase observation — `gripper_control` publishes `DigitalAndSolenoidCommand` on `/solenoid`, but `can_driver` subscribes to `/publish_digital_solenoid`. These should be unified (suggest `/publish_digital_solenoid`) to ensure solenoid commands reach the CAN driver.

### Messages

#### `robot_interface`

Below are the exact ROS message definitions from `src/robot_interface/msg` (copied verbatim):

##### `robot_interface/msg/Detection.msg`

``` bash
std_msgs/Header header
float32 x1
float32 y1
float32 x2
float32 y2
float32 cx
float32 cy
float32 confidence
string class_name
float32 distance
bool valid
```

##### `robot_interface/msg/DetectionArray.msg`

``` bash
std_msgs/Header header
Detection[] detections
```

##### `robot_interface/msg/GripperCmd.msg`

``` bash
bool open
```

##### `robot_interface/msg/GripperJoint.msg`

``` bash
float64 joint_position
float64 joint_speed
```

##### `robot_interface/msg/Waypoint.msg`

``` bash
uint32 index
uint32 version
float64 x
float64 y
uint8 type
```

##### `robot_interface/msg/WaypointBatch.msg`

``` bash
uint32 version
Waypoint[] waypoint
```

##### `robot_interface/msg/UpdateWaypoint.msg`

``` bash
bool edited
uint32 index
uint32 version
float64 x
float64 y
uint8 type
```

##### `robot_interface/msg/Return.msg`

``` bash
bool flag
```

##### `robot_interface/msg/Estop.msg`

``` bash
bool data
```

##### `robot_interface/msg/TargetSetter.msg`

``` bash
string ip
uint16 port
uint32 session_id
```

##### `robot_interface/msg/EncoderFeedback.msg`

``` bash
uint16 can_id
float32 speed
float32 position
```

##### `robot_interface/msg/MotorCommand.msg`

``` bash
uint16 can_id
float32 goal
bool positionmode
bool speedmode
bool voltagemode
bool stop
bool reset
```

##### `robot_interface/msg/DigitalAndSolenoidCommand.msg`

``` bash
uint16 can_id

bool digital1_value
bool digital2_value
bool digital3_value
bool digital4_value

bool solenoid1_value
bool solenoid2_value
bool solenoid3_value
bool solenoid4_value
bool solenoid5_value
bool solenoid6_value
```

##### `robot_interface/msg/ActiveWaypoint.msg`

``` bash
float64 x
float64 y
float64 yaw
```

#### `sensor_msgs`

##### `sensor_msgs/msg/Image`

``` bash
std_msgs/Header header
uint32 height
uint32 width
string encoding
uint8 is_bigendian
uint32 step
uint8[] data
```

##### `sensor_msgs/msg/Imu`

``` bash
std_msgs/Header header
geometry_msgs/Quaternion orientation
float64[9] orientation_covariance
geometry_msgs/Vector3 angular_velocity
float64[9] angular_velocity_covariance
geometry_msgs/Vector3 linear_acceleration
float64[9] linear_acceleration_covariance
```

##### `sensor_msgs/msg/MagneticField`

``` bash
std_msgs/Header header
geometry_msgs/Vector3 magnetic_field
float64[9] magnetic_field_covariance
```

#### `nav_msgs`

##### `nav_msgs/msg/Odometry`

``` bash
std_msgs/Header header
string child_frame_id
geometry_msgs/PoseWithCovariance pose
geometry_msgs/TwistWithCovariance twist
```

#### `geometry_msgs`

##### `geometry_msgs/msg/Twist`

``` bash
geometry_msgs/Vector3 linear
geometry_msgs/Vector3 angular
```

##### `geometry_msgs/msg/Quaternion`

``` bash
float64 x
float64 y
float64 z
float64 w
```

##### `geometry_msgs/msg/Vector3Stamped`

``` bash
std_msgs/Header header
geometry_msgs/Vector3 vector
```

### Services

#### `std_srvs`

##### `std_srvs/srv/Trigger`

``` bash
boolean success
string message
```

## State Machine Definitions (code-accurate)

The authoritative FSMs are implemented in `src/navigation/navigation/mission_planner.py` and reflected in the STATUS message published on `/robot_status`.

Motion FSM (`MotionState` enum)

| Code | Name     | Meaning |
| ---- | -------- | ------- |
| 0    | IDLE     | No active waypoint plan; robot is idle |
| 1    | NAVIGATE | Executing waypoint plan; publishing `/active_wp` |
| 2    | RETURN   | Returning along history/backtrack path |
| 3    | PAUSED   | Temporarily halted for docking/interaction |
| 4    | FAULT    | Fault condition (estop, navigation fault, etc.) |

Common transitions (as implemented):

- `HELLO` / client connect → IDLE (session established)
- `/waypoint` received (non-empty plan) → NAVIGATE
- waypoint arrival (PICKUP/DROPOFF) → PAUSED
- `RETURN` command → RETURN
- `ESTOP` → FAULT (and sets fault_origin='estop')

Docking FSM (`DockingState` enum)

| Code | Name         | Meaning |
| ---- | ------------ | ------- |
| 0    | NONE         | No docking active |
| 4    | DOCK_STABLE  | Aligned/stable pose for gripper interaction |
| 5    | GRIPPER_READY| Safe to start gripper execution |

Notes: Docking FSM is only active while Motion FSM == `PAUSED`. The planner sets `DOCK_STABLE` then transitions to `GRIPPER_READY` when conditions (distance, alignment, timeouts) are met.

Gripper FSM (`GripperState` enum)

| Code | Name       | Meaning |
| ---- | ---------- | ------- |
| 0    | INITIALIZE | Gripper initialization/reset |
| 1    | MOVING     | Gripper moving toward target position |
| 2    | OPEN       | Gripper open state |
| 3    | CLOSE      | Gripper closed state |
| 4    | IDLE       | Stable idle state |
| 5    | UNKNOWN    | Fault / no feedback |

Execution flow (typical PICKUP):

1. NAVIGATE → drives to waypoint
2. on arrival (PICKUP) → Motion → PAUSED; Docking → DOCK_STABLE
3. Docking stabilizes → GRIPPER_READY
4. App/UI trigger or automatic command → Gripper FSM executes OPEN/CLOSE action
5. On successful grip: planner `_complete_docking()` advances waypoint, Docking resets to NONE, Motion resumes (NAVIGATE or IDLE)

Fault handling

- Navigation timeouts, stuck detection, or lost docking target set Motion FSM to `FAULT` and populate fault enums (`NavFault`, `DockFault`, `GripperFault`) in logs.

STATUS message mapping (`robot_interface/msg/Status.msg`)

- `session_id` (uint32) — session identifier assigned on HELLO
- `motion_state` (uint8) — Motion FSM value
- `dock_state` (uint8) — Docking FSM value
- `gripper_state` (uint8) — Gripper FSM value
- `active_wp_index` (uint32) — current waypoint index
- `remaining_count` (uint32) — remaining waypoints in plan

The robot is the source-of-truth: the app observes STATUS and issues control packets (WAYPOINT_BATCH, GRIPPER, RETURN, ESTOP) but should not attempt to override the planner's internal FSMs directly.

## Theory and Constraints

This section captures runtime assumptions, protocol invariants, timing requirements, and operational constraints that the code depends on. Treat the code as the source-of-truth; the items here summarize behaviours and limits you must respect when integrating or modifying the system.

- **Protocol versioning and wire format**: `PROTOCOL_VERSION = 2` is enforced by the robot listener. All TS-Link packets use a short header (1-byte type, 2-byte length) and big-endian (network order) payload encoding. Payload struct formats are defined in the code (e.g., odometry uses `'>ddd'`, heartbeat `'>II'`, status `'>IBBBII'`) — rely on those formats rather than guessing byte layouts.

- **UDP ports and session lifetimes**: robot binds `0.0.0.0:5050` for App→Robot packets; robot sends Robot→App packets to the app's IP on UDP port `5051`. HELLO establishes `session_id` and `client_port`. The listener uses `HEARTBEAT_TIMEOUT_S = 2.0` and will drop sessions after ~2s without heartbeat.

- **Timing constraints and rates**:
  - Odometry publishing: ~10 Hz from `udp_sender`/`odometry` node. Plan control loops and consumers around this rate.
  - Heartbeat: robot sends heartbeats on a 0.5 s timer; the app should send heartbeats at ≈500 ms to keep the session alive.
  - Network latency/window: allow for packet reordering or occasional loss — application-level state (session_id, sequence/version fields) is used to maintain consistency.

- **Packet size and fragmentation**: keep TS-Link payloads well under typical Wi‑Fi MTU (recommend < 1400 bytes) to avoid IP fragmentation. Waypoint batches and image/large payloads should be chunked or reduced.

- **ROS QoS recommendations**:
  - Control and safety topics (`/e_stop`, `/robot_status`, `/target_info`, `/waypoint`, `/gripper_cmd`) should use reliable, history=keep_last(1) QoS and low latency settings so they are delivered even under transient network load.
  - High-bandwidth sensors (`/camera/*`, `/camera/depth/*`) may use best_effort to reduce latency/CPU cost; consumers must tolerate occasional dropped frames.

- **Safety and priority**:
  - `Estop` and any fault condition must preempt normal operation. Implement local (node-level) safety checks so critical actuators stop even if higher-level comms fail.
  - Avoid long-running blocking calls on callbacks that handle safety messages.

- **CAN bus constraints**:
  - `can_driver` configures `can0` at 1,000,000 bps (socketcan). Ensure the physical hardware supports 1 Mbps and that system permissions allow bringing `can0` up (may require sudo or system configuration).
  - Be mindful of CAN message rates and aggregate bandwidth; heavy motor command streams can saturate the bus.

- **Topic naming and compatibility**:
  - The documentation and the runtime must use the same topic names; code mismatches will break actuation (example: `gripper_control` publishes `/solenoid` while `can_driver` subscribes to `/publish_digital_solenoid`). Resolve mismatches by choosing a canonical topic name and updating both publisher(s) and subscriber(s).

- **Operational guidance**:
  - The app must listen on UDP port `5051` and honor the `session_id` returned by HELLO.
  - Treat the robot as authoritative: the planner publishes `STATUS` and the app should issue commands (WAYPOINT_BATCH, UPDATE_WAYPOINT, RETURN, GRIPPER, ESTOP) rather than trying to directly set planner-internal state.
