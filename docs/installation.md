# Installation & Operation — Target Setter (v2.0)

This page contains installation steps, environment pins, camera setup, and how to run the system.

## Overview

A semi-autonomous waypoint navigation system with optional GPU-accelerated perception. Use `quickstart.md` for a minimal setup; this page expands on environment pins and practical installation notes.

## Requirements

- ROS2 (Humble or later)
- Python 3.10+
- Optional: NVIDIA CUDA 12.* and cuDNN 9.* for GPU inference
- GeForce RTX 3050 (recommended for performance)
- Camera (USB or RealSense) or `/dev/video*` available
- `robot_interface` package built in the same workspace
- An Android phone with Wi‑Fi

## Jetson AGX Xavier (optional)

- JetPack 5.1.2 (L4T R35.4.1)
- ROS2 Foxy
- Python 3.8
- CUDA 11.4 (managed by JetPack)

## Installation Steps

1. Copy the `src/` tree into your ROS2 workspace root (e.g. `~/ros2_ws/src`).
2. Create and activate a virtual environment inside the repo:

       python3 -m venv .cv_env
       source .cv_env/bin/activate

3. Install Python dependencies:

       pip install -r requirements_common.txt
       pip install -r requirements.txt

   For Jetson boards, use `requirements_jetson.txt` instead of `requirements.txt`.

4. Critical pinned packages (recommended to avoid runtime/symbol errors):

   - `torch==2.4.0`
   - `nvidia-cudnn-cu12==9.1.0.70`
   - `nvidia-cuda-runtime-cu12==12.1.105`
   - `numpy==1.26.4` or `numpy==1.23.5`

5. (Optional) Export Roboflow model to ONNX:

       python3 export_model.py

   Set `MODEL_PATH` to the exported `.onnx` or TensorRT `.engine` file before running perception.

6. Build workspace:

       cd ~/ros2_ws
       colcon build --symlink-install
       source install/setup.bash

## Camera Setup (usb_cam)

1. Install driver:

       sudo apt install ros-humble-usb-cam

2. Grant device access:

       sudo usermod -a -G video $USER

   Log out and back in to apply group membership.

3. Verify camera:

       ls -la /dev/video*
       v4l2-ctl --list-devices

4. Test with OpenCV:

       python3 -c "import cv2; cap = cv2.VideoCapture('/dev/video0'); print('Camera OK' if cap.isOpened() else 'Camera failed')"

5. Launch usb_cam node:

       ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video0 -p image_width:=640 -p image_height:=480

## Running the System

### Recommended (single launch)

    ros2 launch target_setter target_setter.launch.py

### Manual (node-by-node for debugging)

    # camera
    ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video0

    # perception (set MODEL_PATH if required)
    export MODEL_PATH=/path/to/model.onnx
    ros2 run perception object_detection

    # control
    ros2 run control robot_control_node

    # communication
    ros2 run communication udp_listener_node

## How to Operate

1. Add the field dimension before adding waypoints.
2. Bind the phone to the robot before sending waypoints.
3. Place waypoints on the map and press **Send**.
4. Edit waypoints by dragging; changes apply immediately.
5. Use **Return** to send the robot back to the last visited waypoint.

## Notes

- Default UDP port: `5050`.
- Use `tuner.py` to calibrate HSV thresholds: `python3 tuner.py`.
- If GPU provider fails, install pinned cuDNN runtime: `pip install nvidia-cudnn-cu12==9.1.0.70` and set `LD_LIBRARY_PATH`.
