# TS-Link Protocol v2.0

## Overview

UDP-based binary protocol used by the v1.1 TS-ROS2 stack between the app (client) and robot (server).
All packets share a common 3-byte header. Byte order is big-endian throughout.

## Header

Prepended to every packet.

| Field  | Type   | Description                               |
|--------|--------|-------------------------------------------|
| type   | uint8  | Packet type ID                            |
| length | uint16 | Payload length in bytes (excludes header) |

## Packet Type IDs

| ID   | Name            | Direction     | Description                                             |
| ---- | --------------- | ------------- | ------------------------------------------------------- |
| 0x01 | HELLO           | App → Robot   | Initiates session handshake                             |
| 0x02 | HELLO_RESPONSE  | Robot → App   | Returns session_id + status                             |
| 0x03 | WAYPOINT_BATCH  | App → Robot   | Sends full navigation plan (replaces existing plan)     |
| 0x04 | UPDATE_WAYPOINT | App → Robot   | Edits a waypoint in current plan using seq for ordering |
| 0x05 | RETURN          | App → Robot   | Robot retraces/returns via visited path                 |
| 0x06 | ESTOP           | App → Robot   | Immediate stop + transition to IDLE                     |
| 0x07 | HEARTBEAT       | Bidirectional | Keepalive for session watchdog                          |
| 0x08 | GOODBYE         | Bidirectional | Clean session teardown                                  |
| 0x09 | ODOMETRY        | Robot → App   | Continuous pose stream (x, y, yaw)                      |
| 0x10 | GRIPPER         | App → Robot   | Open/close gripper command                              |
| 0x0A | STATUS          | Robot → App   | Motion + docking + waypoint progress                    |

## App Waypoint Type Codes

| Type       | Code |
| ---------- | ---- |
| NAVIGATION | 0x00 |
| PICKUP     | 0x01 |
| DROPOFF    | 0x02 |

## Status Codes

Used in HELLO response field.

| Code | Meaning                                |
|------|----------------------------------------|
| 0x00 | OK                                     |
| 0x01 | Reject (bad session, malformed packet) |
| 0x02 | Out of bounds (index exceeds plan size)|
| 0x03 | Stale (seq out of order)               |

## Robot State Codes

Used in the STATUS packet.

### Motion State Codes

| Code | Meaning  | Description                               |
| ---- | -------- | ----------------------------------------- |
| 0x00 | IDLE     | Robot is stationary, no active task       |
| 0x01 | NAVIGATE | Actively following waypoint path          |
| 0x02 | RETURN   | Returning along path history              |
| 0x03 | PAUSED   | Motion halted (can include docking phase) |

### Docking State Codes

Only valid when `motion_state == PAUSED`

| Code | Meaning       | Description                                      |
| ---- | ------------- | ------------------------------------------------ |
| 0x00 | NONE          | Not in docking phase                             |
| 0x04 | DOCK_STABLE   | Robot has reached final pose, stable and aligned |
| 0x05 | GRIPPER_READY | Robot is fully ready for gripper interaction     |

> Codes 4–5 are NOT motion states.
> They are docking sub-states emitted during PAUSED phase only.

## Gripper State Codes (NEW)

This reflects the live gripper process state shown in the app.

| Code | Meaning     |
|------|-------------|
| 0x00 | INITIALIZE  |
| 0x01 | LIFTING     |
| 0x02 | OPEN        |
| 0x03 | CLOSE       |
| 0x04 | DROPPING    |
| 0x05 | IDLE        |
| 0x06 | UNKNOWN     |

## Packets — App → Robot

![alt text](img/TS-Link_v2.0_app_to_robot.png)

### HELLO

Initiates a session. App retries until a HELLO response is received.

| Field     | Type   | Description           |
|-----------|--------|-----------------------|
| version   | uint8  | Protocol version      |
| client_id | uint32 | Unique app identifier |

### WAYPOINT_BATCH

Sends a full navigation plan. Replaces any existing plan.

