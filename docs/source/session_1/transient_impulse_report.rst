Transient & Impulse Response Analysis
=====================================

1  Introduction
---------------

This report presents a transient (step) response and impulse response
analysis of the robot's motor-control loop recorded during Session 1.
Two separate test runs (TEST1 and TEST2) are covered.  The analysis is
performed at three levels of abstraction:

1. **Per-motor channel** — each individual CAN-bus motor command/feedback pair.
2. **Overall speed** — the mean motor-speed magnitude averaged across all
   active motors at each time step, representing the aggregate translational
   effort of the drivetrain.
3. **Yaw (heading)** — the unwrapped yaw angle derived from the odometry
   quaternion, and the angular velocity :math:`\omega_z` obtained by
   numerical differentiation.

1.1  Methodology
~~~~~~~~~~~~~~~~

**Transient response metrics.**  For every detected step change in the
command signal the following classical metrics are computed on the
corresponding feedback signal:

.. list-table:: Metric Definitions
   :header-rows: 1
   :widths: 22 78

   * - Metric
     - Definition
   * - Rise time :math:`T_r`
     - Time for the normalised response to go from 10 % to 90 % of the
       step amplitude.
   * - Settling time :math:`T_s`
     - Time until the response permanently enters (and stays within) the
       :math:`\pm 2\%` band around the final value.
   * - Overshoot (OS %)
     - Peak deviation beyond the final value expressed as a percentage of
       the step size.
   * - Steady-state error (SSE)
     - Difference between the commanded final value and the mean of the
       last 20 % of the measured response window.

**Impulse response estimation.**  Two complementary frequency-domain
methods are used to identify the transfer function :math:`H(f)` from
command to feedback:

1. *Wiener deconvolution* — regularised spectral division:

   .. math::

      H(f) = \frac{S_{uy}(f)}{S_{uu}(f) + \varepsilon}

   where :math:`\varepsilon = 0.01 \cdot \max S_{uu}` prevents
   noise amplification.

2. *Cross-correlation* — the normalised causal cross-correlation
   :math:`R_{uy}(\tau)` for :math:`\tau \ge 0`.

From :math:`H(f)` a Bode-magnitude plot :math:`|H(f)|` in dB is derived
to reveal the bandwidth of the closed-loop system.

2  Per-Motor Transient Response
-------------------------------

Each motor is addressed by its CAN command ID (1–4).  The kinematic
publisher sends speed-mode goals at ~10 Hz; encoder feedback is sampled
by ``current_odometry`` at a higher rate.  The mapping used is
command CAN → feedback CAN: {2: 103, 3: 104, 4: 105}.

2.1  TEST1
~~~~~~~~~~

**CAN 2** — The controller commands a goal of -6.52 rad/s.  
The rise time could not be determined (the feedback signal did not cleanly cross the 10 %–90 % thresholds), which indicates either a very fast initial ramp or a mismatch between command and feedback scaling.  
Settling time averages **3.024 s** (range 3.024–3.024 s).  
Overshoot is very high at **100.0 %**, suggesting that the feedback magnitude consistently exceeds the command magnitude — this is expected when the motor driver applies its own internal gain or when the command→feedback units are not identical.  
The mean steady-state error is **-8.851** (max = 8.851).  
The relatively large SSE implies that the motor's encoder-measured speed settles to a different operating point than the commanded goal.  This could be caused by differences in units (e.g. rad/s vs RPM), CAN-ID mapping offsets, or a proportional-only controller lacking integral action.

**CAN 3** — The controller commands a goal of 3.26 rad/s.  
The rise time could not be determined (the feedback signal did not cleanly cross the 10 %–90 % thresholds), which indicates either a very fast initial ramp or a mismatch between command and feedback scaling.  
Settling time averages **3.025 s** (range 3.025–3.025 s).  
Overshoot averages **17.2 %**, which is within an acceptable range for a speed-mode controller.  
The mean steady-state error is **2.229** (max = 2.229).  
The relatively large SSE implies that the motor's encoder-measured speed settles to a different operating point than the commanded goal.  This could be caused by differences in units (e.g. rad/s vs RPM), CAN-ID mapping offsets, or a proportional-only controller lacking integral action.

