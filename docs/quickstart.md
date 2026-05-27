# Quickstart — TS-ROS2 (v2.0)

This page provides minimal steps to get a development environment running quickly. These instructions assume a Debian/Ubuntu-based system and an active Python virtual environment.

## Prerequisites

- ROS2 Humble or later installed
- Python 3.10+
- Optional: NVIDIA CUDA 12.* and cuDNN 9.* for GPU inference
- Camera (USB or RealSense) or `/dev/video*` available

## Environment (recommended)

``` bash
# create and activate a virtualenv inside the repo
python3 -m venv .cv_env
source .cv_env/bin/activate

# install Python dependencies
pip install -r requirements_common.txt
pip install -r requirements.txt
```

If you are on Jetson, use `requirements_jetson.txt` instead of `requirements.txt`.

## Build the ROS2 workspace

``` bash
# from your ROS2 workspace root
colcon build --symlink-install
source install/setup.bash
```

## Launch core system (recommended)

``` bash
ros2 launch target_setter target_setter.launch.py
```

## Run nodes manually (debugging)

``` bash
# camera
ros2 run usb_cam usb_cam_node_exe --ros-args -p video_device:=/dev/video0 -p image_width:=640 -p image_height:=480

# perception (set MODEL_PATH if required)
export MODEL_PATH=/path/to/model.onnx
ros2 run perception object_detection

# control
ros2 run control robot_control_node

# communication
ros2 run communication udp_listener_node
```

## Camera test

``` bash
# verify camera topic
ros2 topic list | grep image
ros2 topic hz /camera/color/image_raw
```

## Notes

- If GPU provider fails, install pinned cuDNN runtime: `pip install nvidia-cudnn-cu12==9.1.0.70` and set `LD_LIBRARY_PATH` accordingly.
- Use `tuner.py` to calibrate HSV thresholds for your environment.
