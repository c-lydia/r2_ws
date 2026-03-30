Yaw Analysis
============

Objective
---------

Evaluate the robot's heading (yaw) behaviour, both in the time domain and
the frequency domain, to determine whether the commanded
:math:`\omega_z` is being executed and how stable the heading is over
time.

Method
------

The yaw angle :math:`\psi` is extracted from the ``udp_sender`` odom, which
reports actual robot heading.  The angular rate is computed numerically:

.. math::

   \dot{\psi}[k] = \frac{\psi[k] - \psi[k-1]}{t[k] - t[k-1]}

Unlike the ``current_odometry`` publisher (which outputs near-zero values),
the UDP odom yaw spans a meaningful range: **−0.66 to +1.50 rad**
(≈ 2.16 rad total across both tests).

**Expected outcome:**  With :math:`\omega_z \approx 0.5` rad/s commanded for
30+ s, the robot should accumulate :math:`0.5 \times 30 = 15` rad of
rotation.

Discrete-Time Yaw & Angular Rate
---------------------------------

TEST 1
~~~~~~

.. figure:: ../../img/yaw_analysis/yaw_discrete_TEST1.png
   :width: 100%
   :align: center

   Unwrapped yaw (top) and angular rate :math:`\dot{\psi}` (bottom) — TEST 1.

.. list-table:: Yaw metrics — TEST 1
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Yaw range
     - 0.65 → 1.50 rad
   * - Total rotation
     - ~0.85 rad (49°)
   * - Duration
     - 58 s
   * - Mean :math:`\dot{\psi}`
     - ~0.015 rad/s
   * - Peak :math:`|\dot{\psi}|`
     - ~0.1 rad/s

**Interpretation:**  The yaw in TEST 1 rises monotonically from ~0.65 to
~1.50 rad, accumulating only 0.85 rad over 58 s.  This corresponds to a mean
angular rate of ~0.015 rad/s — roughly **3 %** of the commanded
:math:`\omega_z = 0.5` rad/s.

TEST 2
~~~~~~

.. figure:: ../../img/yaw_analysis/yaw_discrete_TEST2.png
   :width: 100%
   :align: center

   Unwrapped yaw and angular rate — TEST 2.

.. list-table:: Yaw metrics — TEST 2
   :header-rows: 1
   :widths: 25 25

   * - Metric
     - Value
   * - Yaw range
     - −0.66 → −0.06 rad
   * - Total rotation
     - ~0.60 rad (34°)
   * - Mean :math:`\dot{\psi}`
     - ~0.018 rad/s

**Interpretation:**  TEST 2 yaw drifts from −0.66 to −0.06 rad — a change of
0.60 rad in the positive direction, yet the commanded :math:`\omega_z` was
positive.  The magnitude is still only ~3.6 % of expected, confirming the
open-loop motor issue.

Stability
---------

A 2 s rolling window is applied to the yaw and :math:`\dot{\psi}` signals to
assess stationarity.

TEST 1
~~~~~~

.. figure:: ../../img/yaw_analysis/yaw_stability_TEST1.png
   :width: 100%
   :align: center

   Yaw stability (rolling mean ± 1σ, 2 s window) — TEST 1.

.. figure:: ../../img/yaw_analysis/wz_stability_TEST1.png
   :width: 100%
   :align: center

   :math:`\dot{\psi}` stability (rolling mean ± 1σ) — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/yaw_analysis/yaw_stability_TEST2.png
   :width: 100%
   :align: center

   Yaw stability — TEST 2.

.. figure:: ../../img/yaw_analysis/wz_stability_TEST2.png
   :width: 100%
   :align: center

   :math:`\dot{\psi}` stability — TEST 2.

The rolling standard deviation of :math:`\dot{\psi}` is small relative to the
mean, indicating **quasi-stationary** drift rather than oscillatory
instability.

Power Spectral Density
----------------------

.. figure:: ../../img/yaw_analysis/psd_yaw_TEST1.png
   :width: 90%
   :align: center

   PSD of yaw — TEST 1.

.. figure:: ../../img/yaw_analysis/psd_wz_TEST1.png
   :width: 90%
   :align: center

   PSD of :math:`\dot{\psi}` — TEST 1.

.. figure:: ../../img/yaw_analysis/psd_yaw_TEST2.png
   :width: 90%
   :align: center

   PSD of yaw — TEST 2.

.. figure:: ../../img/yaw_analysis/psd_wz_TEST2.png
   :width: 90%
   :align: center

   PSD of :math:`\dot{\psi}` — TEST 2.

The yaw PSD is dominated by very-low-frequency content (< 0.1 Hz),
corresponding to the slow monotonic drift.  No narrow-band peaks are visible,
ruling out resonant oscillation in the heading loop.

:math:`\dot{\psi}` with Motor Commands
---------------------------------------

.. figure:: ../../img/wz_with_commands/wz_with_commands_TEST1.png
   :width: 100%
   :align: center

   :math:`\dot{\psi}` with motor command events overlaid — TEST 1.

.. figure:: ../../img/wz_with_commands/wz_with_commands_TEST2.png
   :width: 100%
   :align: center

   :math:`\dot{\psi}` with motor command events — TEST 2.

Vertical lines mark ``MotorCommand`` publish times (coloured by CAN ID).
The :math:`\dot{\psi}` signal shows **no strong correlation** with command
events, consistent with the open-loop condition — motor commands are being
sent but not causing proportional yaw changes.

Comparison
----------

.. figure:: ../../img/yaw_analysis/comparison_yaw.png
   :width: 100%
   :align: center

   Normalised-time comparison of yaw between tests.

Key Findings
------------

1. **Commanded vs actual yaw rate:** the controller commands
   :math:`\omega_z \approx 0.5` rad/s, but the measured
   :math:`\dot{\psi} \approx 0.015` rad/s — a **97 % shortfall**.
2. **Total rotation** over 30–60 s is only 0.6–0.85 rad instead of the
   expected 15+ rad.
3. **No resonant oscillation** is present in the PSD — the yaw drift is
   monotonic and smooth.
4. **No command–response correlation** is visible in the overlay plots,
   confirming the motor control layer is not driving the heading.
5. The small observed yaw change is likely from mechanical play, ground
   reaction asymmetry, or external disturbances.

.. seealso::

   :doc:`velocity_components` — The :math:`\omega_z` commands that should
   drive rotation.

   :doc:`impulse_response` — System-level :math:`\omega_z \to \dot{\psi}`
   transfer function.

   :doc:`navigation_analysis` — Heading impact on trajectory quality.
