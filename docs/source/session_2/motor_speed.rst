Motor Speed & Position Feedback
===============================

Objective
---------

Evaluate the motor-level feedback reported via the CAN bus (CAN IDs 102,
103, 104) to determine whether the motors are executing the commanded
goals and providing useful closed-loop information.

Method
------

Each ``EncoderFeedback`` message contains two arrays:

* **Speed** — a four-element array expected to carry motor velocity.
* **Position** — a four-element array carrying absolute encoder readings.

Feedback arrives at approximately **17 Hz** per CAN ID
(combined rate ~50 Hz across three IDs).

Motor Speed Feedback
--------------------

All motor speed feedback arrays are ``[0.0, 0.0, 0.0, 0.0]`` for **every**
sample in both tests — 98 samples in TEST 1, 110 in TEST 2.

TEST 1
~~~~~~

.. figure:: ../../img/motor_speed/motor_speed_fb_TEST1.png
   :width: 100%
   :align: center

   Motor speed feedback — TEST 1 (all zero).

TEST 2
~~~~~~

.. figure:: ../../img/motor_speed/motor_speed_fb_TEST2.png
   :width: 100%
   :align: center

   Motor speed feedback — TEST 2 (all zero).

.. warning::

   The motor speed feedback channel carries **no useful information** in
   Session 2.  The velocity control loop is effectively **open-loop** — the
   controller has no knowledge of actual motor speed.  This is the single
   most critical issue identified in this session.

Impact on Downstream Nodes
~~~~~~~~~~~~~~~~~~~~~~~~~~

Because the ``current_odometry`` node computes the robot's velocity by fusing
motor speed feedback, the published odometry velocity is always
:math:`(0.0,\,0.0)`.  Any controller that reads odometry velocity (e.g. for
damping or integral action) receives zero, which can lead to integral windup
or unbounded output.

Motor Position Feedback
-----------------------

Unlike speed, the motor **position** array contains non-zero values that
change between discrete levels.  Position indices 1, 2, and 3 carry non-zero
values; index 0 is always 0.0.

TEST 1
~~~~~~

.. figure:: ../../img/motor_speed/motor_position_fb_TEST1.png
   :width: 100%
   :align: center

   Motor position feedback — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/motor_speed/motor_position_fb_TEST2.png
   :width: 100%
   :align: center

   Motor position feedback — TEST 2.

.. list-table:: Motor position summary
   :header-rows: 1
   :widths: 20 35 35

   * - Index
     - TEST 1 values
     - TEST 2 values
   * - position[0]
     - Always 0.0
     - Always 0.0
   * - position[1]
     - 42.88°
     - 134.12°
   * - position[2]
     - 5.59°, 151.92°
     - 5.53°, 124.49°
   * - position[3]
   - -16.74°
   - -16.53°

**Interpretation:**  The position values jump between a small number of
discrete levels rather than varying continuously.  This indicates either that
the motor controllers report **absolute encoder positions** that update
infrequently, or that the CAN driver only captures position when a level
crossing occurs.  The different baseline values between TEST 1 and TEST 2
show that position registers have accumulated between runs (the robot was
physically repositioned or the encoders drifted).

.. note::

   Position range within each test is **0.0** — the values are constant for
   the duration of each run.  See :doc:`transient_response` for the
   goal-vs-position comparison.

Key Findings
------------

1. **Zero speed feedback** across all motors and both tests confirms a
   hardware or firmware issue in the motor controllers' speed reporting.
2. **Non-zero but static position** suggests the encoders are physically
   present but their rate-of-change (speed) computation is not being
   transmitted.
3. **CAN 101 (motor 1) is absent** — this motor has no feedback channel at
   all, compounding the open-loop problem.
4. **Downstream odometry is invalidated** — ``current_odometry`` velocity is
   always zero because it depends on the missing speed feedback.

.. seealso::

   :doc:`motor_cmd` — The commands these motors were supposed to execute.

   :doc:`transient_response` — Direct comparison of goal vs position feedback.

   :doc:`conclusion` — Root-cause analysis and recommendations.
