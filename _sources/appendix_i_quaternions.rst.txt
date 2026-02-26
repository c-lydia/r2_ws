Appendix I: Quaternions
=======================

Overview
--------

Quaternions represent 3D rotations without gimbal lock. A quaternion is written
as $q = (w, x, y, z)$ where $w$ is the scalar component and $(x, y, z)$ is the
vector component.

Unit quaternions
----------------

A rotation quaternion is unit length:

.. math::

   \|q\| = \sqrt{w^2 + x^2 + y^2 + z^2} = 1

Quaternion multiplication
-------------------------

Combining rotations uses quaternion multiplication, which is not commutative.
If $q_1$ and $q_2$ are rotations, the composed rotation is $q = q_2 \otimes q_1$.

Axis-angle conversion
---------------------

For rotation angle $\theta$ around unit axis $\hat{u}$:

.. math::

   q = \left(\cos(\theta/2),\ \hat{u}_x\sin(\theta/2),\ \hat{u}_y\sin(\theta/2),\ \hat{u}_z\sin(\theta/2)\right)

Yaw extraction (2D robots)
--------------------------

For planar motion, yaw can be extracted from a quaternion:

.. math::

   \text{yaw} = \arctan2(2(wz + xy),\ 1 - 2(y^2 + z^2))

Numerical stability
-------------------

- Normalize quaternions after integration.
- Avoid repeated small-angle conversions without renormalization.

Applied to odometry
-------------------

Yaw is computed from quaternion orientation and then used in frame transforms
for velocities and positions.
