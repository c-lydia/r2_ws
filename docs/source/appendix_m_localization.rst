Appendix M: Localization
========================

Overview
--------

Localization estimates a robot's position and orientation in a global frame.
It combines motion models with sensor measurements.

Sources of localization
-----------------------

- Odometry: integrates wheel or motor motion.
- IMU: measures angular velocity and acceleration.
- Visual markers or lidar: provide absolute corrections.

Probabilistic view
------------------

State estimation often uses a probabilistic model:

.. math::

   x_k = f(x_{k-1}, u_k) + w_k
   z_k = h(x_k) + v_k

where $w_k$ and $v_k$ represent process and measurement noise.

Filters
-------

- Extended Kalman Filter (EKF): linearizes nonlinear models.
- Particle Filter: represents state as particles.

Frames
------

Common frames in robotics include:

- base_link: robot body.
- odom: local frame for short-term accuracy.
- map: global reference frame.

Applied to this system
----------------------

Odometry provides short-term pose estimates. For long-term accuracy, periodic
corrections can be applied using external references.
