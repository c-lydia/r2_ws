Appendix L: PID Control
=======================

Overview
--------

PID control combines proportional, integral, and derivative terms to reduce
error between a desired value and the measured value.

PID equation
------------

.. math::

   u(t) = K_p e(t) + K_i \int_0^t e(\tau) d\tau + K_d \frac{de(t)}{dt}

Discrete form
-------------

.. math::

   u_k = K_p e_k + K_i \sum_{i=0}^k e_i \Delta t + K_d \frac{e_k - e_{k-1}}{\Delta t}

Tuning
------

- $K_p$ sets responsiveness but can overshoot.
- $K_i$ removes steady-state error but can wind up.
- $K_d$ dampens oscillation but amplifies noise.

Anti-windup
-----------

Clamp the integral term when actuators saturate:

.. math::

   I_k = \text{clamp}(I_k, I_{min}, I_{max})

Filtering
---------

Derivative terms often use low-pass filtering to reduce noise.

Applied to robot motion
-----------------------

The controller uses PD components on position and yaw with filtered derivative
terms for smoother navigation.
