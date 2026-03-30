State Machine Analysis
======================

Objective
---------

Examine the high-level state machine in ``robot_control`` to determine
whether it is transitioning correctly between navigation phases (e.g.
IDLE → NAVIGATE → ROTATE → IDLE).

Method
------

The ``robot_control_node`` logs its current state alongside each velocity
command.  The state string is extracted from every log line and plotted as a
timeline.  In Session 1, several states were observed (IDLE, NAVIGATE, ROTATE,
etc.), producing clear transition events.

Observed States
---------------

Session 2 is fundamentally different: only a **single state** was active
throughout the entire dataset:

.. code-block:: text

   State: NAVIGATE

No state transitions occurred in either TEST 1 or TEST 2.  The controller
remained locked in ``NAVIGATE`` from the first to the last logged message.

State Timeline with Velocity Commands
---------------------------------------

TEST 1
~~~~~~

.. figure:: ../../img/state_machine/state_machine_TEST1.png
   :width: 100%
   :align: center

   State timeline (top) with :math:`V_x`, :math:`V_y`, :math:`\omega_z`
   commands — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/state_machine/state_machine_TEST2.png
   :width: 100%
   :align: center

   State timeline with velocity commands — TEST 2.

The state-timeline panel shows a constant ``NAVIGATE`` bar, while the
velocity panels below confirm that the commands are continuously non-zero.

Interpretation
--------------

The absence of state transitions reveals that the controller **never
completed a waypoint approach** during Session 2.

**Expected behaviour (healthy system):**

1. Robot enters NAVIGATE and moves toward a waypoint.
2. When the distance-to-target drops below a threshold, the state machine
   transitions to IDLE or ROTATE.
3. After settling, it re-enters NAVIGATE for the next waypoint.

**Observed behaviour:**

Because the motors are not executing the commanded velocities (see
:doc:`transient_response`), the robot never actually arrives at any target.
The distance-to-target condition is never satisfied, so the state machine
remains in NAVIGATE indefinitely.

.. note::

   The state machine itself is functioning correctly — it correctly remains
   in NAVIGATE while the distance condition is unsatisfied.  The fault lies
   in the motor execution layer, not the state logic.

This finding is fully consistent with:

* Zero motor speed feedback (:doc:`motor_speed`)
* Constant encoder position (:doc:`transient_response`)
* Minimal actual displacement (:doc:`navigation_analysis`)
* 97 % shortfall in commanded vs actual yaw (:doc:`yaw_analysis`)

Key Findings
------------

1. **Single state (NAVIGATE) for both tests** — no IDLE, ROTATE, or any
   other state is ever reached.
2. **The state machine logic is correct** — it is blocked by the motor
   execution failure, not by a bug.
3. In Session 1, state transitions were observed, confirming the state
   machine code can work when motors respond.

.. seealso::

   :doc:`navigation_analysis` — The trajectory that keeps the robot far
   from its waypoint targets.

   :doc:`transient_response` — Goal-vs-position evidence of motor
   non-response.