| Field     | Type                | Description                          |
|-----------|---------------------|--------------------------------------|
| session_id| uint32              | Session ID from HELLO response       |
| plan_id   | uint32              | Unique plan identifier               |
| count     | uint32              | Number of waypoints                  |
| waypoints | float64 × 2 + uint8 | Interleaved x, y pairs (count pairs) |

Each waypoint:

| Field | Type    | Description                   |
| ----- | ------- | ----------------------------- |
| x     | float64 | Position X                    |
| y     | float64 | Position Y                    |
| type  | uint8   | NAVIGATION / PICKUP / DROPOFF |

### UPDATE_WAYPOINT

Edits a single waypoint in the active plan. Robot discards if seq is stale.

| Field      | Type    | Description                                |
| ---------- | ------- | ------------------------------------------ |
| session_id | uint32  | Active session                             |
| seq        | uint32  | Monotonic counter (prevents stale updates) |
| flag       | uint8   | Reserved (currently always 0x00)           |
| index      | uint32  | Waypoint index in active plan              |
| x          | float64 | Updated position X                         |
| y          | float64 | Updated position Y                         |
| type       | uint8   | Updated waypoint type                      |

> Robot MUST reject UPDATE_WAYPOINT if seq is stale or duplicate

### RETURN

Instructs the robot to navigate back through its visited waypoint history.

| Field      | Type   | Description                    |
|------------|--------|--------------------------------|
| session_id | uint32 | Session ID from HELLO response |

### ESTOP

Emergency stop. Robot halts immediately and transitions to IDLE.
App sends this packet 3–5 times in rapid succession — no acknowledgement.

| Field      | Type   | Description                    |
|------------|--------|--------------------------------|
| session_id | uint32 | Session ID from HELLO response |

### GRIPPER

Gripper command packet. Used to open or close the gripper during manipulation.

| Field      | Type   | Description                                    |
|------------|--------|------------------------------------------------|
| session_id | uint32 | Session ID from HELLO response                 |
| open       | uint8  | `1` = open, `0` = close                        |

> GRIPPER should be sent only when `dock_state == GRIPPER_READY`.

### HEARTBEAT

Keepalive. App sends every ~500ms. Robot transitions to IDLE and stops if
no heartbeat is received within the watchdog timeout.

| Field      | Type   | Description                  |
|------------|--------|------------------------------|
| session_id | uint32 | Session ID from HELLO response |
| timestamp  | uint32 | Sender millisecond timestamp |

### GOODBYE

Clean session termination. Robot invalidates the session on receipt.

| Field      | Type   | Description                    |
|------------|--------|--------------------------------|
| session_id | uint32 | Session ID from HELLO response |

## Packets — Robot → App

![alt text](img/TS-Link_v2_robot_to_app.png)

### HELLO (response)

Sent in response to a HELLO from the app.

| Field      | Type   | Description                          |
|------------|--------|--------------------------------------|
| session_id | uint32 | Assigned session ID for this session |
| status     | uint8  | 0x00 = OK, 0x01 = Reject             |

### ODOMETRY

Streamed continuously at ~10Hz.

| Field | Type    | Description             |
|-------|---------|-------------------------|
| x     | float64 | Robot x position (m)    |
| y     | float64 | Robot y position (m)    |
| yaw   | float64 | Robot heading (radians) |

### STATUS

Streamed ~10Hz. This is the primary sync source for the UI.

| Field            | Type   | Description                          |
|------------------|--------|--------------------------------------|
| session_id       | uint32 | Active session ID                    |
| motion_state     | uint8  | Motion FSM state (0–3)               |
| dock_state       | uint8  | Docking/UI state (1,2,4,5)           |
| gripper_state    | uint8  | Gripper execution state (0–6)        |
| active_wp_index  | uint32 | Current waypoint index               |
| remaining_count  | uint32 | Remaining waypoints                  |

### HEARTBEAT

Keepalive response. App shows disconnected state if this stops arriving.

| Field      | Type   | Description                  |
|------------|--------|------------------------------|
| session_id | uint32 | Current session ID           |
| timestamp  | uint32 | Sender millisecond timestamp |

