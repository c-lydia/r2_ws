Appendix F: Real Time System And Middleware
===========================================

Layered structure
-----------------

ROS2 is built as a stack of layers:

- Client libraries: rclcpp (C++), rclpy (Python)
- ROS client library: rcl
- Middleware interface: rmw
- DDS implementation: Fast DDS, Cyclone DDS, or Connext

Executors
---------

Executors schedule callbacks for subscriptions, timers, and services. Common
executors include single-threaded and multi-threaded variants. Callback groups
control concurrency and prevent data races.

Composition
-----------

ROS2 supports composable nodes that run in a single process. This reduces
overhead and improves performance when nodes are tightly coupled.

Lifecycle nodes
---------------

Lifecycle nodes provide deterministic startup and shutdown behavior. They move
through states like unconfigured, inactive, active, and finalized.

DDS details
-----------

DDS handles discovery, serialization, and transport. QoS policies determine how
data is delivered and what guarantees are provided.

Best practices
--------------

- Choose QoS profiles based on network conditions.
- Use namespaces to keep large systems organized.
- Keep topics small and publish at stable rates.
