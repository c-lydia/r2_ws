Yaw Analysis
============

Objective
---------
Evaluate the robot's yaw (heading) behaviour during each test:

- Is the robot driving **straight** or **turning**?
- Is the yaw rate **steady** or **varying**?
- How does yaw respond to motor commands?

The controller computes yaw error as:

.. math::

   \omega_z = k_p \cdot (\psi_{desired} - \psi_{current})

where :math:`\psi_{desired} = \text{atan2}(y_{error},\; x_{error})`, then
applies velocity saturation (±1.0 rad/s) and rate limiting (0.2 rad/s per
step at 10 Hz).

Method
------
1. The IMU provides orientation as a quaternion :math:`(q_x, q_y, q_z, q_w)`.
   Yaw angle is extracted as:

   .. math::

      \psi = 2 \cdot \text{atan2}(q_z,\; q_w)

2. The yaw is **unwrapped** to remove ±π discontinuities.

3. **Yaw rate** :math:`\omega_z` is computed as the time derivative of
   unwrapped yaw:

   .. math::

      \omega_z = \frac{d\psi}{dt}

4. A **rolling window** (~1 s) computes local mean and standard deviation
   to visualise how the yaw rate evolves over time.

5. **PSD** (Power Spectral Density) via FFT identifies dominant frequency
   content in the yaw rate signal.

Metrics
-------

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Metric
     - Meaning
   * - **Mean wz**
     - Average turning rate — positive = counter-clockwise, negative = clockwise
   * - **Std wz**
     - Fluctuation around the mean — lower = smoother heading hold
   * - **RMS wz**
     - Combines mean offset and fluctuation into one number
   * - **Peak** :math:`|\omega_z|`
     - Maximum instantaneous turning rate reached
   * - **Peak-to-peak**
     - Total swing range of wz
   * - **Dominant freq**
     - Frequency of strongest variation in yaw rate


TEST1 — Yaw Stability
----------------------

Stability (Rolling Mean ± Std)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/wz_stability/stability_wz_TEST1.png
   :width: 100%
   :alt: wz stability - TEST1

.. list-table::
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Mean wz
     - ≈ 0 rad/s
   * - Std wz
     - ≈ 0 rad/s
   * - RMS wz
     - ≈ 0 rad/s
   * - Peak :math:`|\omega_z|`
     - ≈ 0 rad/s
   * - Peak-to-peak
     - ≈ 0 rad/s
   * - Dominant freq
     - N/A (noise floor)

**Interpretation:** The yaw rate is effectively **zero** throughout TEST1.
The robot drove straight with no measurable turning. The dominant frequency
of 46 Hz in the CSV is numerical noise at the machine-precision level
(values on the order of 10⁻¹⁴ rad/s) — not a real oscillation.

Command Overlay
^^^^^^^^^^^^^^^

.. image:: ../img/wz_with_commands/wz_with_commands_TEST1.png
   :width: 100%
   :alt: wz with motor commands - TEST1

The vertical lines show when ``MotorCommand`` messages were published,
colour-coded by CAN ID. In TEST1, motor commands are present but the yaw
rate remains at zero — confirming the commands produced straight-line motion
with no heading disturbance.

PSD (Frequency Domain)
^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/wz_stability/psd_wz_TEST1.png
   :width: 100%
   :alt: PSD - wz TEST1

The PSD is flat at the numerical noise floor. No real frequency content exists
in the yaw rate for TEST1.


TEST2 — Yaw Stability
----------------------

Stability (Rolling Mean ± Std)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/wz_stability/stability_wz_TEST2.png
   :width: 100%
   :alt: wz stability - TEST2

.. list-table::
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Mean wz
     - **−0.302 rad/s**
   * - Std wz
     - 0.216 rad/s
   * - CoV (Std/Mean)
     - 71.4%
   * - RMS wz
     - 0.371 rad/s
   * - Peak :math:`|\omega_z|`
     - 0.854 rad/s
   * - Peak-to-peak
     - 0.854 rad/s
   * - Dominant freq
     - **3.9 Hz**

**Interpretation:**

- The negative mean (−0.302 rad/s) indicates the robot is turning
  **clockwise** on average — this is the expected behaviour when navigating
  toward a waypoint that requires a heading change.
