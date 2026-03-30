Velocity Components
===================

Objective
---------

Analyse the individual velocity command components
(:math:`V_x`, :math:`V_y`, :math:`\omega_z`) to understand the controller's
kinematic intent and identify any saturation, drift, or instability.

Method
------

The ``robot_control_node`` publishes velocity commands at ~10 Hz.  These are
the **only non-zero velocity signals** in Session 2, since the
``current_odometry`` publisher reports :math:`(0.0,\,0.0)` due to zero motor
speed feedback (see :doc:`motor_speed`).

Metric Definitions
------------------

.. list-table::
   :header-rows: 1
   :widths: 18 50

   * - Metric
     - Definition
   * - Mean
     - Time-average of the signal over the test duration
   * - Std
     - Standard deviation — measures signal variability
   * - Peak \|x\|
     - Maximum absolute value reached
   * - Peak-to-peak
     - :math:`\max - \min` — full excursion range

TEST 1 — :math:`V_x`, :math:`V_y`, :math:`\omega_z`
-----------------------------------------------------

.. figure:: ../../img/vel_components/ctrl_vel_commands_TEST1.png
   :width: 100%
   :align: center

   :math:`V_x`, :math:`V_y`, and :math:`\omega_z` commands (separate subplots) — TEST 1.

.. figure:: ../../img/vel_components/ctrl_vel_overlay_TEST1.png
   :width: 100%
   :align: center

   Combined overlay of :math:`V_x`, :math:`V_y`, :math:`\omega_z` — TEST 1.

.. list-table:: Controller command statistics — TEST 1
   :header-rows: 1
   :widths: 12 15 15 15 15

   * - Signal
     - Mean
     - Std
     - Peak \|x\|
     - Peak-to-peak
   * - :math:`V_x`
     - −0.097 m/s
     - 0.078 m/s
     - 0.318 m/s
     - 0.316 m/s
   * - :math:`V_y`
     - +0.171 m/s
     - 0.041 m/s
     - 0.262 m/s
     - 0.175 m/s
   * - :math:`\omega_z`
     - +0.403 rad/s
     - 0.047 rad/s
     - 0.500 rad/s
     - 0.184 rad/s

**Interpretation:**  The robot is commanded to move laterally
(:math:`V_y > 0`) while also rotating (:math:`\omega_z \approx 0.4` rad/s).
The :math:`V_x` component ramps from near zero toward −0.3 m/s, suggesting a
curved approach trajectory to a waypoint.  The saturation at
:math:`\omega_z = 0.5` rad/s indicates the controller is clamped at its
maximum rotational rate.

TEST 2 — :math:`V_x`, :math:`V_y`, :math:`\omega_z`
-----------------------------------------------------

.. figure:: ../../img/vel_components/ctrl_vel_commands_TEST2.png
   :width: 100%
   :align: center

   :math:`V_x`, :math:`V_y`, and :math:`\omega_z` commands — TEST 2.

.. figure:: ../../img/vel_components/ctrl_vel_overlay_TEST2.png
   :width: 100%
   :align: center

   Combined overlay — TEST 2.

.. list-table:: Controller command statistics — TEST 2
   :header-rows: 1
   :widths: 12 15 15 15 15

   * - Signal
     - Mean
     - Std
     - Peak \|x\|
     - Peak-to-peak
   * - :math:`V_x`
     - −0.227 m/s
     - 0.007 m/s
     - 0.233 m/s
     - 0.024 m/s
   * - :math:`V_y`
     - +0.009 m/s
     - 0.009 m/s
     - 0.034 m/s
     - 0.035 m/s
   * - :math:`\omega_z`
     - +0.497 rad/s
     - 0.010 rad/s
     - 0.500 rad/s
     - 0.060 rad/s

**Interpretation:**  TEST 2 is qualitatively different.
:math:`V_x` is steady near −0.23 m/s (backwards), :math:`V_y \approx 0`,
and :math:`\omega_z` is saturated at ~0.5 rad/s.  This is a "reverse while
rotating" command — the controller has locked into a heading-correction mode
and is simultaneously backing up toward its target.  The extremely low std
values (≤ 0.010) show that the commands are essentially constant.

Comparison
----------

.. figure:: ../../img/vel_components/comparison_ctrl_vel.png
   :width: 100%
   :align: center

   Normalised-time comparison of :math:`V_x`, :math:`V_y`, :math:`\omega_z`
   between tests.

Key Findings
------------

1. **TEST 1 is multi-axis** — high lateral (:math:`V_y \approx 0.17`) with
   variable forward (:math:`V_x`), commanding a curved trajectory.
2. **TEST 2 is uni-axial** — near-zero lateral with steady backward
   (:math:`V_x \approx -0.23`), commanding a straight reverse path.
3. **Both tests saturate** :math:`\omega_z` at 0.5 rad/s — the maximum
   allowed by the controller.  Over 30 s this *should* produce >15 rad of
   rotation; the actual yaw change is <1 rad (see :doc:`yaw_analysis`).
4. **No oscillatory instability** is present — all signals are monotonic or
   quasi-constant.

.. seealso::

   :doc:`overall_speed` — Aggregate speed :math:`\sqrt{V_x^2 + V_y^2}`.

   :doc:`stability_analysis` — Rolling-window stability and PSD for each
   component.

   :doc:`motor_cmd` — How these velocity commands map to per-motor goals.
