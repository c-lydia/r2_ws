# Technical Reference

---

## Architecture

---

### Target_Setter app

![alt text](<img/Screenshot from 2025-12-06 16-46-09.png>)

---

### r2_src

![alt text](<img/Screenshot from 2025-12-06 16-47-05.png>)

---

## Communication protocol

---

### UDP packet structure

---

#### Waypoints packet

- **Purpose:** send a list of waypoints for the robot to follow
- **Frequency:** send when pressing Send in the app

**Packet Structure (binary):**

| **Offset** | **Size (bytes)** | **Description**                          |
|------------|------------------|------------------------------------------|
| 0          | 4                | Header (`0xAA`)                          |
| 4          | 4                | Number of waypoints (`counter`)          |
| 8          | 4                | Plan ID (version)                        |
| 12         | 16 * N           | Waypoint (X, Y) in double (8 bytes each) |

**Notes:**

- N = number of waypoints
- Coordinates are in meters, converted from percentage position
- Byte order: Little Endian

---

#### Edit waypoint packet

- **Purpose:** update a previously sent waypoint
- **Frequency:** send when user edits a waypoint via the app

**Packet structure (binary):**

| **Offset** | **Size (bytes)** | **Description**               |
|------------|------------------|-------------------------------|
| 0          | 1                | Edited flag (1 = edited)      |
| 1          | 4                | Waypoint index (1-based)      |
| 5          | 4                | Plan ID                       |
| 9          | 8                | New X coordinate (double)     |
| 17         | 8                | New Y coordinate (double)     |

- Byte order: Liitle Endian

---

#### Return message packet

- **Purpose:** send a single boolean signal to the robot
- **Frequency:** send when return button is pressed

**Packet structure:**

| **Offset** | **Size (bytes)** | **Description**                        |
|------------|------------------|----------------------------------------|
| 0          | 1                | Edited flag (0 = false, 1 = true)      |

- Byte order: a singkke byte, no additional padding

---

#### Odometry data reception

- **Purpose:** receives current robot odometry
- **Frequency:** 10Hz

**Packet structure (binary):**

| **Offset** | **Size (bytes)** | **Description**               |
|------------|------------------|-------------------------------|
| 0          | 8                | X position (double, meters)   |
| 8          | 8                | Y position (double, meters)   |
| 16         | 8                | Yaw (double, radians)         |

- Byte order: Liitle Endian
- The app always stores the latest odometry

---

### UDP data flow

---

#### Sending data

- The app uses `NetworkManager.sendWaypoints()`, `sentEdit()`, and `sendMesage()` to send data
- Wayoints are convertged to binary packets before sending
- Each send operation is donw in a separate thread to avoid blocking the UI
- Plan ID is used to differentiate waypoint plans, and the robot can track updates or edits
- All packets are sent via UDP to the robot's IP and port (default: 5050)

---

#### Receiving data

- The app listens on a persistent UDP socket (started via `startReceiving(port)`)
- Robot sends odometry packets at 10Hz, containing X, Y, Yaw in meters and radians
- Incoming packets are converted from byte arrays to doubles using `ByteBuffer` with Little Endian byte order
- The latest odometry is stored in memory (`latestOdometry`) so that waypoint calculations can reference the mot recent robot position

---

#### Processing data

- When a waypoint is added:
  - Convert the touch position on the field to normalized coordinates (0-100%)
  - Compute the target X, Y in meters using the latest odometry
  - Add the waypoint list and create a button in the UI
  - Add the waypoint list via UDP to the robto
- When a waypoint is edited:
  - User specifies index and new coordinates
  - Update the waypoint list and redraw the UI
  - Send edit packet via UDP with plan ID
- When return message is sent:
  - A single-byte packet is sent to the robot to trigger return behavior
- Odometry received is used for:
  - Displaying the robot's current position on the gamefield
  - Computing accurate target positions for new waypoints

---

## Coordinate convention and control logic

---

### Coordinate convention

---

#### Coordinate flow

- Touch → UI → App → Robot

