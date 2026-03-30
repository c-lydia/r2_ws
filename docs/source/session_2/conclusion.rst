Conclusion
==========

Session 2 reveals a **critical motor execution failure** that prevents the
robot from performing its intended navigation task.  All layers above the
motor driver — the controller, inverse kinematics, state machine, and
navigation planner — function correctly and produce reasonable commands.

Key Findings
------------

1. **Motor speed feedback is zero.**  All four motors report
   ``speed = [0, 0, 0, 0]`` throughout both tests, and encoder position
   feedback is stuck at constant values.  CAN 101 (Motor 1) feedback is
   entirely absent.  See :doc:`motor_speed`.

2. **Controller commands are healthy.**  :math:`V_x` ranges from −0.318 to
   −0.002 m/s, :math:`V_y` from −0.001 to 0.262 m/s, and
   :math:`\omega_z` from 0.316 to 0.500 rad/s.  These are smooth, continuous
   signals with very low jitter (< 1 ms at 10 Hz).  See
   :doc:`velocity_components`.

3. **Motor command goals are sent but not executed.**  The inverse-kinematic
   node translates controller outputs into per-motor goals (range −9.68 to
   +2.61 motor units), but the motors do not respond.  See
   :doc:`motor_cmd` and :doc:`transient_response`.

4. **Actual motion is minimal.**  The robot drifts ~1.5 m (vs expected
   9–18 m) and yaw changes 0.6–0.85 rad (vs expected 15+ rad).  See
   :doc:`navigation_analysis`.

5. **State machine is stuck in NAVIGATE.**  No waypoint arrival, no state
   transitions — the distance-to-target condition is never satisfied.  See
   :doc:`state_machine_analysis`.

6. **Timing is deterministic** for controller (10 Hz, σ < 1 ms) and motor
   command (40 Hz) streams.  UDP odom has one 6.8 s dropout in TEST 1.  See
   :doc:`timing_analysis`.

7. **System-level plant gain ≈ 12.5 %** (from Wiener deconvolution of
   :math:`\omega_z \to \dot{\psi}`), confirming severe attenuation between
   command and response.  See :doc:`impulse_response`.

Root-Cause Hypothesis
---------------------

The most likely cause is a **CAN bus communication failure** between the
ROS motor-command publisher and the physical motor controllers.  The
``MotorCommand`` messages are successfully published to the ROS graph, but
the downstream CAN interface (or the motor controllers themselves) does not
execute them.

Possible sub-causes, ordered by likelihood:

.. list-table::
   :header-rows: 1
   :widths: 5 35 30

   * - #
     - Hypothesis
     - Diagnostic
   * - 1
     - Motor controller not in operational mode (safety-stop / config mode)
     - Check controller status registers
   * - 2
     - CAN bus wiring fault or missing termination resistor
     - Measure bus voltage, check ACK bits
   * - 3
     - Motor driver enable signal not asserted
     - Verify enable GPIO / relay state
   * - 4
     - CAN ID mismatch between software and hardware
     - Cross-reference firmware ID table
   * - 5
     - CAN driver not forwarding ROS messages to physical bus
     - Log ``can_driver`` output, use candump

Recommendations
---------------

.. list-table::
   :header-rows: 1
   :widths: 5 50 15

   * - #
     - Action
     - Priority
   * - 1
     - **Verify CAN bus hardware** — check wiring, termination resistors,
       and bus voltage levels with an oscilloscope.
     - Critical
   * - 2
     - **Confirm motor controller mode** — ensure each controller is in
       operational (run) mode, not safety-stop or configuration mode.
     - Critical
   * - 3
     - **Validate with single-motor test** — send a constant speed command
       to one motor in isolation and confirm physical rotation before running
       full navigation.
     - Critical
   * - 4
     - **Check CAN ID assignment** — verify that hardware motors 1–4 match
       software CAN IDs 1–4, especially for the missing CAN 101.
     - High
   * - 5
     - **Add motor-level diagnostics** — log the driver's internal state
       (enable bit, fault codes) alongside speed/position feedback.
     - High
   * - 6
     - **Reduce odom_pub rate** — the 170 Hz zero-velocity publish is
       wasted bandwidth; reduce to 10 Hz or suppress when stale.
     - Medium
   * - 7
     - **Investigate UDP dropout** — the 6.8 s gap in TEST 1 UDP odom could
       mask real navigation errors once motors are working.
     - Medium

Comparison with Session 1
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 30 30 30

   * - Metric
     - Session 1
     - Session 2
   * - Motor speed feedback
     - Non-zero, tracks goals
     - Always zero
   * - Encoder position
     - Changes over time
     - Constant per motor
   * - Actual displacement
     - Matches commands
     - ~10–20 % of expected
   * - State transitions
     - Multiple (IDLE → NAV → ROTATE)
     - None (NAVIGATE only)
   * - Controller commands
     - Healthy
     - Healthy (similar range)
   * - Timing jitter
     - Low
     - Low (except UDP outlier)
   * - Plant gain (:math:`\omega_z \to \dot{\psi}`)
     - ~1.0 (not measured)
     - ~0.125 (−18 dB)

Session 2 confirms that the **software stack is fully functional** — the
controller, inverse kinematics, state machine, and navigation planner all
operate correctly.  The issue is **entirely in the motor/CAN execution
layer**.  Resolving the CAN communication fault before Session 3 is the
single most important action item.

.. seealso::

   Raw data file: ``test_data/data_session_2.txt``

   Plot generation script: ``src/plot_session_2.py``

   Session 1 report: ``../../test_session_1/docs/``
