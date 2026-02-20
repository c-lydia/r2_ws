Appendix J: Kinematics
======================

Overview
--------

Kinematics describes the relationship between motion variables without
considering forces. For robots, this links wheel velocities to body motion.

Forward kinematics
------------------

Given wheel speeds, compute body velocities. For a holonomic robot, the
relationship can be expressed as:

.. math::

   \mathbf{v} = \mathbf{J} \cdot \mathbf{\omega}

where $\mathbf{J}$ is the kinematic matrix and $\mathbf{\omega}$ are wheel rates.

Inverse kinematics
------------------

Given desired body velocities, compute wheel speeds:

.. math::

   \mathbf{\omega} = \mathbf{J}^{-1} \cdot \mathbf{v}

If $\mathbf{J}$ is not square, a pseudoinverse is used.

Coordinate frames
-----------------

- Local frame: attached to the robot body.
- Global frame: fixed to the environment or map.

Transform between frames using rotation matrices derived from yaw.

Discretization
--------------

Velocities are integrated over time to compute position:

.. math::

   x_{k+1} = x_k + v_x \Delta t

and similarly for $y$ and $\theta$.

Applied to this system
----------------------

The kinematic model converts desired planar velocities into wheel velocities
and back into odometry updates.
