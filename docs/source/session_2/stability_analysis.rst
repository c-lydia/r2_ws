Stability Analysis
==================

Objective
---------

Assess whether the controller velocity commands are **stationary** — i.e.
whether they remain consistent over time or exhibit drift, oscillation, or
sudden regime changes that could indicate control instability.

Method
------

Two complementary techniques are applied to the velocity command signals
:math:`V_x`, :math:`V_y`, and :math:`\omega_z`:

1. **Rolling statistics** — a 2 s sliding window computes the local mean and
   standard deviation.  If the envelope (mean ± 1σ) is tight and slowly
   varying, the signal is quasi-stationary.

2. **Power Spectral Density (PSD)** — estimated via Welch's method.  Narrow
   peaks indicate dominant oscillation frequencies; a flat spectrum indicates
   white noise.

.. math::

   S_{xx}(f) = \frac{1}{N}\left|\sum_{n=0}^{N-1} x[n]\, e^{-j 2\pi f n / N}\right|^2

:math:`V_x` Stability
-----------------------

TEST 1
~~~~~~

.. figure:: ../../img/overall_stability/stability_vx_TEST1.png
   :width: 100%
   :align: center

   :math:`V_x` rolling mean ± 1σ — TEST 1.

.. figure:: ../../img/overall_stability/psd_vx_TEST1.png
   :width: 90%
   :align: center

   PSD of :math:`V_x` — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/overall_stability/stability_vx_TEST2.png
   :width: 100%
   :align: center

   :math:`V_x` rolling mean ± 1σ — TEST 2.

.. figure:: ../../img/overall_stability/psd_vx_TEST2.png
   :width: 90%
   :align: center

   PSD of :math:`V_x` — TEST 2.

:math:`V_y` Stability
-----------------------

TEST 1
~~~~~~

.. figure:: ../../img/overall_stability/stability_vy_TEST1.png
   :width: 100%
   :align: center

   :math:`V_y` rolling mean ± 1σ — TEST 1.

.. figure:: ../../img/overall_stability/psd_vy_TEST1.png
   :width: 90%
   :align: center

   PSD of :math:`V_y` — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/overall_stability/stability_vy_TEST2.png
   :width: 100%
   :align: center

   :math:`V_y` rolling mean ± 1σ — TEST 2.

.. figure:: ../../img/overall_stability/psd_vy_TEST2.png
   :width: 90%
   :align: center

   PSD of :math:`V_y` — TEST 2.

:math:`\omega_z` Stability
----------------------------

TEST 1
~~~~~~

.. figure:: ../../img/overall_stability/stability_wz_TEST1.png
   :width: 100%
   :align: center

   :math:`\omega_z` rolling mean ± 1σ — TEST 1.

.. figure:: ../../img/overall_stability/psd_wz_TEST1.png
   :width: 90%
   :align: center

   PSD of :math:`\omega_z` — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/overall_stability/stability_wz_TEST2.png
   :width: 100%
   :align: center

   :math:`\omega_z` rolling mean ± 1σ — TEST 2.

.. figure:: ../../img/overall_stability/psd_wz_TEST2.png
   :width: 90%
   :align: center

   PSD of :math:`\omega_z` — TEST 2.

Summary Table
-------------

.. list-table:: Dominant Frequencies (Hz)
   :header-rows: 1
   :widths: 15 15 15 15

   * - Test
     - :math:`V_x`
     - :math:`V_y`
     - :math:`\omega_z`
   * - TEST 1
     - 0.031
     - 0.031
     - 0.062
   * - TEST 2
     - 0.030
     - 0.030
     - 0.030

Interpretation
--------------

**Observations:**

* All three command signals exhibit very-low-frequency dominant content
  (≤ 0.06 Hz), corresponding to slow drift over periods of 16–32 s.  This is
  consistent with a navigation controller that smoothly adjusts heading and
  velocity as it approaches successive waypoints.

* The rolling standard deviation stays small relative to the mean throughout
  both tests, confirming the commands are **quasi-stationary** — no abrupt
  mode changes, no oscillatory instabilities, and no saturation events.

* In TEST 1, :math:`\omega_z` has a dominant frequency of **0.062 Hz**
  (period ≈ 16 s), roughly twice the :math:`V_x`/:math:`V_y` frequency.
  This suggests the heading-correction loop updates faster than the
  translational controller — potentially because the P-controller for yaw
  has a higher gain or responds more aggressively to heading error.

* In TEST 2, all three channels converge to ~0.030 Hz (period ≈ 33 s),
  indicating the controller has settled into a single, low-bandwidth
  regulation mode.

Key Findings
------------

1. **No oscillatory instability** — the PSD shows no narrow-band peaks above
   0.1 Hz, ruling out limit-cycle or resonant behaviour.
2. **Quasi-stationary commands** — the rolling σ/mean ratio is small,
   confirming the controller is not chattering or mode-switching.
3. **Heading loop is 2× faster in TEST 1** (0.062 vs 0.031 Hz) — this may
   explain the curved trajectory observed in :doc:`navigation_analysis`.
4. **TEST 2 is the most stable** configuration — all signals at 0.030 Hz
   with very low variance.

.. seealso::

   :doc:`velocity_components` — The raw :math:`V_x`, :math:`V_y`,
   :math:`\omega_z` time series.

   :doc:`yaw_analysis` — Stability of the actual yaw response.

   :doc:`overall_speed` — Per-test speed stability plots.