``` java
Touch Event (screen pixels) 
   ↓ absolutePosition()
Absolute Coordinates relative to boundaryView
   ↓ normalizedPosition()
Normalized Coordinates (0–1)
   ↓ percentagePosition()
Percentage Coordinates (0–100%)
   ↓ targetPosition()
Global Frame (meters) → UDP → Robot
```

- Robot → App (Odometry)

``` java
Odometry Packet (X, Y, yaw in meters) → inputPosition()
   ↓ metersToPxX/Y
Pixels on UI → Display robot position
```

---

#### Frame definition

- Local frame:
  - Origin: the center of the robot
  - +x: forward
  - +y: left
  - +yaw: counter-clockwise
- Global frame:
  - Origin: top-left of the screen on the target_setter app
  - +x: rightward on the screen on the target_setter app
  - +y: downward on the screen on the target_setter app
  - Waypoints that is sent to the robot is in global frame
- Units:
  - On the robot and the data sent from app:
    - x: meters
    - y: meters
    - yaw: radians (data from app only send x and y, yaw must be infer from them)
    - Vx: m/s
    - Vy: m/s
    - Wz: rad/s
  - On the app:
    - x: percentage
    - y: percentage

---

#### Touch input conversion

**Absolute position (touch):**

``` java
double absoluteX = rawX - boundaryLeft;
double absoluteY = rawY - boundaryTop;
```

- Converts raw screen coordinate to coordinate relative to `boundaryView`
- Clamped to boundary edges

**Normalized position (0-1):**

``` java
double normalizedX = absoluteX / screenWidth;
double normalizedY = absoluteY / screenHeight;
```

- Represents position as fraction of the screen

**Percentage position (0-100%):**

``` java
double percentageX = normalizedX * 100.0;
double percentageY = normalizedY * 100.0;
```

- Used as intermediate format for calculation into world meters
- Checked against 0-100% boundary

**Global meters (for UDP):**

``` java
double targetX = (percentageX / 100.0) * GAME_FIELD_X;
double targetY = (percentageY / 100.0) * GAME_FIELD_Y;
```

- Converts to meters based on field dimension
- Result is sent to robot

**Robot odometry (UI display):**

``` java
inputX = odometryData[0] * (screenWidth / GAME_FIELD_X);
inputY = odometryData[1] * (screenHeight / GAME_FIELD_Y);
```

- Converts meters to pixels for UI display
- Clamped boundary using `validateBoundary()`

---

### Control logic

---

#### PD controller

``` python
dx = self.desired_x - self.current_x
dy = self.desired_y - self.current_y
        
current_yaw_p_error = self.normalize_angle(self.desired_yaw - self.current_yaw)
        
current_x_p_error_local =  math.cos(self.current_yaw) * dx + math.sin(self.current_yaw) * dy
current_y_p_error_local = -math.sin(self.current_yaw) * dx + math.cos(self.current_yaw) * dy
        
current_x_d_error = (current_x_p_error_local - self.previous_x_p_error) / self.dt
current_y_d_error = (current_y_p_error_local - self.previous_y_p_error) / self.dt
            
alpha_d = 0.3
current_x_d_error = alpha_d * current_x_d_error + (1 - alpha_d) * self.previous_x_d_error
current_y_d_error = alpha_d * current_y_d_error + (1 - alpha_d) * self.previous_y_d_error

linear_vel_x = self.k_p_linear * current_x_p_error_local + self.k_d * current_x_d_error
linear_vel_y = self.k_p_linear * current_y_p_error_local + self.k_d * current_y_d_error
angular_vel_z = self.k_p_yaw * current_yaw_p_error
```

- Units must match: meters (x, y), radians (yaw), m/s (velocities)
- Linear velocity in robot frame, angular velocity around z-axis
- Low-pass filtering applied on derivative term (`alpha_d = 0.3`)

---

#### Dead reckoning

- if the velocity exceeds maximum velocity, overwirte it with maximum velocity
- if proportional error is less than error threshold, stop the robot to prevent oscillation
- Error threshold must be small enough that the odometry isn't too far off from the actual physical distance

