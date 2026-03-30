Introduction
============

Overview
--------

Session 2 continues the motor-mapping and navigation testing of the
four-wheeled omnidirectional (Mecanum) robot.  Two independent test runs
(TEST 1 and TEST 2) were captured to evaluate:

* Motor command-to-feedback mapping via the CAN bus
* Controller velocity command behaviour (:math:`V_x`, :math:`V_y`, :math:`\omega_z`)
* Position and heading evolution (UDP odometry)
* Waypoint-based navigation performance
* System timing and inter-message jitter

.. note::

   This report follows the same analytical structure as the Session 1
   documentation, with additional sections on **navigation**, **timing**,
   and **state-machine** behaviour specific to Session 2.

System Architecture
-------------------

The control pipeline consists of five ROS 2 nodes executing in sequence:

.. list-table:: ROS 2 Node Pipeline
   :header-rows: 1
   :widths: 25 15 35

   * - Node
     - Rate (Hz)
     - Description
   * - ``robot_control_node``
     - 10
     - Publishes :math:`(V_x,\,V_y,\,\omega_z)` velocity commands
   * - ``inverse_kinematic``
     - 40
     - Converts velocity to per-motor goals on CAN 1–4
   * - ``current_odometry``
     - 170
     - Reads encoder feedback from CAN 102–104; fuses odometry
   * - ``udp_sender``
     - 10
     - Relays position / yaw summaries via UDP
   * - ``udp_listener``
     - async
     - Receives waypoint batches from the base station

The inverse-kinematic transform for a Mecanum drive is:

.. math::

   \begin{bmatrix} \omega_1 \\ \omega_2 \\ \omega_3 \\ \omega_4 \end{bmatrix}
   = \frac{1}{r}
   \begin{bmatrix}
     1 & -1 & -(l_x+l_y) \\
     1 &  1 &  (l_x+l_y) \\
     1 &  1 & -(l_x+l_y) \\
     1 & -1 &  (l_x+l_y)
   \end{bmatrix}
   \begin{bmatrix} V_x \\ V_y \\ \omega_z \end{bmatrix}

where :math:`r` is the wheel radius and :math:`l_x + l_y` is the half-track
sum.

Data Inventory
--------------

.. list-table:: Signal counts by test
   :header-rows: 1
   :widths: 35 15 15

   * - Signal
     - TEST 1
     - TEST 2
   * - Motor speed / position feedback (CAN 102–104)
     - 98
     - 110
   * - Odometry publishes (``current_odometry``)
     - 127
     - 126
   * - Motor commands (``kinematic_publisher``, CAN 1–4)
     - 239
     - 247
   * - UDP odom (``udp_sender``)
     - 495
     - 495
   * - Controller commands (``robot_control_node``)
     - 323
     - 330
   * - Waypoint batches (``udp_listener``)
     - 3
     - 0

CAN ID Mapping
--------------

.. list-table:: Command → Feedback CAN mapping
   :header-rows: 1
   :widths: 25 25 25

   * - Command CAN ID
     - Feedback CAN ID
     - Status
   * - 1
     - (101)
     - **Missing** — no CAN 101 feedback observed
   * - 2
     - 102
     - ✓ Present
   * - 3
     - 103
     - ✓ Present
   * - 4
     - 104
     - ✓ Present

.. warning::

   CAN 101 feedback is absent in Session 2.  Motor 1 commands are sent on
   CAN 1 but **never acknowledged**, leaving motor 1 completely unmonitored.
   This issue was also present in Session 1 and remains unresolved.

Key Findings Summary
--------------------

1. **Motor speed feedback is always zero** — the speed array
   ``[0, 0, 0, 0]`` is reported for every sample, making the control loop
   effectively open-loop with respect to motor velocity.
2. **Motor position feedback** is non-zero but jumps between a small set of
   discrete levels, suggesting absolute encoder positions that update
   infrequently.
3. **Odometry velocity** from ``current_odometry`` is ``(0.0, 0.0)`` because
   it depends on the zero speed feedback.
4. **Controller commands** (:math:`V_x`, :math:`V_y`, :math:`\omega_z`) are
   non-zero and serve as the **primary source** of kinematic intent.
5. **UDP odom** (:math:`x`, :math:`y`, :math:`\psi`) is non-zero and changes,
   providing the best measure of actual robot state.

Test Methodology
----------------

Each test follows the same protocol:

1. ``robot_control_node`` publishes :math:`(V_x,\,V_y,\,\omega_z)` commands
   at ~10 Hz.
2. ``inverse_kinematic`` converts the commands to per-motor goals and sends
   ``MotorCommand`` messages on CAN 1–4 at ~40 Hz.
3. ``current_odometry`` reads motor feedback from CAN 102–104 and publishes
   fused odometry at ~170 Hz.
4. ``udp_sender`` relays position / yaw summaries at ~10 Hz.
5. ``udp_listener`` receives waypoint batches from the base station.

The raw log file ``data_session_2.txt`` contains 5 483 lines and is split at
line 2 755 between TEST 1 and TEST 2.

.. seealso::

   :doc:`motor_cmd` — Motor-level command goals from the kinematic solver.

   :doc:`velocity_components` — Controller velocity command analysis.

   :doc:`conclusion` — Consolidated findings and recommendations.