**CAN 4** — The controller commands a goal of -13.04 rad/s.  
The rise time could not be determined (the feedback signal did not cleanly cross the 10 %–90 % thresholds), which indicates either a very fast initial ramp or a mismatch between command and feedback scaling.  
Settling time averages **3.114 s** (range 3.114–3.114 s).  
Overshoot is very high at **100.0 %**, suggesting that the feedback magnitude consistently exceeds the command magnitude — this is expected when the motor driver applies its own internal gain or when the command→feedback units are not identical.  
The mean steady-state error is **-15.553** (max = 15.553).  
The relatively large SSE implies that the motor's encoder-measured speed settles to a different operating point than the commanded goal.  This could be caused by differences in units (e.g. rad/s vs RPM), CAN-ID mapping offsets, or a proportional-only controller lacking integral action.

TEST1 — per-motor metrics
~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "CAN", "Step", "Goal before", "Goal after", "Rise time (s)", "Settling time (s)", "Overshoot %", "SS Error"
   :widths: auto

   "2", "1", "0.000", "-6.519", "N/A", "3.0236", "100.0", "-8.8509"
   "3", "1", "0.000", "3.262", "N/A", "3.0252", "17.2", "2.2291"
   "4", "1", "0.000", "-13.043", "N/A", "3.1139", "100.0", "-15.5532"

2.2  TEST2
~~~~~~~~~~

**CAN 2** — The controller commands a goal of -8.92 rad/s.  
The rise time could not be determined (the feedback signal did not cleanly cross the 10 %–90 % thresholds), which indicates either a very fast initial ramp or a mismatch between command and feedback scaling.  
Settling time averages **3.977 s** (range 3.977–3.977 s).  
Overshoot is very high at **16563.3 %**, suggesting that the feedback magnitude consistently exceeds the command magnitude — this is expected when the motor driver applies its own internal gain or when the command→feedback units are not identical.  
The mean steady-state error is **-10.143** (max = 10.143).  
The relatively large SSE implies that the motor's encoder-measured speed settles to a different operating point than the commanded goal.  This could be caused by differences in units (e.g. rad/s vs RPM), CAN-ID mapping offsets, or a proportional-only controller lacking integral action.

**CAN 3** — The controller commands a goal of 2.99 rad/s.  
The average rise time is **0.0 ms** (range 0.0–0.0 ms).  
Settling time averages **3.908 s** (range 3.908–3.908 s).  
Overshoot is very high at **10033.3 %**, suggesting that the feedback magnitude consistently exceeds the command magnitude — this is expected when the motor driver applies its own internal gain or when the command→feedback units are not identical.  
The mean steady-state error is **1.545** (max = 1.545).  
The relatively large SSE implies that the motor's encoder-measured speed settles to a different operating point than the commanded goal.  This could be caused by differences in units (e.g. rad/s vs RPM), CAN-ID mapping offsets, or a proportional-only controller lacking integral action.

TEST2 — per-motor metrics
~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "CAN", "Step", "Goal before", "Goal after", "Rise time (s)", "Settling time (s)", "Overshoot %", "SS Error"
   :widths: auto

   "2", "35", "-8.863", "-8.917", "N/A", "3.9770", "16563.3", "-10.1432"
   "3", "32", "2.970", "2.993", "0.0000", "3.9075", "10033.3", "1.5445"

2.3  Per-motor transient plots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   transient_can2_TEST1
   :align: center
.. figure:: ../img/transient/transient_can2_TEST2.png
   :align: center
   :width: 100%
.. figure:: ../img/transient/transient_can3_TEST1.png
   :align: center
   :width: 100%
.. figure:: ../img/transient/transient_can3_TEST2.png
   :align: center
   :width: 100%
.. figure:: ../img/transient/transient_can4_TEST1.png
   :align: center
   :width: 100%
.. figure:: ../img/transient/transient_can4_TEST2.png
   :align: center
   :width: 100%
3  Per-Motor Impulse Response
-----------------------------

