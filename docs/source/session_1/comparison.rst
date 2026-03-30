comparison
==========

This page consolidates all quantitative metrics from the individual analysis
pages into a single side-by-side view.

Test Summary
------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Property
     - TEST1
     - TEST2
   * - Trajectory
     - Straight-line to waypoint
     - Curved path with heading change
   * - Duration
     - ~0.5 s
     - ~0.3 s
   * - Mean overall speed
     - 5.43
     - 2.49
   * - Mean yaw rate (wz)
     - ≈ 0 rad/s
     - −0.302 rad/s (clockwise)


Motor Data Completeness
-----------------------

.. list-table::
   :header-rows: 1
   :widths: 20 20 20 20 20

   * - Motor
     - CAN ID
     - TEST1 samples
     - TEST2 samples
     - Notes
   * - motor 0
     - 102
     - 0
     - 0
     - ACK received, speed not decoded (CAN ID conflict)
   * - motor 1
     - 103
     - 53
     - 77
     - Primary reporting motor
   * - motor 2
     - 104
     - 8
     - 20
     - Sparse, ~17% slower in TEST1
   * - motor 3
     - 105
     - 43
     - 2
     - Nearly absent in TEST2

Motor 1 provides the bulk of speed feedback in both tests. The overall speed
metric is effectively motor 1's speed.


Overall Speed Comparison
------------------------

.. image:: ../img/overall_stability/comparison_overall.png
   :width: 100%
   :alt: Overall speed comparison - TEST1 vs TEST2

.. list-table::
   :header-rows: 1
   :widths: 12 12 12 12 12 12 12

   * - Test
     - Mean
     - Std
     - CoV
     - RMS
     - Peak
     - Dom. Freq
   * - TEST1
     - 5.43
     - 1.08
     - 19.9%
     - 5.54
     - 9.19
     - 2.02 Hz
   * - TEST2
     - 2.49
     - 1.46
     - 58.6%
     - 2.89
     - 5.60
     - 1.98 Hz

**Analysis:**

- TEST1 runs at more than double the speed — the straight-line path produces
  a larger, sustained position error in one direction, so the P controller
  outputs a higher velocity throughout.
- TEST2's higher CoV (59% vs 20%) is expected: the curved trajectory causes
  the position error vector to change continuously (direction and magnitude),
  so the commanded velocity varies accordingly.
- Both tests share a ~2 Hz dominant frequency, corresponding to the natural
  timescale of motor speed variation and CAN reporting cadence. No sharp
  resonance peaks are present.
- The rate limiter (:math:`a_{max} = 0.2` m/s per step) keeps transitions
  smooth in both cases.


Yaw Rate (wz) Comparison
-------------------------

.. image:: ../img/wz_stability/comparison_wz.png
   :width: 100%
   :alt: wz comparison - TEST1 vs TEST2

.. list-table::
   :header-rows: 1
   :widths: 12 15 12 12 12 15

   * - Test
     - Mean wz
     - Std
     - Peak
     - P2P
     - Dom. Freq
   * - TEST1
     - ≈ 0
     - ≈ 0
     - ≈ 0
     - ≈ 0
     - N/A
   * - TEST2
     - −0.302
     - 0.216
     - 0.854
     - 0.854
     - 3.9 Hz

**Analysis:**

- TEST1 has zero yaw activity — the robot drove straight with no heading
  change required.
- TEST2 shows the robot turning clockwise (negative wz) to reach a waypoint
  requiring a heading change. The 0.854 rad/s peak stays below the 1.0 rad/s
  velocity saturation limit.
- The 3.9 Hz dominant frequency reflects the characteristic timescale of
  heading adjustments — not oscillation.


Velocity Components
-------------------

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Component
     - TEST1
     - TEST2
   * - vx
     - 0 (no position feedback)
     - 0 (no position feedback)
   * - vy
     - 0 (no position feedback)
     - 0 (no position feedback)
   * - wz
     - ≈ 0 (straight line)
     - −0.302 rad/s mean (turning)

The ``vx`` and ``vy`` components are zero in both tests because the CAN ID
conflict on motor 0 prevents the ``current_odometry`` node from computing
encoder-based position and velocity. Only the IMU-derived yaw rate ``wz``
provides real feedback.


Controller Architecture
-----------------------

Both tests use the same controller (``robot_control.py``):

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Parameter
     - Value
     - Role
   * - ``k_p``
     - 0.2
     - P-only gain for position → velocity
   * - ``LINEAR_VEL_MAX``
     - 3.0 m/s
     - Velocity saturation (linear)
   * - ``ANGULAR_VEL_MAX``
     - 1.0 rad/s
     - Velocity saturation (angular)
   * - ``A_MAX``
     - 0.2 m/s per step
     - Rate limiter acceleration bound
   * - ``ERROR_THRESHOLD``
     - 0.05
     - Deadzone threshold
   * - Timer period
     - 0.1 s (10 Hz)
     - Control loop frequency

The pipeline is: ``p_controller()`` → ``deadzone()`` → ``velocity_limit()``
→ ``rate_limit()`` → publish ``/cmd_vel``.

The **rate limiter** is the key stability mechanism: it limits the velocity
change per step to :math:`a_{max} \cdot dt = 0.2 \times 0.1 = 0.02` m/s (or
rad/s), which prevents the controller output from oscillating regardless of
the P gain.


Summary
-------

.. list-table::
   :header-rows: 1
   :widths: 25 38 37

   * - Aspect
     - TEST1 (straight line)
     - TEST2 (curved path)
   * - Speed stability
     - Stable (20% CoV)
     - Variable (59% CoV) — expected
   * - Yaw stability
     - Zero turning — stable
     - Active turning — bounded
   * - Motor feedback
     - 3 of 4 motors report
     - 2 of 4 motors report reliably
   * - Velocity saturation
     - Not reached
     - Not reached
   * - Rate limiter
     - Active, smooth output
     - Active, smooth output

Both tests demonstrate that the P-only controller with velocity saturation
and rate limiting operates within its design bounds. The variability observed
in TEST2 is a consequence of the curved trajectory geometry, not controller
instability.

.. seealso::

   - :doc:`motor_speed` — per-motor details and data completeness
   - :doc:`overall_speed` — full speed stability analysis
   - :doc:`yaw_analysis` — full yaw rate analysis
   - :doc:`conclusion` — summary and next steps