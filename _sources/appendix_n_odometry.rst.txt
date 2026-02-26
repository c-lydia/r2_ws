Appendix N: Odometry
====================

Overview
--------

Odometry estimates robot motion by integrating velocity over time. It is fast
and local but accumulates drift due to wheel slip and noise.

Kinematic integration
---------------------

Given linear velocities in the global frame:

.. math::

   x_{k+1} = x_k + v_x \Delta t
   y_{k+1} = y_k + v_y \Delta t

Yaw integration uses angular velocity:

.. math::

   \theta_{k+1} = \theta_k + \omega_z \Delta t

Error sources
-------------

- Wheel slip or uneven terrain.
- Encoder quantization.
- Incorrect wheel radius or geometry parameters.

Mitigation
----------

- Periodic calibration of wheel parameters.
- Fusing odometry with IMU or external sensors.
- Avoiding long open-loop runs without correction.

Applied to this project
-----------------------

Odometry is derived from motor velocities and transformed into the global frame
for display and control.