### GOODBYE

Acknowledgement of app GOODBYE, or robot-initiated clean shutdown.

| Field      | Type   | Description        |
|------------|--------|--------------------|
| session_id | uint32 | Current session ID |

## Session Lifecycle

1. App sends **HELLO** (retries until response is received or timeout)
2. Robot replies with **HELLO_RESPONSE** carrying `session_id`
3. All subsequent packets from app MUST include `session_id`
4. Robot silently drops any packet with a mismatched `session_id`
5. Robot resets internal `seq` counter at session start
6. Either side may send **GOODBYE** to terminate session cleanly
7. On app restart: new HELLO → new `session_id` → fresh session state

## Edit Reliability

**UPDATE_WAYPOINT** is a fire-and-forget UDP operation.

* The app increments `seq` per update request
* Robot uses `seq` to reject stale or duplicate updates
* There is no explicit ACK packet

### Success detection

The app considers an update successful when:

* `STATUS.active_wp_index` reflects the updated waypoint
* AND no newer `seq` overwrote the update

### Failure handling

* If timeout occurs, the app may resend using the same waypoint data but a new `seq`
* Robot ignores updates where `seq <= last_seen_seq`

## Waypoint Execution Semantics

1. WAYPOINT_BATCH replaces the entire active plan
2. Robot begins execution immediately after receipt
3. Waypoints are processed sequentially using `active_wp_index`
4. `remaining_count` reflects dynamic execution progress
5. Waypoint `type` affects robot behavior at arrival:

   * NAVIGATION → standard traversal point
   * PICKUP → docking + gripper interaction expected
   * DROPOFF → docking + release interaction expected

## Docking Behaviour

Docking is a **secondary state machine active only during PAUSED motion state**.

When robot approaches a PICKUP or DROPOFF waypoint:

1. Motion transitions to **PAUSED**
2. Robot enters docking sequence:
   * `DOCK_STABLE (0x04)` → alignment complete
   * `GRIPPER_READY (0x05)` → safe manipulation window
3. Robot remains in PAUSED while docking conditions are valid

> Docking states MUST NOT be interpreted as motion states.
> They are only valid when `motion_state == PAUSED`

## Gripper Behaviour

GRIPPER commands are only valid when:

``` bash
dock_state == GRIPPER_READY
```

### On GRIPPER command

1. Robot executes open/close action immediately
2. Action is treated as a **transient event (not a state)**
3. After completion:

   * `dock_state` is reset to `NONE`
   * Robot transitions back to motion execution

### Post-gripper transition

Robot behavior depends on context:

* If more waypoints remain → resume **NAVIGATE**
* If in return mode → continue **RETURN**
* If plan completed → transition to **IDLE**

## ESTOP Behaviour

On **ESTOP** receipt the robot:

1. Immediately publishes zero velocity command
2. Cancels current motion trajectory
3. Clears active waypoint execution context
4. Transitions motion state to **IDLE**
5. Resets docking state to **NONE**
6. Keeps session alive (does NOT reset session_id)

App may resume by sending a new WAYPOINT_BATCH without re-handshaking.

## Heartbeat Behaviour

* App sends HEARTBEAT every ~500ms
* Robot uses heartbeat timeout to detect loss of connectivity
* If heartbeat is lost:

  * robot stops motion safely
  * transitions to IDLE
  * clears docking state

Robot HEARTBEAT is purely informational and does not affect control flow.

## Migration from v1

See `ts_link_v1.0.md` for legacy behavior and limitations.

### Key breaking changes in v2

* Big-endian encoding replaces little-endian format
* 3-byte explicit header introduced for all packets
* Session-based communication is mandatory (HELLO required)
* STATUS replaces implicit robot state inference
* Docking state introduced as a second-layer FSM
* Waypoint `type` field introduced (NAVIGATION / PICKUP / DROPOFF)
* UPDATE_WAYPOINT uses monotonic `seq` for ordering guarantees
* Heartbeat replaces idle-time timeout behavior
* Gripper becomes event-driven instead of state-driven
