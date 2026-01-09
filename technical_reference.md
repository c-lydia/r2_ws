# Technical Reference

---

## Architecture

---

### Target_Setter app

![alt text](<img/Screenshot from 2025-12-06 16-46-09.png>)

---

### r2_src

!![alt text](<img/Screenshot from 2025-12-06 16-47-05.png>)

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

#### Frame conversion (in target_setter app)



---

#### Frame transformation