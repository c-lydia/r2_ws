Appendix P: Complementary Filtering
===================================

Overview
--------

A complementary filter combines two signals with different frequency qualities.
One signal provides good low-frequency behavior, the other provides high-frequency
response. The sum provides a balanced estimate.

Basic equation
--------------

.. math::

   y = \alpha y_{fast} + (1 - \alpha) y_{slow}

where $0 < \alpha < 1$.

Why it works
------------

- The low-pass component reduces noise and drift.
- The high-pass component preserves responsiveness.

Discrete implementation
-----------------------

.. code-block:: python

   filtered = alpha * new_value + (1 - alpha) * previous_filtered

Applied to derivative terms
---------------------------

Derivative signals are noisy. A complementary filter can smooth the derivative
term in a PD or PID controller, improving stability without a large delay.

Applied to waypoint updates
---------------------------

When target updates occur mid-motion, filtering avoids sudden jumps in desired
position and keeps the control output smooth.
