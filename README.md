# TS-ROS2 Robotics Platform

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

TS-ROS2 is a modular ROS2-based robotics system for waypoint navigation, perception, and manipulation.

It evolved from a single navigation stack into a layered robotics platform with multiple versioned system generations.

## System Versions

### v1.0 — Legacy Stable System

- Original UDP protocol (v1)
- Waypoint-based navigation system
- Basic P-controller robot control loop
- Monolithic ROS2 workspace structure
- Android app compatibility (v1 protocol)

> v1.0 is stable and frozen (no further feature development)

### v2.0 — Current Platform

- **TS-Link protocol v2.0**
- Android app v2.0
- ROS2 package set v2.0
- Modular ROS2 architecture redesign
- Added perception pipeline (CV system via Docker runtime)
- Added manipulation subsystem
- Expanded Android UI modules
- Launch file and installation updates
- Multi-layer system design:
  - Core navigation layer
  - Perception layer
  - Manipulation layer
  - Communication layer

> v2.0 is the current TS-ROS2 release line

## Compatibility

| Feature | v1 App | v2 App |
|--------|--------|----------|
| TS-Link v1.0 protocol | ✔ | ❌ |
| TS-Link v2.0 protocol | ❌ | ✔ |
| Navigation system | ✔ | ✔ |
| CV pipeline | ❌ | ✔ |
| Manipulation | ❌ | ✔ |

## System Overview

TS-ROS2 is structured as a layered robotics system:

### Core Layer

- Robot motion control
- Odometry processing
- Waypoint execution
- State machine (navigate / pause / return)

### Communication Layer

- UDP-based Android ↔ Robot interface
- ROS2 topic bridge
- Real-time command synchronization

### Perception Layer (v2)

- Camera input processing
- GPU inference (TensorRT / ONNX fallback)
- Docker-isolated CV runtime
- Shared-memory frame pipeline

### Manipulation Layer (v2)

- Gripper control logic
- Detection-based interaction
- Distance-aware decision system

## Communication Architecture

#### v1 (Legacy)

- Simple waypoint batch format
- Fixed schema
- Android app compatibility

#### TS-Link v2.0 (Current)

- Structured frame system
- Extended metadata support
- Not backward compatible with v1

## ROS2 Workspace Structure

``` bash
communication/
control/
navigation/
hardware_interface/
perception/      (v2)
manipulation/    (v2)
robot_interface/
target_setter/
```

Each module is independently testable and replaceable.

## Perception Runtime (v2)

- Docker-based CV execution environment
- GPU acceleration support (CUDA / TensorRT)
- ONNX fallback for portability
- Shared memory bridge with ROS2 inference nodes

## Design Philosophy

- Modular robotics architecture over monolithic design
- Clear separation of concerns:
  - control
  - perception
  - communication
- Optional subsystem design (CV / manipulation)
- Deterministic navigation core remains stable across versions

## Supported Hardware

- MSI Cyborg 15 (RTX 3050)
- NVIDIA CUDA-capable systems
- Jetson devices (experimental support)
- Standard ROS2-compatible Linux systems

## Project State

- v1.0 → legacy stable system (frozen)
- v2.0 → current robotics platform

**`custom_messages` not found at build**

- Make sure the `custom_messages` package is inside `~/ros2_ws/src` and run `colcon build` again before sourcing.

For technical insight, please read [CHANGELOG](CHANGELOG.md), [development_notes](docs/development_notes.md), [system_architecture](docs/system_architecture.md), and [TS-Link protocol](docs/ts_link_protocol/ts_link_v2.0.md)

## Known Issues

- **Yaw error** — heading is off
- **Residual position error** — P controller leaves steady-state error near the target.
- **Waypoint edit bug** — editsoapply to the wrong version of planning due to mistake on the app.
- **No emergency stop** — not yet implemented on the app.
- **No launch file** — nodes must be started manually.
