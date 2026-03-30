Transient Response
==================

Objective
---------

Evaluate the motor-level transient dynamics by comparing motor **command
goals** against the corresponding **position feedback** over time.  In a
healthy system, position should track goals with a characteristic rise time
and settling behaviour.

Method
------

Each motor receives a goal via ``MotorCommand`` (CAN 1–4) at ~40 Hz.  The
corresponding encoder position arrives via ``EncoderFeedback`` (CAN 102–104)
at ~17 Hz.  Speed feedback is not available in Session 2 (all zeros — see
:doc:`motor_speed`), so encoder **position** is the only measurable
motor-level response.

For each motor, two time series are plotted on a shared time axis:

* **Goal** (top panel) — the commanded motor speed/position.
* **Position feedback** (bottom panel) — the encoder-reported position.

.. note::

   Motor 1 (CAN 1 / CAN 101) is excluded because CAN 101 feedback is
   absent from the log.

Motor-Level Transient (Goal vs Position Feedback)
--------------------------------------------------

CAN 2 (Motor 2)
~~~~~~~~~~~~~~~~

.. figure:: ../../img/transient/transient_can2_TEST1.png
   :width: 100%
   :align: center

   Motor 2: goal (top) vs position feedback (bottom) — TEST 1.

.. figure:: ../../img/transient/transient_can2_TEST2.png
   :width: 100%
   :align: center

   Motor 2: goal vs position feedback — TEST 2.

CAN 3 (Motor 3)
~~~~~~~~~~~~~~~~

.. figure:: ../../img/transient/transient_can3_TEST1.png
   :width: 100%
   :align: center

   Motor 3: goal vs position — TEST 1.

.. figure:: ../../img/transient/transient_can3_TEST2.png
   :width: 100%
   :align: center

   Motor 3: goal vs position — TEST 2.

CAN 4 (Motor 4)
~~~~~~~~~~~~~~~~

.. figure:: ../../img/transient/transient_can4_TEST1.png
   :width: 100%
   :align: center

   Motor 4: goal vs position — TEST 1.

.. figure:: ../../img/transient/transient_can4_TEST2.png
   :width: 100%
   :align: center

   Motor 4: goal vs position — TEST 2.

Transient Metrics
-----------------

.. list-table:: Transient Metrics
   :header-rows: 1
   :widths: 12 8 15 15 15 15

   * - Test
     - CAN
     - Goal Range
     - Pos Mean
     - Pos Range
     - Pos Std
   * - TEST 1
     - 2
     - variable
     - constant
     - 0.0
     - 0.0
   * - TEST 1
     - 3
     - variable
     - constant
     - 0.0
     - 0.0
   * - TEST 1
     - 4
     - variable
     - constant
     - 0.0
     - 0.0
   * - TEST 2
     - 2
     - variable
     - constant
     - 0.0
     - 0.0
   * - TEST 2
     - 3
     - variable
     - constant
     - 0.0
     - 0.0
   * - TEST 2
     - 4
     - variable
     - constant
     - 0.0
     - 0.0

.. warning::

   Position range = 0.0 means the position feedback is **constant** (stuck
   at a single value) across the entire test.  This confirms the motors were
   **not rotating** despite receiving non-zero goal commands continuously.

Interpretation
--------------

The transient plots reveal a complete disconnect between input and output:

* **Goals** vary continuously over time (range ≈ −9.68 to +2.61 motor units),
  reflecting the inverse-kinematic controller's attempts to drive each motor.
* **Position feedback** is flat — each motor's encoder reports a single
  constant value (e.g., 42.88°, 134.12°) throughout both tests.

In a functioning system, the position would show:

.. math::

   \theta(t) = \int_0^t g(\tau)\, d\tau + \theta_0

where :math:`g(\tau)` is the goal (speed command) and :math:`\theta_0` is the
initial position.  The expected position change for a goal of −9.62 over 30 s
would be :math:`\approx 289` motor units — yet the actual change is **zero**.

This confirms either:

1. The motors did not move (hardware/power/driver issue), or
2. The encoder feedback pipeline was frozen (firmware/CAN issue).

Either way, the motor control loop is effectively **open-loop** and the
controller output is purely **feed-forward**.

Key Findings
------------

1. **Zero position change** across all three monitored motors (CAN 2, 3, 4)
   in both tests — the motors are not executing commands.
2. **Goal signals are well-formed** — the inverse kinematic node is producing
   valid, time-varying motor commands.
3. **The disconnect is at the motor execution layer**, not the command
   generation layer.
4. Motor 1 (CAN 1) has no feedback at all, so its status is unknown.

.. seealso::

   :doc:`motor_speed` — Speed feedback (also zero) and position values.

   :doc:`motor_cmd` — The command goals being sent to these motors.

   :doc:`impulse_response` — System-level transfer function estimation.
