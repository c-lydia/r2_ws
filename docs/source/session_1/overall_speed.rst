Overall Speed
=============

Objective
---------
Evaluate whether the robot maintains a consistent speed throughout each test.
The controller uses **P-only position control** with velocity saturation
(:math:`v_{max} = 3.0` m/s) and rate limiting (:math:`a_{max} = 0.2` m/s
per step at 10 Hz). Under this architecture, speed is expected to change
smoothly over time — proportional to the remaining position error — without
oscillation.

.. note::

   Overall speed is computed as the **mean of all reporting motor magnitudes**
   at each timestamp. Because motor 0 (CAN 102) never reports speed data and
   motors 2/3 report sparsely (see :doc:`motor_speed`), this metric is
   heavily weighted toward motor 1 (CAN 103).

Method
------
1. Per-motor speed magnitudes are computed as:

   .. math::

      |\mathbf{v}_i| = \sqrt{s_1^2 + s_2^2 + s_3^2 + s_4^2}

2. **Overall speed** = mean of all motor magnitudes at each timestamp.

3. A **rolling window** of ~1 second is applied to compute local mean and
   standard deviation — this shows whether speed is drifting or changing.

4. **PSD** (Power Spectral Density) is computed via FFT on a uniformly
   resampled signal to identify dominant frequency content.

Metrics
-------

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Metric
     - Meaning
   * - **Mean**
     - Average speed — the steady-state operating point
   * - **Std**
     - Standard deviation — how much speed changes over the test
   * - **CoV** (Std / Mean)
     - Coefficient of variation — relative variability, enables comparison
       across different speed levels
   * - **RMS**
     - Root mean square — combines mean level and variability
   * - **Peak**
     - Maximum absolute value reached
   * - **Peak-to-peak (P2P)**
     - Total swing range (max − min)
   * - **Dominant frequency**
     - Frequency with highest PSD — indicates periodic content if present


Velocity Components
-------------------
The odometry node publishes three velocity components: ``vx``, ``vy``, and
``wz``. These show the full velocity profile from the robot's frame.

TEST1
^^^^^

.. image:: ../img/vel_components/vel_components_TEST1.png
   :width: 100%
   :alt: Velocity components - TEST1

TEST2
^^^^^

.. image:: ../img/vel_components/vel_components_TEST2.png
   :width: 100%
   :alt: Velocity components - TEST2

.. note::

   ``vx`` and ``vy`` are both zero throughout because the odometry position
   estimation is not working (``can_id`` conflict prevents encoder position
   feedback from being decoded). Only the yaw rate ``wz`` derived from the
   IMU quaternion contains useful information. See :doc:`yaw_analysis` for
   ``wz`` stability.


TEST1
-----

Raw Speed
^^^^^^^^^

.. image:: ../img/overall_speed/overall_speed_TEST1.png
   :width: 100%
   :alt: Overall speed trace - TEST1

The overall speed for TEST1 shows the robot ramping up, reaching a steady
operating point, and maintaining it throughout the straight-line drive.

Stability (Rolling Mean ± Std)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/overall_stability/stability_overall_TEST1.png
   :width: 100%
   :alt: Stability plot - overall speed TEST1

- The **rolling mean** (orange) stays close to ~5.4 throughout the test.
- The **shaded band** (±1σ) is relatively narrow, indicating consistent output.
- The text annotation in the plot corner shows the numeric summary.

.. list-table::
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Mean
     - 5.43
   * - Std
     - 1.08
   * - CoV
     - 19.9%
   * - RMS
     - 5.54
   * - Peak
     - 9.19
   * - Peak-to-peak
     - 5.53
   * - Dominant freq
     - 2.02 Hz

**Interpretation:** Speed is stable at ~20% CoV. The peak of 9.19 is a brief
spike (visible in the motor speed plot as motor 1's spike to ~9.2 at
t ≈ 0.45 s), likely caused by a new waypoint activation or a transient in the
CAN reporting. The 2.02 Hz dominant frequency reflects the broadband energy
distribution in the signal — not a control-loop oscillation but rather the
natural speed profile of the P controller as the position error changes.

PSD (Frequency Domain)
^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/overall_stability/psd_overall_TEST1.png
   :width: 100%
   :alt: PSD - overall speed TEST1

The PSD shows the signal's energy distribution across frequencies:

- A broad peak around **~2.0 Hz** reflects the natural timescale of speed
  changes in the P controller combined with the CAN bus reporting cadence.
- The peak is **broadband**, not a sharp resonance — this indicates general
  variability rather than a specific oscillatory mode. The rate limiter
  (:math:`a_{max} = 0.2`) suppresses rapid changes, preventing any
  oscillatory behaviour.


TEST2
-----

Raw Speed
^^^^^^^^^

.. image:: ../img/overall_speed/overall_speed_TEST2.png
   :width: 100%
   :alt: Overall speed trace - TEST2

