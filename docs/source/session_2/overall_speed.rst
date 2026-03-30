Overall Commanded Speed
=======================

Objective
---------

Quantify the overall translational speed commanded by the controller and
assess its stability across each test run.

Method
------

Because motor speed feedback is zero (see :doc:`motor_speed`), the overall
speed is derived from the controller velocity commands:

.. math::

   |\mathbf{v}| = \sqrt{V_x^2 + V_y^2}

This represents the **commanded** translational speed, not a measured one.
A 2 s rolling window is used to compute mean ± 1σ for the stability plots.

.. note::

   :math:`\omega_z` is excluded from the speed magnitude because it
   represents rotation, not translation.

TEST 1
------

.. figure:: ../../img/overall_speed/overall_speed_TEST1.png
   :width: 100%
   :align: center

   Overall commanded speed :math:`\sqrt{V_x^2 + V_y^2}` — TEST 1.

.. figure:: ../../img/overall_stability/stability_speed_TEST1.png
   :width: 100%
   :align: center

   Stability: rolling mean ± 1σ (2 s window) — TEST 1.

.. list-table:: Speed statistics — TEST 1
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Mean speed
     - ~0.20 m/s
   * - Final speed
     - ~0.10 m/s
   * - Peak-to-peak
     - 0.316 m/s
   * - Duration
     - 32 s

**Interpretation:**  TEST 1 shows the commanded speed drifting from ~0.20
m/s down to ~0.10 m/s over 32 seconds.  This gradual decrease is consistent
with a waypoint approach — as the robot nears its target, the :math:`V_x`
component (which ramps toward −0.3) grows while :math:`V_y` shrinks, reducing
the overall magnitude.

TEST 2
------

.. figure:: ../../img/overall_speed/overall_speed_TEST2.png
   :width: 100%
   :align: center

   Overall commanded speed — TEST 2.

.. figure:: ../../img/overall_stability/stability_speed_TEST2.png
   :width: 100%
   :align: center

   Stability: rolling mean ± 1σ (2 s window) — TEST 2.

**Interpretation:**  TEST 2 maintains a nearly constant commanded speed of
~0.227 m/s with very low variance (std ≈ 0.007 m/s).  This indicates a
straight-line approach command with stable heading — the controller is not
continuously re-adjusting its trajectory.

Comparison
----------

.. figure:: ../../img/overall_speed/comparison_speed.png
   :width: 100%
   :align: center

   Normalised-time comparison of overall commanded speed.

.. list-table:: Speed comparison
   :header-rows: 1
   :widths: 15 20 20 20

   * - Test
     - Mean (m/s)
     - Std (m/s)
     - Peak-to-peak (m/s)
   * - TEST 1
     - ~0.20
     - 0.078
     - 0.316
   * - TEST 2
     - ~0.227
     - 0.007
     - ~0.024

**Interpretation:**  TEST 1 shows significant speed variation (p2p = 0.316
m/s) while TEST 2 is steady.  The difference arises because TEST 1's
controller is simultaneously adjusting heading (large :math:`\omega_z`) while
approaching a far waypoint, whereas TEST 2 commands a more direct path.

Key Findings
------------

1. **Commanded speed is non-zero** in both tests, confirming the controller
   is actively requesting translational motion.
2. **TEST 1 speed drifts** from 0.20 → 0.10 m/s — consistent with a curved
   approach trajectory.
3. **TEST 2 speed is quasi-stationary** at 0.227 m/s — the most stable
   signal in the entire dataset.
4. Despite commanding 0.2+ m/s for 30–60 s, actual displacement (from UDP
   odom) is only ~1.5 m — an order-of-magnitude shortfall confirming the
   motor control failure (see :doc:`navigation_analysis`).

.. seealso::

   :doc:`velocity_components` — Individual :math:`V_x`, :math:`V_y`,
   :math:`\omega_z` analysis.

   :doc:`stability_analysis` — Per-component stability and PSD.

   :doc:`navigation_analysis` — Actual vs expected displacement.
