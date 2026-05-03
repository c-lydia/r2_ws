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

This version (v2.0) is optimized for the MSI Cyborg 15 (GeForce RTX 3050) and introduces:

- **Shared Memory IPC**: Zero-copy frame exchange between ROS2 and GPU inference engine
- **Dual-backend Inference**: Priority to TensorRT `.engine` files with ONNX Runtime fallback
- **Hybrid Consensus Vision**: AI inference verified by HSV color logic to eliminate false-positive detections
- **Model Export**: Automated Roboflow model export to ONNX format via `export_model.py`

## Configuration

### Requirements

- ROS2 (Humble or later)
- GeForce RTX 3050 (for hardware-accelerated perception  performance test)
- MSI Cyborg 15 Integrated Webcam / RealSense D435 / generic USB camera (performance test)
- `robot_interface` package built in the same workspace
- An Android phone with Wifi
- **Camera driver**: `usb_cam` ROS2 package (installed via `apt install ros-humble-usb-cam` or from source)
- CUDA Toolkit 12.* and cuDNN 9.* for GPU acceleration
- Optional: TensorRT 8.* for optimized inference (automatic fallback to ONNX Runtime)

### Jetson AGX Xavier Setup

- JetPack 5.1.2 (L4T R35.4.1)
- ROS2 Foxy
- Python 3.8
- CUDA 11.4 (managed by JetPack)

### Installation

To install the app:

