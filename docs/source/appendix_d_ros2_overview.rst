Appendix D: ROS2 Overview
=========================

What is ROS2
------------

ROS2 (Robot Operating System 2) is a middleware framework for building robot
applications. It provides communication, tools, and libraries for composing
complex robot systems from modular nodes.

Key concepts
------------

Nodes
^^^^^

- Independent processes that perform specific tasks.
- Nodes communicate via topics, services, and actions.

Topics
^^^^^^

- Publish/subscribe channels for streaming data.
- Designed for high-frequency sensor and state updates.

Services
^^^^^^^^

- Synchronous request/response interactions.
- Used for operations like configuration or queries.

Actions
^^^^^^^

- Long-running goals with feedback and cancellation.
- Suitable for navigation and planning tasks.

Parameters
^^^^^^^^^^

- Runtime configuration values stored on nodes.
- Can be read and set externally.

QoS (Quality of Service)
------------------------

ROS2 exposes DDS QoS settings like reliability, durability, and history depth.
Selecting the right QoS is critical in lossy networks or real-time systems.

Packages and workspaces
-----------------------

- A package is a unit of build and deployment.
- A workspace contains multiple packages and their build artifacts.

Lifecycle management
--------------------

ROS2 supports managed nodes with lifecycle states (unconfigured, inactive,
active, finalized). This helps bring up systems in a predictable order.

Why ROS2 for robotics
---------------------

- Scalable communication infrastructure.
- Tooling for visualization and debugging.
- Large ecosystem of drivers and algorithms.
