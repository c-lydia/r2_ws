Impulse & Frequency Response
============================

Objective
---------

Estimate the system-level transfer function from controller commands to
measured robot response, and characterise the plant gain and bandwidth.

Method
------

Because motor-level speed feedback is zero throughout Session 2 (see
:doc:`motor_speed`), per-motor impulse response cannot be computed.
Instead, a **system-level** analysis is performed using signals that are
actually non-zero:

* **:math:`\omega_z` channel**: :math:`\omega_z` command (controller) →
  yaw rate :math:`\dot{\psi}` (derived from UDP odom yaw).
* **:math:`V_y` channel**: :math:`V_y` command → :math:`\dot{y}` (derived
  from UDP odom :math:`y` position).

This treats the entire robot (motors + kinematics + environment) as a SISO
system.  The impulse response :math:`h[n]` is estimated via **Wiener
deconvolution**:

.. math::

   H(f) = \frac{S_{uy}(f)}{S_{uu}(f) + \varepsilon}

where :math:`S_{uy}` is the cross-spectral density between input :math:`u`
and output :math:`y`, :math:`S_{uu}` is the input auto-spectral density, and
:math:`\varepsilon` is a regularisation constant to suppress noise
amplification.

:math:`\omega_z \to` Yaw Rate
------------------------------

TEST 1
~~~~~~

.. figure:: ../../img/impulse/impulse_wz_yaw_TEST1.png
   :width: 100%
   :align: center

   Impulse response: :math:`\omega_z` command → yaw rate — TEST 1.

.. figure:: ../../img/impulse/freq_response_wz_TEST1.png
   :width: 100%
   :align: center

   Frequency response (magnitude): :math:`\omega_z \to \dot{\psi}` — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/impulse/impulse_wz_yaw_TEST2.png
   :width: 100%
   :align: center

   Impulse response: :math:`\omega_z \to \dot{\psi}` — TEST 2.

.. figure:: ../../img/impulse/freq_response_wz_TEST2.png
   :width: 100%
   :align: center

   Frequency response: :math:`\omega_z \to \dot{\psi}` — TEST 2.

:math:`V_y \to \dot{y}`
------------------------

TEST 1
~~~~~~

.. figure:: ../../img/impulse/impulse_vy_y_TEST1.png
   :width: 100%
   :align: center

   Impulse response: :math:`V_y` command → :math:`\dot{y}` — TEST 1.

.. figure:: ../../img/impulse/freq_response_vy_TEST1.png
   :width: 100%
   :align: center

   Frequency response: :math:`V_y \to \dot{y}` — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/impulse/impulse_vy_y_TEST2.png
   :width: 100%
   :align: center

   Impulse response: :math:`V_y \to \dot{y}` — TEST 2.

.. figure:: ../../img/impulse/freq_response_vy_TEST2.png
   :width: 100%
   :align: center

   Frequency response: :math:`V_y \to \dot{y}` — TEST 2.

Key Metrics
-----------

.. list-table:: Impulse Response Metrics
   :header-rows: 1
   :widths: 12 22 18 18

   * - Test
     - Channel
     - Peak Lag (s)
     - Peak Value
   * - TEST 1
     - :math:`\omega_z \to \dot{\psi}`
     - 0.0
     - −0.125
   * - TEST 2
     - :math:`\omega_z \to \dot{\psi}`
     - 0.0
     - −0.125

**Peak lag = 0.0 s** means the system responds instantaneously within the
sampling resolution (~100 ms).  The **negative peak value** (~−0.125)
indicates sign inversion: a positive :math:`\omega_z` command produces a
negative yaw rate, which may reflect a sign convention mismatch in the
kinematic transform or an actual reverse-rotation behaviour.

Interpretation
--------------

1. **Plant gain ≈ 0.125** — only 12.5 % of the commanded angular velocity
   appears in the measured yaw rate.  For a theoretically ideal system the
   gain should be 1.0, so the effective system is attenuated by **−18 dB**.

2. **Low-pass characteristic** — the frequency response rolls off above
   ~0.5 Hz, with most energy concentrated below 0.1 Hz.  This is consistent
   with a system dominated by inertia and friction rather than active motor
   tracking.

3. **Flat impulse at lag 0** — instead of the expected decaying exponential
   (first-order plant) or damped oscillation (second-order), the impulse is
   essentially a Dirac delta scaled by 0.125.  This means there is no dynamic
   coupling — the small observed yaw change is proportional to the command but
   not mediated by motor action.

.. math::

   \hat{h}[n] \approx -0.125 \cdot \delta[n]

This is consistent with a system where external forces (ground friction
asymmetry, cable drag) weakly couple the chassis to the commanded rotation
rather than the motors actively driving it.

Key Findings
------------

1. **System gain is 0.125** — the robot executes only ~12.5 % of
   commanded :math:`\omega_z`, confirming severe motor underperformance.
2. **Zero lag** — no dynamic response; the coupling is instantaneous and
   purely proportional.
3. **Sign inversion** — positive commands yield negative yaw rate; a sign
   error in the kinematic pipeline should be investigated.
4. The frequency response is essentially flat below 0.5 Hz, ruling out
   resonance effects.

.. seealso::

   :doc:`yaw_analysis` — Time-domain yaw behaviour that these metrics
   summarise.

   :doc:`transient_response` — Motor-level (goal vs position) transient
   analysis.

   :doc:`stability_analysis` — PSD of the command signals.
