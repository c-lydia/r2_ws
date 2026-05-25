# Changelog

All notable changes to this project are documented in this file.

## [v2.0] - 2026-05-25

### Added

- System architecture documentation updated ([docs/system_architecture.md](docs/system_architecture.md)) for v2.0.
- Launch file `target_setter.launch.py` to start core nodes together.
- Shared Memory IPC for zero-copy camera → inference frame exchange.
- Dual-backend inference: TensorRT `.engine` priority with ONNX Runtime fallback.
- Hybrid consensus vision: AI inference verified by HSV color logic to reduce false positives.
- `export_model.py` automation for Roboflow → ONNX export.
- `robot_interface/msg/estop.msg` documented for emergency stop signaling.
- Localization support added for UI and messages.
- Fault handlers added to `mission_planner` to improve robustness.
- Unit tests added for critical modules (communication and planner).

### Changed

- Optimized perception pipeline for NVIDIA RTX 3050 (CUDA/cuDNN pinned versions).
- README and installation instructions updated for v2.0.
- System architecture and TS-Link protocol documentation reviewed and aligned with the v2.0 release.
- Added Jetson-specific setup notes and optional requirements file.
- Updated gripper decision logic in the manipulation stack.
- `mission_planner` behavior updated (task sequencing and retries).
- Navigation updates and refinements.
- Communication package updates and contract refinements.
- System contracts updated.

### Fixed

- Minor refactors to reduce inference latency and stabilize topic publishing.
- Documentation inconsistencies from v1.0 corrected.
- Fixed communication bugs and debugged message flow.
- Fixed small typos and documentation issues.

## [v1.0] - 2026-04-30

### Added

- Android application for waypoint-based robot control
- UDP communication system (10 Hz waypoint streaming)
- ROS 2 navigation node with P-controller implementation
- Stateful robot controller (IDLE / NAVIGATE / RETURN / PAUSED)
- Touch-based map interface for waypoint placement
- Real-time waypoint editing (drag to update positions)
- Waypoint deletion and undo functionality
- Return-to-previous-waypoint feature

### System Features

- Global-frame waypoint navigation system
- Manual node-based ROS 2 execution (no launch files)
- Basic odometry integration for robot pose tracking
- Speed saturation and ramp-up control in P-controller

### Known Issues

- Yaw drift due to yaw coupling on controller
- Steady-state error from P-only controller
- Occasional waypoint mismatch during fast edits
- No emergency stop system implemented yet
- No automated launch system (manual startup required)

### Notes

- APK and ROS2 stack must be version-matched manually
- System assumes consistent global frame alignment between app and robot