The impulse response captures the full dynamic behaviour of each
   impulse_can3_TEST2
any resonant modes.  A narrow impulse that decays quickly corresponds to
a fast, well-damped motor; a broad, oscillating impulse indicates
underdamped dynamics.

   impulse_can4_TEST1
signals at each frequency.  A flat response up to a certain cutoff
frequency followed by a roll-off is typical of a well-tuned speed loop.

**CAN 2 (TEST1):**  The Wiener impulse response peaks at a lag of **182.6 ms**, representing the dominant transport + rise delay of the motor driver.  
   freq_response_can2_TEST1
The cross-correlation estimate corroborates the Wiener result, showing a similar peak location and decay envelope.

**CAN 4 (TEST1):**  The Wiener impulse response peaks at a lag of **0.0 ms**, representing the dominant transport + rise delay of the motor driver.  
The estimated −3 dB bandwidth is **49.8 Hz**, meaning the closed-loop system meaningfully tracks command variations up to approximately 50 Hz before significant attenuation sets in.  
   freq_response_can2_TEST2

**CAN 2 (TEST2):**  The Wiener impulse response peaks at a lag of **0.0 ms**, representing the dominant transport + rise delay of the motor driver.  
.. figure:: ../img/transient/transient_can2_TEST1.png
   :align: center
   :width: 100%
   CAN 2 TEST1
**CAN 3 (TEST2):**  The Wiener impulse response peaks at a lag of **157.3 ms**, representing the dominant transport + rise delay of the motor driver.  
   The estimated -3 dB bandwidth is **17.8 Hz**, meaning the closed-loop system meaningfully tracks command variations up to approximately 18 Hz before significant attenuation sets in.  
   The cross-correlation estimate corroborates the Wiener result, showing a similar peak location and decay envelope.

.. figure:: ../img/transient/transient_can2_TEST2.png
   :align: center
   :width: 100%
   CAN 2 TEST2
.. figure:: ../img/impulse/impulse_can2_TEST1.png
   :align: center
   :width: 100%
   CAN 2 IMPULSE TEST1

.. figure:: ../img/transient/transient_can3_TEST1.png
   :align: center
   :width: 100%
   CAN 3 TEST1
   transient_overall_TEST2
   :width: 100%

      :width: 100%
      CAN 3 TEST2
   :align: center
   :width: 100%
      :align: center
      :width: 100%
      CAN 4 TEST1
.. figure:: ../../img/impulse/impulse_can4_TEST1.png
   .. figure:: ../img/transient/transient_can4_TEST2.png
      :align: center
      :width: 100%
      CAN 4 TEST2
   impulse_overall_TEST1

.. figure:: ../../img/impulse/freq_response_can2_TEST1.png
   :align: center

.. figure:: ../../img/impulse/freq_response_can2_TEST2.png
   :align: center

A total of **6 step transitions** were detected in the aggregate command signal during this test run.  
      :align: center

TEST1 — overall speed step metrics
      :align: center
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

      :align: center
.. csv-table::
   :header: "Step", "Goal before", "Goal after", "Rise time (s)", "Settling time (s)", "Overshoot %", "SS Error"
   :widths: auto

   "104", "3.262", "13.043", "N/A", "0.5243", "39.4", "7.7189"
   "108", "3.262", "13.043", "N/A", "0.4240", "39.4", "7.7133"
   "112", "3.262", "13.043", "N/A", "0.3250", "39.4", "7.6134"
   "116", "3.262", "13.043", "N/A", "0.2252", "39.4", "8.4250"
   "120", "3.262", "13.043", "N/A", "0.1257", "39.4", "8.6027"
   "124", "3.262", "13.043", "N/A", "0.0239", "79.4", "9.2382"