1. Open the provided `.apk` file
2. Install the app (don't scan)

To configure ROS2 package:

1. Copy the provided `src` directory into your workspace
2. Install base dependencies from requirements files:

   ``` bash
   pip install -r requirements_common.txt  # Common dependencies
   pip install -r requirements.txt          # Host (ROS2) environment
   ```

   **Optional**: For Jetson boards, use `requirements_jetson.txt` instead.

3. **Critical environment pins** (to prevent thermal spikes and "Undefined Symbol" errors):

   - `torch==2.4.0`
   - `nvidia-cudnn-cu12==9.1.0.70`
   - `nvidia-cuda-runtime-cu12==12.1.105`
   - `numpy==1.26.4` or `numpy==1.23.5`

4. (**Optional**) Export your Roboflow model to ONNX format:

   ``` bash
   python3 export_model.py  # Requires inference-sdk
   ```

   Set `MODEL_PATH` environment variable to your exported model before running inference.

5. Build the package:

``` bash
python3 -m venv <venv>
source <venv>/bin/activate
pip install -r requirements.txt

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/.cv_env/lib/python3.10/site-packages/nvidia/cudnn/lib

cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

### Camera Setup (usb_cam)

If using a USB camera:

``` bash
# Install the usb_cam driver
sudo apt install ros-humble-usb-cam

# Grant video device permissions
sudo usermod -a -G video $USER
# Log out and back in for permissions to take effect

# Test camera availability
ls -la /dev/video*
v4l2-ctl --list-devices

# Check camera can be opened with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture('/dev/video0'); print('Camera OK' if cap.isOpened() else 'Camera failed')"
```

Then launch usb_cam node:

``` bash
ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video0 -p image_width:=640 -p image_height:=480
```

### Running

You can now use the provided launch file to start the core system, or run nodes individually for debugging.

#### Option A: Launch File (Recommended)

This starts the communication, control, and navigation nodes simultaneously.

``` bash
ros2 launch target_setter target_setter.launch.py
```

#### Option B: Manual Execution

Run each node in a separate terminal. Ensure the GPU library path is exported.

1. Start the camera driver (in terminal 1):

   ``` bash
   ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video0
   ```

2. Start vision inference (in terminal 2):

   ``` bash
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/.cv_env/lib/python3.10/site-packages/nvidia/cudnn/lib
   export MODEL_PATH=/workspace/models/yolov8n.onnx  # Optional: set your model path
   ros2 run perception object_detection_node
   ```

3. Start other nodes (in separate terminals):
   - Control: `ros2 run control robot_control_node`
   - Communication: `ros2 run communication udp_listener_node`
   - Hardware: `ros2 run hardware_interface can_driver_node`

> The port is set to `5050` by default.
> Run the provided `tuner.py` script to calibrate HSV thresholds for the current lighting: `python3 tuner.py`.

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
- **Shared Memory IPC**: Zero-copy frame exchange between ROS2 and inference engine
- **Dual-backend Inference**: Automatic fallback from TensorRT to ONNX Runtime
- **Hybrid Consensus Vision**: Uses the RTX 3050 to run AI inference, verified by HSV color logic to prevent "hallucinations" (e.g., chasing badges or background noise).
- **GPU Acceleration**: Fully offloads inference to CUDAExecutionProvider to maintain stable CPU temperatures
- **Model Export**: Built-in `export_model.py` to convert Roboflow models to ONNX format

## Testing Notes

### Camera Testing

When testing with `usb_cam` package, verify:

```bash
# Check camera is publishing
ros2 topic list | grep image
ros2 topic hz /image_raw  # Should be ~30 Hz

# View camera feed
ros2 run image_view image_view_node --ros-args --remap image:=/image_raw
```

### Inference Warnings (Non-Fatal)

The following warnings during startup are expected and can be safely ignored when using the base YOLO model:

``` txt
ModelDependencyMissing: Your `inference` configuration does not support SAM model.
ModelDependencyMissing: Your `inference` configuration does not support SAM3 model.
ModelDependencyMissing: Your `inference` configuration does not support Gaze Detection model.
ModelDependencyMissing: Your `inference` configuration does not support YoloWorld model.
DeprecationWarning: DepthProImageProcessorFast is deprecated.
FutureWarning: Importing from timm.models.layers is deprecated.
```

These are suppressed by default. To use these advanced models:

```bash
# Install optional inference backends
pip install 'inference[sam]'         # Segment Anything Model
pip install 'inference[gaze]'        # Gaze detection
pip install 'inference[yolo-world]'  # YoloWorld model

# Then enable them
export CORE_MODEL_SAM_ENABLED=True
export CORE_MODEL_GAZE_ENABLED=True
export CORE_MODEL_YOLO_WORLD_ENABLED=True
```

## Troubleshooting

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

### CUDA Provider / GPU Errors

If you see errors like `libcufft.so.11: cannot open shared object file` or `Failed to create CUDAExecutionProvider`:

- Ensure CUDA Toolkit 12.* is installed: `apt-get install cuda-toolkit-12-1`
- Ensure cuDNN 9.* is installed: `pip install nvidia-cudnn-cu12==9.1.0.70`
- Set the GPU library path before running: `export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/.cv_env/lib/python3.10/site-packages/nvidia/cudnn/lib`
- If the error persists, fall back to CPU inference by setting `CORE_MODEL_*_ENABLED` environment variables to `False` (this will be slower).

### Camera Driver Issues (usb_cam)

If `usb_cam` node fails to start:

- Verify camera is connected: `ls -la /dev/video*`
- Check camera is recognized: `v4l2-ctl --list-devices`
- Grant video permissions: `sudo usermod -a -G video $USER` (then log out and back in)
- Try a different video device (e.g., `/dev/video1` instead of `/dev/video0`)
- Test with `ffmpeg`: `ffmpeg -f v4l2 -i /dev/video0 -frames 1 test.jpg`
- If using RealSense D435, ensure `librealsense2` is installed instead of generic `usb_cam`

### Inference Engine Issues

- If inference fails to start, check `MODEL_PATH` is set and exists:
  
  ``` bash
  echo $MODEL_PATH
  ls -la $MODEL_PATH  # Should show .onnx or .engine file
  ```

- If TensorRT fails, it will automatically fall back to ONNX Runtime (slower but functional)
- To force CPU-only inference (debugging): `export FORCE_CPU=1`
- Check inference is producing detections: `ros2 topic echo /detections | head -20`

## Known Issues

- **Yaw error** — heading is off
- **Residual position error** — P controller leaves steady-state error near the target
- **Waypoint edit bug** — edits apply to the wrong version of planning due to mistake on the app
- **No emergency stop** — not yet implemented on the app
- **Stale detections warning** — If inference lags >50ms, detections are dropped (tune `STALENESS_MS` in `shm_bridge.py` if needed)
