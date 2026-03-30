Overview
========

Purpose
-------

This documentation presents the stability analysis of the **Session 1** - the first system-level evaluation of the ``target_setter`` project. The goal is to characterize motor speed atbility and yaw behavior under two test conditions.

System under test
-----------------

- **Platform:** 4-wheel omnidirectional robot
- **Controller:** ``robot_control`` (ROS 2 node) take waypoints from Android app ``target_setter``
- **Sensors:** IMU (quaternion orientation), motor encoders (per-motor speed)
- **Communication:** CAN bus via ``can_driver``, UDP via ``udp_listener`` and ``udp_sender``
- **Odometry:** ``current_odometry`` node (fuses encoder + IMU)

Test conditions
---------------

.. list-table::
   :header-rows: 1
   :widths: 15 40 25

   * - Test
     - Description
     - Environment
   * - TEST1
     - Curve-path at higher speed
     - Assume planar, indoor environment
   * - TEST2
     - Lower speed with yaw commands
     - Assume planar, indoor environment

Data Collected
--------------
...existing code...

Session 1 Results
-----------------
- Controller is stable
- `NAVIGATE` and `IDLE` state transition works correctly
- Robot moved in curve path
- Yaw estimates from sensor is working correctly
- Position estimates from odometry is not working due to `can_id` conflicts
- Motor 4 hits saturation

Session 2 Overview
------------------
- Odometry samples: **495**
- Robot control commands: **323**
- Motor commands (total): **239**
- Waypoint batch updates: **2**
- Odometry duration: **57.70 s**
- Odometry rate: **8.6 Hz**
- Control command duration: **32.20 s**
- Control command rate: **10.0 Hz**

Session 2 Waypoint Batches
--------------------------
- **Version 2** @ t=1772875602.605: (idx=0, x=0.000, y=0.000)
- **Version 3** @ t=1772875611.606: (idx=0, x=0.463, y=1.661), (idx=1, x=0.895, y=2.097)

Session 2 Odometry Statistics
-----------------------------
- **x**: min=1.247  max=2.110  mean=1.500  std=0.291
- **y**: min=0.739  max=2.132  mean=1.553  std=0.363
- **yaw**: min=-0.657  max=1.499  mean=0.978  std=0.462
- **Total path length**: 3.381 m
- **Net displacement**: 0.671 m
- **Start**: (1.259, 1.020)
- **End**:   (1.869, 0.740)
- **Yaw range**: 2.156 rad (123.5°)

Session 2 Velocity Command Statistics
-------------------------------------
- **Vx**: min=-0.3180  max=-0.0020  mean=-0.0967  std=0.0775
- **Vy**: min=0.0870  max=0.2620  mean=0.1715  std=0.0414
- **Wz**: min=0.3160  max=0.5000  mean=0.4028  std=0.0466

Session 2 State Machine Transitions
-----------------------------------
- **NAVIGATE**: 323 samples
- State transitions detected: **0**
  - Per-motor speed vectors (4 components each)
  - Odometry publishes: velocity (vx, vy) and orientation quaternion
  - ``MotorCommand`` publishes with ``can_id`` and ``goal``
- Raw log file: ``test_data/data_session_1.txt``

Signals Analyzed
----------------

1. **Overall speed:** mean of per-motor speed magnitudes at each timestamp
2. **Yaw rate (wz):** derivative of unwrapped yaw angle from quaternion 
3. **Per-motor speed:** individual motor magnitude tracks for symmetry checks

Document Structure
------------------
.. list-table::
   :widths: 25 50

   * - :doc:`motor_speed`
     - Per-motor speed traces, inter-motor symmetry
   * - :doc:`overall_speed`
     - Aggregated speed stability (rolling mean ± std)
   * - :doc:`yaw_analysis`
     - Yaw rate stability, command-response overlay
   * - :doc:`comparison`
     - TEST1 vs TEST2 side-by-side
   * - :doc:`conclusion`
     - Summary of findings, issues observed, and next steps
