Timing Analysis
===============

Objective
---------

Evaluate the real-time scheduling quality of each ROS 2 message stream by
measuring inter-message jitter.  Excessive jitter can degrade control
performance even when the control algorithm itself is correct.

Method
------

For each message stream, the inter-arrival time
:math:`\Delta t_k = t_{k} - t_{k-1}` is computed for all consecutive pairs.
Three summary statistics are reported:

.. list-table::
   :header-rows: 1
   :widths: 20 50

   * - Metric
     - Definition
   * - Median :math:`\Delta t`
     - Typical gap — corresponds to the nominal publishing rate
   * - Std :math:`\Delta t`
     - Jitter magnitude — how much individual gaps deviate
   * - Max :math:`\Delta t`
     - Worst-case latency — the single longest gap observed

Jitter Distributions
--------------------

TEST 1
~~~~~~

.. figure:: ../../img/timing/timing_jitter_TEST1.png
   :width: 100%
   :align: center

   Inter-message jitter distribution for all topics — TEST 1.

TEST 2
~~~~~~

.. figure:: ../../img/timing/timing_jitter_TEST2.png
   :width: 100%
   :align: center

   Inter-message jitter distribution — TEST 2.

Timing Summary
--------------

.. list-table:: Timing Jitter — TEST 1
   :header-rows: 1
   :widths: 28 14 14 14

   * - Topic
     - Median (ms)
     - Std (ms)
     - Max (ms)
   * - ``ctrl_cmd`` (:math:`V_x / V_y / \omega_z`)
     - 100
     - 0.7
     - ~105
   * - ``udp_odom`` (:math:`x / y / \psi`)
     - 117
     - 309
     - **6 800**
   * - ``motor_cmd`` (goals)
     - 25
     - 40
     - ~300
   * - ``odom_pub`` (velocity)
     - 5.8
     - 1.3
     - ~12

.. list-table:: Timing Jitter — TEST 2
   :header-rows: 1
   :widths: 28 14 14 14

   * - Topic
     - Median (ms)
     - Std (ms)
     - Max (ms)
   * - ``ctrl_cmd``
     - ~100
     - ~1
     - ~105
   * - ``udp_odom``
     - ~100
     - ~50
     - ~500
   * - ``motor_cmd``
     - ~25
     - ~15
     - ~100
   * - ``odom_pub``
     - ~6
     - ~1
     - ~12

Interpretation
--------------

**Controller commands** (``ctrl_cmd``)
    Run at almost exactly 10 Hz with sub-millisecond jitter — the most
    deterministic stream in the system.  The ROS 2 timer is delivering
    consistent scheduling.

**Motor commands** (``motor_cmd``)
    Run at ~40 Hz (25 ms median) but with higher relative jitter (std =
    40 ms in TEST 1).  The large std indicates **bursty scheduling** — the
    ``inverse_kinematic`` node sometimes publishes multiple messages in rapid
    succession followed by a pause.  This may be caused by the four CAN
    channels being published sequentially within one timer callback.

**UDP odom** (``udp_odom``)
    Shows a large outlier in TEST 1 — one gap of **~6.8 s** (68× the
    nominal interval).  This is likely a network dropout or UDP packet loss
    event.  Outside this outlier, UDP odom runs at ~8.5 Hz (117 ms).

    .. warning::

       A 6.8 s gap in position feedback means the controller is operating
       with stale state for nearly 7 seconds.  If odometry were used for
       closed-loop control, this would cause significant control degradation.

    TEST 2 has much better UDP timing (max ~500 ms), suggesting the network
    issue was transient.

**Odometry publish** (``odom_pub``)
    The fastest stream at ~170 Hz (5.8 ms median) with tight jitter.
    However, since the published velocity is always :math:`(0.0,\,0.0)`,
    this high rate is **wasted bandwidth** — it could be reduced to 10 Hz
    without information loss.

Key Findings
------------

1. **Controller timing is excellent** — 10 Hz ± 0.7 ms, meeting real-time
   requirements.
2. **Motor command scheduling is bursty** — std/median ratio > 1.0 in
   TEST 1; consider rate-limiting the CAN publisher.
3. **UDP has a single 6.8 s dropout** in TEST 1 — root cause should be
   investigated (network interface, buffer overflow, or ROS executor
   starvation).
4. **Odometry publishes at 170 Hz** but carries no useful data — bandwidth
   can be reclaimed.

.. seealso::

   :doc:`velocity_components` — The controller commands whose timing is
   analysed here.

   :doc:`motor_cmd` — Motor goals with bursty scheduling characteristics.

   :doc:`conclusion` — Summary of all identified issues.