The overall speed for TEST2 is lower and shows more variation, which is
expected: the robot is navigating a curved path, so the velocity commands
change as the heading error and position error evolve together.

Stability (Rolling Mean ± Std)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/overall_stability/stability_overall_TEST2.png
   :width: 100%
   :alt: Stability plot - overall speed TEST2

- The **rolling mean** varies over the test duration, reflecting the changing
  velocity profile as the robot turns toward its waypoint.
- The **shaded band** is wider relative to the mean, as the speed naturally
  ramps up and down during the curved trajectory.

.. list-table::
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Mean
     - 2.49
   * - Std
     - 1.46
   * - CoV
     - **58.6%**
   * - RMS
     - 2.89
   * - Peak
     - 5.60
   * - Peak-to-peak
     - 5.60
   * - Dominant freq
     - 1.98 Hz

**Interpretation:** The higher CoV (59%) does **not** indicate control
instability. In a P-only position controller, the commanded velocity is
proportional to the remaining error (:math:`v = k_p \cdot e`). During a
curved trajectory the error magnitude changes continuously — the robot
accelerates toward the waypoint, turns, and the velocity profile reflects
these geometry changes. Additionally, the position feedback is not working
(CAN ID conflict on motor 0), so the controller uses stale position
estimates, causing the error computation to drift. The velocity saturation
(3.0 m/s) and rate limiter (0.2 m/s per step) ensure that the output remains
bounded and smooth despite these conditions.

PSD (Frequency Domain)
^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/overall_stability/psd_overall_TEST2.png
   :width: 100%
   :alt: PSD - overall speed TEST2

- Dominant frequency at **~2.0 Hz**, similar to TEST1.
- This shared frequency across both tests reflects the characteristic
  timescale of motor speed variation as reported by the CAN bus, not a
  control-loop oscillation.


Comparison
----------

.. image:: ../img/overall_stability/comparison_overall.png
   :width: 100%
   :alt: Overall speed comparison - TEST1 vs TEST2

Both tests are plotted on **normalised time** (0 to 1) so their shapes can be
compared despite different durations.

.. list-table::
   :header-rows: 1
   :widths: 15 15 15 15 15 15

   * - Test
     - Mean
     - Std
     - CoV
     - Peak
     - Dom. Freq
   * - TEST1
     - 5.43
     - 1.08
     - 19.9%
     - 9.19
     - 2.02 Hz
   * - TEST2
     - 2.49
     - 1.46
     - 58.6%
     - 5.60
     - 1.98 Hz

Key differences:

- TEST1 operates at more than double the speed of TEST2 (5.43 vs 2.49),
  consistent with a straight-line path having a larger, sustained position
  error in one direction.
- TEST2 has higher relative variability (59% vs 20% CoV) because the
  curved trajectory causes the position error — and therefore the velocity
  command — to change continuously.
- Both share a ~2 Hz dominant frequency, which corresponds to the natural
  timescale of speed variation from the CAN reporting and motor response,
  not a control-loop resonance.

Key Findings
------------

1. **The controller uses P-only position control with velocity saturation
   and rate limiting.** The commanded velocity is proportional to position
   error (:math:`v = k_p \cdot e`, where :math:`k_p = 0.2`), clamped to
   ±3.0 m/s, and rate-limited to 0.2 m/s change per control step (10 Hz).
   This architecture prevents oscillation by design — the rate limiter acts
   as implicit damping.

2. **TEST1 speed is stable.** A CoV of 20% with most of the variability
   coming from a single transient spike (9.19) indicates the controller
   maintains a consistent operating point during straight-line driving.

3. **TEST2 higher variability is expected behaviour**, not instability. The
   P controller naturally produces a changing velocity profile during a
   curved trajectory as the position error vector evolves. The 59% CoV
   reflects the geometry of the path, not a tuning problem.

4. **The ~2 Hz PSD peak** is broadband variability from motor speed changes
   and CAN reporting cadence, not a control-loop oscillation. No sharp
   resonance peak is present in either test.

5. **Overall speed metric is approximate** because motor 0 (CAN 102) is
   missing and motors 2/3 report sparsely. The metric primarily reflects
   motor 1's behaviour.

6. **Odometry velocity components** (vx, vy) are both zero due to the CAN ID
   conflict preventing position feedback. Only the IMU-derived yaw rate (wz)
   is available — see :doc:`yaw_analysis` for wz stability.

.. seealso::

   - :doc:`motor_speed` — per-motor traces and data completeness
   - :doc:`yaw_analysis` — yaw stability (affected by the same motor issues)
   - Raw data: ``test_data/overall_speed/odom_vels_TEST1.csv``,
     ``test_data/overall_speed/odom_vels_TEST2.csv``
   - Metrics: ``test_data/stability/stability_summary.csv``
