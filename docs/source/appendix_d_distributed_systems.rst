Appendix E: Distributed Systems
===============================

Overview
--------

A distributed system is a collection of independent processes that cooperate
via a network. Robotics stacks are inherently distributed, with sensors,
controllers, and user interfaces running on separate nodes.

Key challenges
--------------

Latency and jitter
^^^^^^^^^^^^^^^^^^

- Network delays vary over time.
- Control loops must tolerate nondeterministic timing.

Partial failures
^^^^^^^^^^^^^^^^

- Components can fail independently.
- Systems should degrade gracefully when nodes disconnect.

Consistency
^^^^^^^^^^^

- Shared state is hard to keep synchronized.
- Stale data can lead to incorrect decisions.

Time and ordering
-----------------

- Clocks drift between machines.
- Use timestamps and sequence numbers to detect ordering issues.

CAP tradeoff
------------

The CAP theorem highlights tradeoffs between consistency, availability, and
partition tolerance. Robotics systems often prioritize availability and timely
responses over strict consistency.

Patterns
--------

- Publish/subscribe for streaming state.
- Request/response for configuration.
- Heartbeats for liveness detection.

Applied to this project
-----------------------

Waypoint commands and odometry updates are exchanged over UDP, which trades
reliability for low latency. The app must tolerate packet loss and occasional
stale data while keeping the UI responsive.
