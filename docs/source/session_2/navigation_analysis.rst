Navigation Analysis
====================

Objective
---------

Evaluate the robot's physical trajectory to determine whether it follows the
commanded path and reaches its waypoint targets.

Method
------

Position and heading are taken from the ``udp_sender`` odom
(:math:`x`, :math:`y`, :math:`\psi`).  XY trajectory plots show the path
the robot actually took, overlaid with any waypoint targets received via
``udp_listener``.  Start (▶) and end (■) positions are marked.

Expected displacement given the commanded speed and duration:

.. math::

   d_{\text{expected}} = |\mathbf{v}| \times T
   \approx 0.2\;\text{m/s} \times 50\;\text{s} = 10\;\text{m}

XY Trajectory
-------------

TEST 1
~~~~~~

.. figure:: ../../img/navigation/nav_trajectory_TEST1.png
   :width: 100%
   :align: center

   XY trajectory with waypoints — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/navigation/nav_trajectory_TEST2.png
   :width: 100%
   :align: center

   XY trajectory with waypoints — TEST 2.

Position & Heading vs Time
--------------------------

TEST 1
~~~~~~

.. figure:: ../../img/navigation/nav_signals_TEST1.png
   :width: 100%
   :align: center

   :math:`x`, :math:`y`, and :math:`\psi` vs time — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/navigation/nav_signals_TEST2.png
   :width: 100%
   :align: center

   :math:`x`, :math:`y`, and :math:`\psi` vs time — TEST 2.

Position Summary
----------------

.. list-table:: Position Range (UDP Odom)
   :header-rows: 1
   :widths: 12 22 22 22

   * - Test
     - :math:`x` range (m)
     - :math:`y` range (m)
     - :math:`\psi` range (rad)
   * - TEST 1
     - 1.25 → 2.11
     - 0.74 → 2.13
     - 0.65 → 1.50
   * - TEST 2
     - 1.25 → 2.11
     - 0.74 → 2.13
     - −0.66 → −0.06

.. list-table:: Displacement vs Expected
   :header-rows: 1
   :widths: 12 18 18 18

   * - Test
     - Actual disp. (m)
     - Expected disp. (m)
     - Ratio
   * - TEST 1
     - ~1.7
     - ~10
     - **17 %**
   * - TEST 2
     - ~1.5
     - ~7
     - **21 %**

Interpretation
--------------

**Observations:**

* The robot moved within a small patch of approximately **0.9 m × 1.4 m**
  across both tests.  The actual diagonal displacement (~1.5 m) is an
  order of magnitude less than the 9–18 m expected from the commanded
  velocities.

* The yaw differs markedly between tests: TEST 1 ends with
  :math:`\psi \approx 1.50` rad (86°), while TEST 2 stays near −0.3 rad.
  The robot's heading is dominated by its initial orientation plus
  passive drift, not by the controller's :math:`\omega_z` commands.

* The trajectory shapes are irregular — not the smooth arcs or
  straight-line segments expected from a functioning Mecanum drive.

* Three waypoint batches were received in TEST 1 (from ``udp_listener``),
  but zero in TEST 2.  The robot never arrived at any of them.

**Root cause:**  The motor control failure identified in
:doc:`transient_response` and :doc:`motor_speed` limits both translational
and rotational motion.  The small observed displacement is likely from
residual friction coupling or human intervention, not motor-driven actuation.

Key Findings
------------

1. **Actual displacement is ~10–20 % of expected** — confirming severe
   motor underperformance.
2. **No waypoints reached** — consistent with the NAVIGATE-only state
   machine (:doc:`state_machine_analysis`).
3. **Yaw is uncontrolled** — heading differs by ~2 rad between tests,
   determined by initial placement rather than commands.
4. **Trajectory is irregular** — not consistent with any commanded motion
   profile.

.. seealso::

   :doc:`yaw_analysis` — Detailed yaw behaviour and commanded vs actual
   angular rate comparison.

   :doc:`overall_speed` — Commanded speed that should have produced much
   greater displacement.

   :doc:`state_machine_analysis` — State machine stuck in NAVIGATE.