---

### Path planning

---

#### Waypoint callback

- Store each waypoint in a dictionary
- Append it into the queue
- Copy the waypoint in the queue to `active_target` to execute

---

#### Waypoints execution

- if `active_target` does not exist, and there's waypoint in the queue, pop the queue, then reset robot state to go to the waypoint that's being popped
- if return is triggered, and there's visited waypoint, command the robot to go the visited waypoint
- Otherwise, stop the robot

---

#### Waypoint update

- Store the edited waypointin a dictionary
- If the edited waypoint is active, use complementary to smooth the robot movement when update to prevent jumping suddenly

``` python
self.active_target['x'] = (1 - ALPHA) * self.active_target['x'] + ALPHA * update_wp['updated_x']
self.active_target['y'] = (1 - ALPHA) * self.active_target['y'] + ALPHA * update_wp['updated_y']
```

- Otherwise, just update the waypoint as normal

---

#### Pause

- Robot pauses motion at each target
- If distance from the robot to the target is less than tolerance, stop the robot
- If the elapsed time during pause exceeds pause duration, command the robot to go to the next waypoint

---

#### Return

- Update the return flag

---

### Odometry handling

---

#### Frame conversion

- Calculate velocity in local frame

``` python
linear_vel_x_local = (self.R/4) * (self.motor_vel[0] + self.motor_vel[1] + self.motor_vel[2] + self.motor_vel[3])
linear_vel_y_local = (self.R/4) * (self.motor_vel[0] - self.motor_vel[1] + self.motor_vel[2] - self.motor_vel[3])
w_z = (self.R * (-self.motor_vel[0] + self.motor_vel[1] + self.motor_vel[2] - self.motor_vel[3]))/(2 * (self.l_x + self.l_y))
```

- Convert them to global frame

``` python
v_x_global = math.cos(self.current_yaw) * linear_vel_x_local - math.sin(self.current_yaw) * linear_vel_y_local
v_y_global = math.sin(self.current_yaw) * linear_vel_x_local + math.cos(self.current_yaw) * linear_vel_y_local
```

- Integrate velocity to get position

``` python
self.x += v_x_global * self.dt 
self.y += v_y_global * self.dt
```

---

#### Offset

``` python
self.x_odom = (self.x - self.x_start) - self.frame_offset_x
self.y_odom = (self.y - self.y_start) - self.frame_offset_y
```

---

#### Yaw

- Calculate yaw from quaternion

``` python
def calculate_yaw(self, q_x, q_y, q_z, q_w):
  siny_cosp = 2 * (q_w * q_z + q_x * q_y)
  cosy_sinp = 1 - 2 * (q_y**2 + q_z**2)
  return math.atan2(siny_cosp, cosy_sinp)
```

- Normalize yaw

``` python
def normalize_angle(self, a):
  return math.atan2(math.sin(a), math.cos(a))
```

- Offset yaw

``` python
self.current_yaw = (self.yaw - self.yaw_start) + 2 * math.pi * self.overflow_counter
```

- Convert to quaternion to publish

``` python
def publish_yaw(self, yaw):
  q = Quaternion()
  q.w = math.cos(yaw/2)
  q.x = 0.0
  q.y = 0.0
  q.z = math.sin(yaw/2)
  return q
```

---

#### Frame correction

- Checked if the frame is flipped
- If it flips, add yaw by `pi`
- Recalculate velocity in global frame with the new yaw

---

### Inverse Kinematic

``` python
V_wheel = [
  Vx/self.R - Vy/self.R - omega_z*(self.lx + self.ly)/(2.0*self.R),
  Vx/self.R + Vy/self.R + omega_z*(self.lx + self.ly)/(2.0*self.R),
  Vx/self.R + Vy/self.R - omega_z*(self.lx + self.ly)/(2.0*self.R), 
  Vx/self.R - Vy/self.R + omega_z*(self.lx + self.ly)/(2.0*self.R)
]
```
