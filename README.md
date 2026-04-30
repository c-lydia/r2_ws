# Target Setter — v1.1

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue?logo=ros)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python)
![C++](https://img.shields.io/badge/C++-17-blue?logo=c%2B%2B)
![Android](https://img.shields.io/badge/Android-App-green?logo=android)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?logo=opencv)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![Navigation](https://img.shields.io/badge/Navigation-Waypoint%20Based-blueviolet)
![Control](https://img.shields.io/badge/Control-P%20Controller-orange)
![Communication](https://img.shields.io/badge/Protocol-UDP-lightblue)
![Architecture](https://img.shields.io/badge/System-Robotics%20Stack-critical)
![NVIDIA](https://img.shields.io/badge/NVIDIA-RTX%203050-76B900?logo=nvidia)
![CUDA](https://img.shields.io/badge/CUDA-12.1-blue?logo=nvidia)
![MSI](https://img.shields.io/badge/Hardware-MSI%20Cyborg%2015-red?logo=msi)
![Status](https://img.shields.io/badge/Status-Optimized-brightgreen)

## Overview

A semi-autonomous waypoint navigation system. Waypoints are placed on a touch-screen map (global frame) and sent to the robot over UDP at 10 Hz. The robot executes them sequentially using a P controller inside a ROS2 node, with a state machine managing navigation, pausing, and return behaviour.

This version is optimized for the MSI Cyborg 15 (GeForce RTX 3050) and introduces Hybrid Consensus vision to eliminate false-positive detections.

---

## Configuration

### Requirements

- ROS2 (Humble or later)
- GeForce RTX 3050 (for hardware-accelerated perception)
- MSI Cyborg 15 Integrated Webcam / RealSense D435
- `robot_interface` package built in the same workspace
- An Android phone with Wifi

### Installation

To install the app:

1. Open the provided `.apk` file
2. Install the app (don't scan)

To configure ROS2 package:

1. Copy the provided `src` directory inside `r2_src` into your workspace
2. Environment Setup: To prevent thermal spikes and "Undefined Symbol" errors, the following environment pins are required:

   - `torch==2.4.0`
   - `nvidia-cudnn-cu12==9.1.0.70`
   - `nvidia-cuda-runtime-cu12==12.1.105`
   - `numpy==1.26.4`

3. Build the package:

``` bash
python3 -m venv <venv>
source <venv>/bin/activate
pip install -r requirements.txt

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/.cv_env/lib/python3.10/site-packages/nvidia/cudnn/lib

cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Running

You can now use the provided launch file to start the core system, or run nodes individually for debugging.

### Option A: Launch File (Recommended)

This starts the communication, control, and navigation nodes simultaneously.

``` bash
ros2 launch target_setter target_setter.launch.py
```

#### Option B: Manual Execution

Run each node in a separate terminal. Ensure the GPU library path is exported in the perception terminal.

- Vision: `ros2 run perception object_detection_node`
- Control: `ros2 run control robot_control_node`
- Communication: `ros2 run communication udp_listener_node`
- Hardware: `ros2 run hardware_interface can_driver_node`

> Run all the nodes inside different terminal. The port is set to `5050` by default.
> Run the provided tuner.py script to calibrate HSV thresholds for the current lighting: `python3 tuner.py`.

## How to Operate

1. Add the field dimension first before adding waypoints.
2. Bind the phone to the robot before sending.
3. **Send waypoints** — tap the map to place waypoints, then press **Send**. The robot navigates to each one in order.
4. **Edit a waypoint** — drag a waypoint on the map. Updates are applied immediately, even while the robot is moving.
5. **Delete / undo** — use the app controls before the waypoints are executed.
6. **Return** — press **Return** on the app. The robot immediately heads back to the last visited waypoint.

## Features

- Add waypoints by touch on a global-frame map
- Edit waypoints in real time (mid-navigation)
- Delete / undo waypoints from the app
- Send all waypoints at once
- Return to previous waypoint
- P controller with speed saturation and velocity ramp-up
- Stateful control (IDLE / NAVIGATE / RETURN / PAUSED)
- Hybrid Consensus Vision: Uses the RTX 3050 to run AI inference, verified by HSV color logic to prevent "hallucinations" (e.g., chasing badges or background noise).
- GPU Acceleration: Fully offloads math to the CUDAExecutionProvider to maintain stable CPU temperatures.

## Toubleshooting

### Robot does not move after sending waypoints

- Check that the UDP listener is running and receiving packets.
- Verify `/waypoint` is being published: `ros2 topic echo /waypoint`
- Check that `/current_odom` is being published by your driver node.

### Robot moves in the wrong direction

- Confirm the odometry frame matches the app's global frame. A mismatch here will cause the robot to navigate to the wrong position.
- Check that the robot's initial pose at startup is (0, 0) or matches the app's origin.

### Yaw is way off

- Known issue. Check that the yaw from `/current_odom` is consistent with the direction the robot is physically facing.
- Verify the quaternion-to-yaw conversion matches your odometry convention.

### Robot overshoots or oscillates

- Reduce `K_P` in `robot_control.py`.
- Increase `A_MAX` gradually if the ramp-up is too slow and causing overshoot.

### Robot stops short of the waypoint

- The P controller has inherent steady-state error. Reduce `ERROR_THRESHOLD` or `ARRIVAL_THRESHOLD` to tighten accuracy.

### Waypoint edit applies to the wrong waypoint

- Known app-side bug. Restart the app and re-send waypoints as a workaround.

### Robot gets stuck in PAUSED and never resumes

- Check that `_pause_robot` is not being set externally without a corresponding `resume()` call.
- Verify the odometry topic is still publishing — the timer callback depends on fresh pose data.

### `custom_messages` not found at build

- Make sure the `custom_messages` package is inside your workspace and run `colcon build` again before sourcing.

### Node Aborts or "Undefined Symbol" error

- This indicates a library mismatch. Re-install the pinned versions: `pip install nvidia-cudnn-cu12==9.1.0.70`

### High CPU temperatures (80°C+)

- The system has likely fallen back to CPU inference. Ensure the perception node is set to `CUDAExecutionProvider`.

### Vision "Hallucinations" (False Positives)

- Your HSV thresholds are too wide. Tighten the `lower_blue` or `lower_red` values and reduce the morphological kernel to `5x5`.

## Known Issues

- **Yaw error** — heading is off
- **Residual position error** — P controller leaves steady-state error near the target.
- **Waypoint edit bug** — edits oapply to the wrong version of planning due to mistake on the app.
- **No emergency stop** — not yet implemented on the app.