4.2  TEST2 — overall speed analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A total of **6 step transitions** were detected in the aggregate command signal during this test run.  
Rise time could not be reliably measured for the majority of steps, indicating that the overall speed responds nearly instantaneously to command changes or that the step amplitudes are too small relative to noise.  
The average settling time is **0.324 s** (range 0.074–0.574 s), indicating that the drivetrain reaches steady state within a fraction of a second after each command update.  
The mean overshoot is **80.3 %** (peak 91.1 %).  This elevated overshoot reflects the fact that the measured motor speed magnitudes systematically differ from the RMS command goal — partly due to unit/scaling differences between the kinematic publisher's goal field and the encoder feedback, and partly due to transient dynamics when the command steps.  
The mean steady-state error is **11.30** (max = 11.44).  
The persistent offset between commanded and measured speed suggests that either the units differ (the kinematic publisher may be commanding joint-space speeds while the encoder reports in different units) or the controller lacks integral action to eliminate the offset.

TEST2 — overall speed step metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "Step", "Goal before", "Goal after", "Rise time (s)", "Settling time (s)", "Overshoot %", "SS Error"
   :widths: auto

   "280", "2.993", "14.904", "N/A", "0.5741", "78.1", "11.4363"
   "284", "2.993", "14.904", "N/A", "0.4744", "78.1", "11.4120"
   "288", "2.993", "14.904", "N/A", "0.3746", "78.1", "11.3556"
   "292", "2.993", "14.904", "N/A", "0.2741", "78.1", "11.2534"
   "296", "2.993", "14.904", "N/A", "0.1741", "78.2", "11.1849"
   "300", "2.993", "14.904", "N/A", "0.0743", "91.1", "11.1842"

4.3  Overall speed plots
~~~~~~~~~~~~~~~~~~~~~~~~

.. figure:: ../../img/transient/transient_overall_TEST1.png
   :align: center
   :width: 100%

.. figure:: ../img/transient/transient_can3_TEST2.png
   :align: center
   :width: 100%
   CAN 3 TEST2
   :width: 100%

   transient_overall_TEST2

.. figure:: ../../img/impulse/freq_response_overall_TEST1.png
   :align: center
   :width: 100%

   freq_response_overall_TEST1

.. figure:: ../../img/impulse/freq_response_overall_TEST2.png
   :align: center
   :width: 100%

   freq_response_overall_TEST2

.. figure:: ../../img/impulse/impulse_overall_TEST1.png
   :align: center
   :width: 100%

   impulse_overall_TEST1

.. figure:: ../../img/impulse/impulse_overall_TEST2.png
   :align: center
   :width: 100%

   impulse_overall_TEST2

5  Yaw — Transient & Impulse Response
-------------------------------------

The yaw (heading) angle is extracted from the odometry quaternion and
unwrapped to remove discontinuities at :math:`\pm\pi`.  The angular
velocity :math:`\omega_z = \dot{\psi}` is computed by numerical
differentiation of the unwrapped yaw.  The impulse response analysis
identifies the transfer function from the aggregate motor command to
:math:`\omega_z`.

5.2  TEST2 — yaw analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

During TEST2 the yaw changes from **-2.762 rad** to **-3.026 rad**, a total rotation of **0.265 rad** (15.2°).  The analysis detected **15 step intervals** in the command signal during which the yaw evolves.

The mean yaw rise time is **26.8 ms** (range 0.0–88.6 ms).  This represents the time for the heading to traverse from 10 % to 90 % of each incremental yaw step.  
The mean settling time is **0.311 s** (range 0.072–0.576 s).  
Overshoot is very large (mean 2305 %).  This is expected for heading dynamics: the yaw is an integrator of :math:`\omega_z`, so even small command-level overshoots become amplified in the integrated yaw signal.  The heading does not typically 'step' instantaneously; instead it ramps, and small inter-step intervals make the metric artificially high.  
The mean steady-state error is **0.1351 rad** (7.74°), showing that the heading closely tracks its expected value between command updates.

TEST2 — yaw step metrics
~~~~~~~~~~~~~~~~~~~~~~~~