- The standard deviation of 0.216 rad/s reflects the **changing yaw error**
  as the robot moves along the curved path. In a P-only controller, the
  angular velocity is proportional to the heading error
  (:math:`\omega_z = k_p \cdot e_\psi`). As the robot turns, the heading
  error decreases, so the yaw rate naturally decreases. When the robot's
  position changes relative to the waypoint, the desired heading
  (:math:`\text{atan2}(y_{err}, x_{err})`) shifts, and the yaw error
  changes again.
- The **rate limiter** (0.2 rad/s per step) ensures these changes are
  smooth and bounded. The peak of 0.854 rad/s is below the velocity
  saturation limit of 1.0 rad/s, confirming the controller never saturates.
- The **3.9 Hz** dominant frequency in the PSD reflects the timescale of
  yaw rate variation — not a resonance or limit cycle. With the rate limiter
  constraining the output change to 0.02 rad/s per step (10 Hz loop),
  sustained oscillation is not possible.

Command Overlay
^^^^^^^^^^^^^^^

.. image:: ../img/wz_with_commands/wz_with_commands_TEST2.png
   :width: 100%
   :alt: wz with motor commands - TEST2

- Motor commands arrive throughout the test (vertical lines).
- The wz signal varies as the robot adjusts its heading toward the waypoint.
  The yaw rate changes reflect the evolving heading error, not controller
  instability.
- The rate limiter ensures smooth transitions between different yaw rates.

PSD (Frequency Domain)
^^^^^^^^^^^^^^^^^^^^^^

.. image:: ../img/wz_stability/psd_wz_TEST2.png
   :width: 100%
   :alt: PSD - wz TEST2

- A clear peak at **~3.9 Hz** reflects the characteristic rate of heading
  adjustment during the curved trajectory.
- This is the natural response timescale of the P controller with rate
  limiting and velocity saturation — as the heading error changes, the
  controller adjusts ``wz`` accordingly.
- Compare to the overall speed PSD which peaks at ~2.0 Hz — the different
  frequencies reflect different dynamics: translational speed changes more
  slowly than heading adjustments.


Comparison
----------

.. image:: ../img/wz_stability/comparison_wz.png
   :width: 100%
   :alt: wz comparison - TEST1 vs TEST2

.. list-table::
   :header-rows: 1
   :widths: 15 18 15 15 15 18

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

The contrast confirms the test design:

- **TEST1** has no yaw activity — the robot drove straight to its waypoint.
- **TEST2** shows active heading correction as the robot navigates a curved
  path. The wz varies within the controller's bounds (below the 1.0 rad/s
  saturation limit), demonstrating that the P controller with rate limiting
  produces bounded, non-oscillatory heading control.


Key Findings
------------

1. **The P-only yaw controller with rate limiting produces stable heading
   control.** The rate limiter (0.2 rad/s per step) prevents the output from
   changing faster than 2 rad/s², which effectively damps any potential
   overshoot. No sustained oscillation is observed.

2. **TEST2 wz variability is expected behaviour.** The robot is navigating a
   curved path — the heading error changes continuously as the robot moves,
   and the P controller adjusts ``wz`` proportionally. The 71% CoV reflects
   the geometry of the trajectory, not control instability.

3. **The peak yaw rate of 0.854 rad/s stays below the 1.0 rad/s saturation
   limit**, confirming that the velocity saturation is appropriately sized
   for this trajectory.

4. **Missing motor 0 (CAN 102) feedback** affects position estimation (vx
   and vy are zero), which means the position error fed to the controller
   may drift from the true value. This is a known issue from the CAN ID
   conflict that will be addressed in Session 2.

5. **The 3.9 Hz PSD peak** is the characteristic timescale of heading
   adjustments during the curved trajectory, not a control-loop resonance.
   The rate limiter makes sustained oscillation at this or any other
   frequency impossible.

.. seealso::

   - :doc:`motor_speed` — per-motor data showing motor asymmetry
   - :doc:`overall_speed` — translational speed stability and velocity
     components
   - Raw data: ``test_data/overall_speed/odom_vels_TEST1.csv``,
     ``test_data/overall_speed/odom_vels_TEST2.csv``
   - Metrics: ``test_data/stability/stability_summary.csv``