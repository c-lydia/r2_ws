# Changelog

All notable changes to this project are documented in this file.

---

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

---

### System Features

- Global-frame waypoint navigation system
- Manual node-based ROS 2 execution (no launch files)
- Basic odometry integration for robot pose tracking
- Speed saturation and ramp-up control in P-controller

---

### Known Issues

- Yaw drift due to yaw coupling on controller
- Steady-state error from P-only controller
- Occasional waypoint mismatch during fast edits
- No emergency stop system implemented yet
- No automated launch system (manual startup required)

---

### Notes

- APK and ROS2 stack must be version-matched manually
- System assumes consistent global frame alignment between app and robot