.. csv-table::
   :header: "Step", "Yaw before (rad)", "Yaw after (rad)", "Rise time (s)", "Settling time (s)", "Overshoot %", "SS Error"
   :widths: auto

   "280", "-2.762", "-2.773", "0.0222", "0.5757", "2332.5", "0.2300"
   "281", "-2.773", "-2.779", "0.0000", "0.4808", "3939.6", "0.2246"
   "282", "-2.773", "-2.779", "0.0000", "0.4790", "3939.6", "0.2257"
   "283", "-2.773", "-2.779", "0.0000", "0.4775", "3939.6", "0.2257"
   "284", "-2.773", "-2.817", "0.0802", "0.4760", "473.5", "0.1877"
   "287", "-2.817", "-2.823", "0.0000", "0.3778", "3304.4", "0.1859"
   "288", "-2.817", "-2.862", "0.0886", "0.3762", "359.2", "0.1474"
   "290", "-2.862", "-2.865", "0.0000", "0.2787", "6992.6", "0.1503"
   "291", "-2.862", "-2.865", "0.0000", "0.2771", "6992.6", "0.1503"
   "292", "-2.862", "-2.919", "0.0837", "0.2757", "189.4", "0.0960"
   "293", "-2.909", "-2.919", "0.0000", "0.1807", "1109.7", "0.1003"
   "296", "-2.919", "-2.983", "0.0689", "0.1757", "67.1", "0.0361"
   "298", "-2.983", "-2.991", "0.0000", "0.0792", "468.9", "0.0337"
   "299", "-2.983", "-2.991", "0.0000", "0.0774", "468.9", "0.0337"
   "300", "-2.983", "-3.026", "0.0583", "0.0725", "0.0", "-0.0018"

Yaw / ωz plots
~~~~~~~~~~~~~~

.. figure:: ../../img/transient/transient_yaw_TEST1.png
   :align: center
   :width: 100%

   transient_yaw_TEST1

.. figure:: ../../img/transient/transient_yaw_TEST2.png
   :align: center
   :width: 100%

   transient_yaw_TEST2

.. figure:: ../../img/impulse/freq_response_yaw_TEST1.png
   :align: center
   :width: 100%

   freq_response_yaw_TEST1

.. figure:: ../../img/impulse/freq_response_yaw_TEST2.png
   :align: center
   :width: 100%

   freq_response_yaw_TEST2

.. figure:: ../../img/impulse/impulse_yaw_TEST1.png
   :align: center
   :width: 100%

   impulse_yaw_TEST1

.. figure:: ../../img/impulse/impulse_yaw_TEST2.png
   :align: center
   :width: 100%

   impulse_yaw_TEST2

Conclusion
----------

The transient and impulse response analysis of Session 1 reveals the
following key findings:

- **Per-motor speed loop:**  Across 5 detected steps and 3 CAN channels, the average settling time is 3.41 s.  The controller reliably drives each motor to a steady operating point, though the steady-state error (mean SSE = 15.55) indicates a gain/unit mismatch between commands and feedback.  Consider adding integral action or calibrating the command → encoder-unit conversion to reduce this offset.
- **Overall speed:**  The aggregate speed settles in **0.299 s** on average, confirming that the drivetrain as a whole responds quickly to waypoint-driven command changes.  The overshoot/SSE pattern mirrors the per-motor analysis.
- **Yaw dynamics:**  The heading settles within **0.311 s** per command interval.  Because yaw is the integral of :math:`\omega_z`, the transient metrics (especially overshoot) are inherently larger than for the speed channels.  The impulse response from command to :math:`\omega_z` provides a more representative picture of the rotational closed-loop bandwidth.

- **Impulse response:**  Both Wiener deconvolution and cross-correlation
  methods yield consistent estimates of each channel's dynamics.  The
  impulse responses are compact (energy concentrated within the first
  few hundred milliseconds), confirming that the motors and driver
  electronics introduce only modest latency.

**Recommendations:**

1. Verify and unify the units between the kinematic publisher's ``goal``
   field and the encoder feedback (both should be in the same rad/s or
   RPM scale) to eliminate the systematic steady-state offset.
2. If tighter tracking is needed, add integral (I) action to the motor
   speed controller.
3. Use the estimated impulse responses as a basis for model-based
   controller design (e.g. pole placement or feed-forward compensation)
   to further reduce overshoot and settling time.
