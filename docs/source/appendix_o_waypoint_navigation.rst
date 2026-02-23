Appendix O: Waypoint Navigation
===============================

Overview
--------

Waypoint navigation drives a robot through a sequence of target positions.
Key components include path planning, control, and arrival detection.

Path planning
-------------

- For sparse waypoints, straight-line segments are common.
- For smoother trajectories, use splines or polynomial paths.

Arrival detection
-----------------

A waypoint is considered reached when distance and timing constraints are met:

.. math::

   \text{dist} = \sqrt{(x_t - x)^2 + (y_t - y)^2}

If dist is below a tolerance for a specified duration, the waypoint is complete.

Handling edits
--------------

When waypoints are edited, smoothing can reduce abrupt changes in command
velocity. A simple low-pass update is:

.. math::

   x_{new} = (1 - \alpha) x_{old} + \alpha x_{update}

Return behavior
---------------

Visited waypoints can be stored in a stack to support a return-to-base function.

Applied to this system
----------------------

The app sends waypoint lists and updates to the robot. The controller processes
the queue, updates the active target, and transitions between states.
