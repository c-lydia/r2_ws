Motor Command Goals
===================

Objective
---------

Examine the per-motor speed goals produced by the ``inverse_kinematic`` node
to verify that the kinematic transform is producing reasonable outputs and to
characterise the command profiles for each test.

Method
------

The ``inverse_kinematic`` node converts the high-level velocity vector
:math:`(V_x,\,V_y,\,\omega_z)` into per-motor speed goals using the
Mecanum kinematic matrix and publishes ``MotorCommand`` messages on
CAN IDs 1–4 at approximately **40 Hz** (median interval ≈ 25 ms).

The motor goal for wheel :math:`i` is:

.. math::

   g_i = \frac{1}{r}\bigl(V_x \pm V_y \pm (l_x+l_y)\,\omega_z\bigr)

where the sign pattern depends on the wheel position.  In Session 2,
command goals span from **−9.68** to **+2.61** motor units, representing
substantial commanded effort.

Metric Definitions
------------------

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Metric
     - Definition
   * - Mean goal
     - Time-average of the goal signal per CAN channel
   * - Std
     - Standard deviation — measures command steadiness
   * - Range
     - Peak-to-peak span :math:`\max(g) - \min(g)`

TEST 1
------

.. figure:: ../../img/motor_cmd/motor_cmd_goals_TEST1.png
   :width: 100%
   :align: center

   Per-motor command goals over time — TEST 1.

.. list-table:: Motor command statistics — TEST 1
   :header-rows: 1
   :widths: 12 18 18 18

   * - CAN
     - Mean goal
     - Std
     - Range
   * - 2
     - −4.41
     - 0.020
     - ≈ 0.06
   * - 3
     - +2.61
     - 0.000
     - 0.00
   * - 4
     - −9.62
     - 0.020
     - ≈ 0.06

**Interpretation:**  TEST 1 shows large, nearly constant goals.  CAN 4
commands near −9.6, CAN 2 near −4.4, and CAN 3 near +2.6.  The very low
standard deviations (≤ 0.02) indicate that the kinematic solver is
requesting a consistent omnidirectional motion — simultaneous lateral,
forward, and rotational movement — throughout the entire run.

TEST 2
------

.. figure:: ../../img/motor_cmd/motor_cmd_goals_TEST2.png
   :width: 100%
   :align: center

   Per-motor command goals over time — TEST 2.

**Interpretation:**  TEST 2 exhibits a different command profile.  CAN 2 and
CAN 3 oscillate around zero (range ≈ ±0.3), while CAN 4 alone carries the
majority of the effort (mean ≈ −5.1).  This asymmetry corresponds to a
predominantly longitudinal + rotational command (:math:`V_x \neq 0`,
:math:`V_y \approx 0`, :math:`\omega_z \approx 0.5`), which projects most
of the effort onto a single wheel pair.

Combined View
-------------

.. figure:: ../../img/motor_cmd/motor_cmd_goals_all.png
   :width: 100%
   :align: center

   All motor command goals (global time axis).

The combined view highlights the temporal gap between tests and the
qualitative difference in command profiles.  The kinematic transform is
functioning correctly in both cases — the different goal patterns are a
direct consequence of different :math:`(V_x, V_y, \omega_z)` inputs (see
:doc:`velocity_components`).

Key Findings
------------

1. **Kinematic solver is active** — goals span a wide range
   (−9.68 to +2.61), confirming the inverse-kinematic node is producing
   non-trivial motor commands.
2. **TEST 1 commands are near-constant** (std ≤ 0.02), indicating a smooth
   approach trajectory with minimal heading correction.
3. **TEST 2 commands are asymmetric** — CAN 4 dominates, reflecting a
   different velocity vector (backward + rotation).
4. **CAN 1 goals are present** but have no feedback pair (CAN 101 is
   absent), so motor 1 operates entirely unmonitored.

.. seealso::

   :doc:`velocity_components` — The controller commands that drive
   these motor goals.

   :doc:`motor_speed` — Motor-level feedback (speed and position)
   from CAN 102–104.

   :doc:`transient_response` — Goal vs position feedback comparison.
