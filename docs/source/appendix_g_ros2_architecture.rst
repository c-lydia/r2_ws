Appendix G: ROS2 Architecture
=============================

Introduction
------------

Modern robotic systems are inherently distributed, modular, and real-timeconstrained. Unlike traditional software, a robot is not a monolithic program; it is composed of sensors, algorithms, control loops, actuators, and supervisory components. Each of these components may operate:

- At different frequencies
- On different processors
- With different languages
- Across different machines

The immediate implication is that direct coupling of these components quickly becomes unmanageable. Simple mechanisms like shared memory or ad-hoc TCP sockets fail to scale and cannot guarantee correctness under timing constraints.

Robotics cannot be treates as standard software engineering because physical embodiment imposes temporal correctness requirements. Missing a deadline may not just degrade performance; it can compromise safety. Middleware in robotics is therefore not a convenience, bit a necessity.

The Robot Operating System (ROS) emerged to address these issues. ROS 1 provided modularity and message-oriented design but relied on a centralized master node, best-effort TCP transport, and had limited real-time capabilities. ROS 2 represents a re-conception of middleware, emphasizing distributes discovery, data-centric communication, deterministic-enabling design, and integrated security. This chapter builds from first principles to examine why ROS 2 is architectured the way it is, and critically analyzes its ability to support real-time robotic systems. 

Why robotics needs middleware
-----------------------------

The challenges of distributed robotics
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A UAV stabilization system illustrates the challenge: IMU sensors stream data at hundreds of herts, control loops compute corrections, and actuators apply forces - all in a slightly synchronized loop. Without middleware:

- Each node must know addresses and protcols of every other node
- Temporal guarantees must be manually ensured across heterogeneous platforms
- Scaling to multiple robots multiplies communication complexity

These challenges highlight that middleware must do more than "send messages". It must provide a structural framework to manage distribution =, temporal constraints, and modular evolution.

Core middleware functions
^^^^^^^^^^^^^^^^^^^^^^^^^

Middleware solves three foundational problems:

- **Discovery:** nodes must find each ither dynamicallt. Hardcoding endpoints is brittle and unscalable.
- **Communication:** nodes must exchange data reliably. ROS 1's TCP-based transport often relied on best-effort semantics, which can lead to message loss.
- **Decoupling:** components should evolve independently. Tight coupling increases development fragility and reduces reusability.

These functions are amplified by physical constraints - actuators cannot wait indefinitely, and sensors produce high-rate asynchronous streams. Middleware is thus both a communication substrate and an enabling technology for desterministic design.

Communication models in distributed systems
-------------------------------------------

Understanding ROS 2 requires understanding the choices of communication paradigms, because these choices have direct consequences for latency, scalability, and determinism. 

Shared memory
^^^^^^^^^^^^^

Mechanisms
~~~~~~~~~~

In shared memory systems, multiple processes map a portion of memory into their address space, allowing them to read and write the same memory directly. No message passing or serialization is required, which minimizes latency and CPU overhead. 

Why
~~~

- Low latency: memory access is orders of magnitude faster than network I/O
- Predictable timing: access times can often be bounded, making it suitable for hard real-time applications.

challenges
~~~~~~~~~~

- Concurrency hazards: multiple processes writing simultaneously can correupt data. Locks or atomic opertions are required, but they introduce blocking or priority inversion, which can compromize real-time behavior.
- Tight coupling: all processes must understand the memory layout. Changing a data structure requires updating all processes simultaneously. This reduces modularity, which is a key goal in robotics middleware.
- Limited scalability: shared memory only works on a single machine. modern robots often have heterogeneous processors or operate in multi-robot fleets, so shared memory alone is insufficient.

Shared memory is suitable for high-frequency, low-latency interactions on a single embedded board, such as passing IMU data to a flight controller. However, for inter-machine communication or modular software architecture, it is too fragile. ROS 2 abstracts these details via DDS, providing similar low-latency behavior where necessary but with safer distributed mechanisms.

Shared memory demonstrates a fundamental trade-off between latency and modularity, It is "fast but brittle," highlighting why middleware must balance efficientcy with robustness. 

Remote Procedure Calls (RPC)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mechanism
~~~~~~~~~

RPC allows one process to invoke a function in another process or machine as if it were local. The middleware handles network communication, serialization, and deserialization.

Why
~~~

- Calls are blocking and synchronous, which simplifies reasoning about program flow.
- Request-response semantics provide strong guarantees about correspondence between requests and responses.

Challenges
~~~~~~~~~~

- Blocking behavior: a high-frequency sensor loop cannot afford to block waiting for a remote service. At 400 Hz, even small network jitter can accumulate into missed deadlines.
- Tight coupling: the caller must know exactly which remote service to invoke. This reduces flexibility and makes system evolution difficult.
- Scalability limitations: in multi-robot systems, RPC requires point-to-point connections, which scale poorly as the number of nodes grows.

RPC works well for configuration or low-rate command messages. however, it is unsuitable for continuous high-rate sensor streams or real-time control loops.

RPC demonstrates the trade-off between simplicity and temporal decoupling. Synchronous semantics are easy to reason about, but they are incompatible with asynchronous streaming, which dominates robotics workloads.

Publish-Subscribe
^^^^^^^^^^^^^^^^^

Mechanism
~~~~~~~~~

Publish-subscribe decouples producers (publishers) from consumers (subscribers) via topics. Publishers post messages to topics without knowledge of who will read them. Subscribers listen to topics without knowledge of the publishers. The middleware handles delivery, buffering, and discovery.

Why
~~~

- Temporal decoupling: a high-frequency sensor can publish independently of how many subscribers exist or their processing rate.
- Modularity and scalability: new nodes can join dynamically without changing publishers. This is essential for multi-robot systems.
- QoS control: DDS allows policies for reliability, latency, and message history, enabling formal temporal reasoning.

Challenges
~~~~~~~~~~

- Timing variability: message delivery depends on network conditions, subscriber load, and middleware buffering.
- Ordering and consistency: messages may arrive out of order or be dropped depending on QoS settings.
- Analysis complexity: unlike RPC or shared memory, worst-case latency must be decomposed across middleware, OS, and hardware layers.

Publish-subscribe is aligned with robotics because sensor data is continuous and asynchronous. Flight controllers, motion planners, and logging systems can all operate independently while sharing the same topic streams. DDS adds data-centric semantics, where messages carry global system state, enabling automatic discovery and QoS enforcements.

Publish-subscribe represents the modern compromize between flexibility, modularity, and temporal control. It sacrifices some predictability in favor of scalability, decoupling, and multi-robot operation, but ROS 2 mitigates this via QoS, executors, and formal timing analysis.

Comparative discussion
^^^^^^^^^^^^^^^^^^^^^^

| Feature             | Shared Memory            | RPC                       | Publish–Subscribe           |
| ------------------- | ------------------------ | ------------------------- | --------------------------- |
| Latency             | Very low                 | Low–medium                | Medium                      |
| Determinism         | High (on single machine) | Moderate (network jitter) | Low–medium (depends on QoS) |
| Modularity          | Low                      | Medium                    | High                        |
| Scalability         | Poor                     | Limited                   | High                        |
| Temporal Decoupling | None                     | None                      | Yes                         |

- Shared memory optimizes latency but sacrifices modularity and scalability
- RPC simplifies reasoning for synchronous tasks but cannot handle high-rate streaming efficiently
- Publish-subscribe sacrifices some determinstic predictability but enables distributed, modular, and scalable systems, which is why ROS 2 builds on this model

The design of ROS 2 reflects a deliberate engineering compromise. Rather than optimizing for the lowest latency at the cost of system fragility, it prioritizes modularity, discoverability, and the ability to enforce temporal contracts via QoS, making it suitable for distributed real-time robotics.

Real-Time Systems: dterminsim and temporal correctness
------------------------------------------------------

In robotics, real-time behavior is not merely about being fast; it ia about temporal correctness. A system is correct if and only if outputs are delivered both logically correct and within required deadlines:

.. math::

    Coorectness = f(Logical-Output, Timing)

Why
^^^

Consider a UAV performing attitude stabilization. Its IMY streams acceleration and angular velocity data at 400 Hz, resulting is a 2.5 ms control period. The flight controller must compute actuator commands before the next sensor sample arrives. A delay of even a fraction of a millisecond may destabilize the vehicle. Similarly, an industrial robot arm that misses a motion command deadline may collide with nearby equipment.

Categories of real-time Systems
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Hard real-time: missing a deadline constitutes system failure. Examples include low-level motor control loops, UAV stabilization, and collision avoidance. The system must guarantee timing under all conditions.
- Soft real-time: occasional deadline misses degrade performance but are tolerated. Examples include telemetry logging, visualization, or high-level planning. Timing constraints exist but are less stringent.

Middleware mus enable the analysis and enforcement of temporal behavior. ROS 2 does not automatically provide hard real-time guarantees, but it offers mechanisms forr expressing temporal contracts and controlling execution, which are essential for building predictable robotic systems.

Real-time correctness emerges from the combined behavior of sensors, computation, middleware, OS scheduling, and actuators. Middleware alone cannot enforce timing, but it is critical for temporal reasoning, modularity, and predictability. Without it, reasonsing about worse-case latency becomes intractable in distributed robotic systems.

ROS 1 Limitations and motivation for ROS 2
------------------------------------------

While ROS 1 revolutionized robotics research, its architecture imposed fundamental limitations for distributed, real-time, and safety-critical systems.

centralized master node
^^^^^^^^^^^^^^^^^^^^^^^

ROS 1 relies on a single master node to manage:

- Node registration
- Topic and service discovery
- Parameter management

Problems
~~~~~~~~

- Single point of failure: if the master node crashes, all nodes lose the ability to discover neew nodes or communicate reliably
- Limited scalability: multi-robot deployments require additional configuration to avoid IP conflicts and manually manage connections

Centralizeation simplifies implementation for laboratory setups but reduces system robustness in real-world scenarios where nodes may be dynamically added or removed

For modern robotic applications, reliability and decentralized operation are essential, motivatong ROS 2's removal of the central master node.

TCP-Based transport and best-effort delivery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ROS 1 primarily uses TCP/IP for topic communication. While TCP ensures delivery in order, it introduces:

- **Variable latency:** retransmission and congestion control cause unpredictable delays
- **Head-of-line blocking:** slow network links can delay subsequent messages
- **Unsuitability for high-frequency streams:** at hundreds of Hz, TCP retransmission may cause deadlines to be missed

Best-effort delivery and TCP's inherent variability are incompatoble with hard real-time control loops. UDP offers lower latency but requires manual handling of reliability, ordering, and congestion. ROS 1's transport was not designed for predictab;e timing, limiting its use in prduction systems.

Limited real-time configurability
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ROS 1 lacks mechanisms to:

- Specify maximum acceptable latency for messages
- Monitor or enforce deadlines
- Control scheduling of callback execution

Developers must rely on ad-hoc solutions to approximate real-time behavior, often resulting in fragile systems that break under increased load or network variability.

Lack of integrated security
^^^^^^^^^^^^^^^^^^^^^^^^^^^

In ROS 1:

- Messages are transmitted without authentication or encryption
- Access control is absent

Modern robots often operate in networked environments where malicious or untrusted agents may interfere. ROS 1’s lack of security prevents safe deployment in multi-robot systems or industrial settings.

Motivation for ROS 2
^^^^^^^^^^^^^^^^^^^^

ROS 2 addresses these limitations by:

- Decentralizing discovery via DDS, eliminating the master node dependency
- Supporting multiple transport protocols with QoS policies to control reliability, latency, and deadlines
- Introducing explicit executors to control callback execution and scheduling
- Integrating DDS-Security, providing authentication, encryption, and access control

ROS 2 represents a re-foundation rather than an incremental improvement. Its architecture explicitly targets distributed, real-time, and secure robotics, enabling predictable temporal behavior, modularity, and scalability.

The evolution from ROS 1 to ROS 2 demonstrates a critical insight: robust, real-time robotic systems cannot rely on naive middleware assumptions. Instead, architectural mechanisms must enable predictability, observability, and temporal reasoning.

DDS and the Data-Centric paradigm
---------------------------------

At the core of ROS 2 lies the Data Distribution Service (DDS), a middleware standard originally designed for high-reliability distributed systems such as aerospace platforms, autonomous vehicles, air-traffic control infrastructure, and defense systems. DDS was standardized by the Object Management Group with the explicit goal of enabling scalable, fault-tolerant, real-time data exchange across distributed computing nodes.

The adoption of DDS represents one of the most fundamental architectural changes in ROS 2. Rather than building a custom communication layer—as ROS 1 did—ROS 2 leverages an existing industrial-grade middleware ecosystem. This decision reflects a deeper shift in philosophy: instead of focusing on process-to-process communication, the system focuses on data itself as the central abstraction.

In other words, ROS 2 communication is data-centric rather than connection-centric.

Connection-centric vs data-centric communication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Traditional distributed systems often adopt a connection-centric model. In such systems, communication is conceptualized as explicit interactions between endpoints. A node must know:

- which other node it communicates with
- how to reach that node
- what protocol the node expects

This model tightly couples components together.

ROS 1 followed this pattern. A publisher would advertise a topic through a central master node, subscribers would query the master, and then the nodes would establish direct transport connections. Communication therefore depended on explicit relationships between nodes.

DDS, by contrast, implements a data-centric publish–subscribe model.

In this paradigm:

- Communication revolves around data topics, not node identities.
- Nodes declare intentions about the data they produce or consume.
- The middleware automatically discovers matching publishers and subscribers.

This shift changes how developers conceptualize distributed robotics systems. Instead of asking:

.. note::

    Which node should I send this information to?

the system asks:

.. note::

    What information should exist in the global data space?

Nodes then interact with that shared information space through topics.

Core DDS Concepts
^^^^^^^^^^^^^^^^^

DDS defines a set of core abstractions that structure communication.

Domain 
~~~~~~

A domain represents a logical communication environment. Nodes that belong to the same DDS domain can automatically discover each other and exchange data. Domains therefore act as isolation boundaries, allowing multiple independent robotic systems to operate on the same network without interference.

For example:

- A warehouse fleet of robots may operate within domain 0
- A testing environment may use domain 1

Nodes from different domains will not communicate unless explicitly bridged.

Topic
~~~~~

A topic represents a named channel for structured data.

Each topic is defined by:

- a name
- a data type

Topics serve as the primary mechanism for decoupling system components. Publishers write data to topics, while subscribers read from them.

Example topics in a robotic system may include:

- ``/imu/data``
- ``/camera/image``
- ``/robot_pose``
- ``/cmd_vel``

Importantly, nodes do not need to know who produces or consumes the topic.

Publisher and DataWriter
~~~~~~~~~~~~~~~~~~~~~~~~

A publisher is responsible for sending data into the DDS system. Internally, DDS represents this functionality through a DataWriter entity, which manages message transmission and reliability policies.

The DataWriter handles tasks such as:

- serialization of data structures
- scheduling message transmission
- applying Quality of Service (QoS) policies

From the perspective of a ROS 2 developer, publishing a message simply means writing data to a topic, while DDS manages the underlying communication complexities.

Subscriber and DataReader
~~~~~~~~~~~~~~~~~~~~~~~~~

A subscriber receives data from topics through an internal DDS component called a DataReader.

The DataReader:

- monitors the topic for incoming data
- buffers messages according to QoS rules
- delivers data to the application layer

Subscribers therefore interact with data streams, rather than with specific publishers.

Automatic discovery
^^^^^^^^^^^^^^^^^^^

One of the most powerful features of DDS is automatic participant discovery.

When a DDS node starts, it broadcasts its presence to other nodes on the network. Through a discovery protocol, nodes exchange metadata describing:

- the topics they publish
- the topics they subscribe to
- their Quality of Service requirements

The middleware then automatically establishes the required communication pathways.

This mechanism eliminates the need for a centralized registry, such as the ROS 1 master node.

The implications are significant:

- No single point of failure
- Dynamic system composition
- Plug-and-play robotics components

For instance, if a new sensor node is added to a robot, other nodes that subscribe to its topic will automatically begin receiving data without configuration changes.

Quality of Service (QoS) policies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DDS communication behavior is controlled through Quality of Service policies, which define the semantics of data delivery.

These policies enable developers to specify communication contracts between publishers and subscribers.

Key QoS parameters include:

Reliability
~~~~~~~~~~~

Defines whether message delivery must be guaranteed.

Two modes exist:

- Reliable: ensures all messages reach subscribers, potentially retransmitting lost packets.
- Best effort: prioritizes low latency, allowing message loss.

In robotics, reliability choices depend on application context. High-rate sensor streams may use best-effort delivery, while mission-critical commands may require reliability.

Durability
~~~~~~~~~~

Durability determines whether data should persist for late-joining subscribers.

For example:

- Transient local durability allows new subscribers to receive previously published messages.
- Volatile durability only delivers data published after subscription.

This feature is useful for state topics, where new nodes must immediately obtain the current system state.

History and depth
~~~~~~~~~~~~~~~~~

These parameters control how many past messages are stored.

For high-frequency sensors, keeping only the most recent sample prevents buffer growth and reduces latency. Conversely, logging systems may require larger histories.

Deadline
~~~~~~~~

The deadline QoS defines the maximum allowed interval between consecutive messages.

If the publisher fails to meet this deadline, DDS generates a notification event. This mechanism enables monitoring of temporal contracts within the communication system.

Liveliness
~~~~~~~~~~

Liveliness policies detect whether a publisher is still active.

If a publisher stops transmitting data, subscribers can detect the failure and trigger recovery mechanisms.

Data lifecycle and memory management
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DDS treats data as stateful objects with lifecycles rather than simple messages. Each data instance is tracked across the system, allowing DDS to manage:

- data creation
- updates
- deletion
- persistence

This design enables more advanced behaviors such as state synchronization and distributed caching.

For robotics applications, this capability is valuable because many topics represent system state rather than transient events.

Examples include:

- robot pose
- map data
- battery status

By maintaining state awareness, DDS enables subscribers to quickly reconstruct the system state even after temporary disconnections.

Transport abstraction
^^^^^^^^^^^^^^^^^^^^^

DDS abstracts the underlying network transport layer. Depending on the implementation and configuration, data may be transmitted via:

- shared memory (within a single machine)
- UDP
- TCP
- specialized real-time transports

This abstraction allows DDS to optimize communication depending on the deployment environment.

For example:

- nodes running on the same computer may exchange data via zero-copy shared memory, minimizing latency
- nodes on separate machines may use UDP multicast for efficient broadcast communication

Such flexibility is essential for modern robotics systems, which often combine embedded processors, onboard computers, and cloud infrastructure.

Scalability and multi-robot systems
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A major advantage of DDS is its ability to support large distributed systems.

Because communication is topic-based and discovery is decentralized, adding new nodes does not increase configuration complexity. This property is critical for:

- multi-robot fleets
- swarm robotics
- distributed sensor networks

For instance, in a swarm of aerial drones performing environmental monitoring, each drone may publish telemetry data to a shared topic. Ground stations and analysis nodes can subscribe to this topic without requiring explicit knowledge of every drone.

As the swarm grows, the communication architecture remains unchanged.

Limitations and challenges
^^^^^^^^^^^^^^^^^^^^^^^^^^

Despite its advantages, DDS introduces several complexities.

Configuration Complexity
~~~~~~~~~~~~~~~~~~~~~~~~

DDS offers a large number of QoS parameters. While powerful, this flexibility increases the difficulty of system configuration. Misconfigured QoS settings can lead to communication incompatibilities or performance issues.

Non-deterministic network behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DDS improves reliability and observability but cannot eliminate network variability. Latency, packet loss, and congestion may still affect communication timing.

Therefore, developers must combine DDS with:

- real-time operating systems
- careful executor design
- deterministic memory management

Implementation variability
~~~~~~~~~~~~~~~~~~~~~~~~~~

Multiple DDS implementations exist, each with different performance characteristics and feature sets. ROS 2 can operate on several DDS backends, including those developed by companies such as RTI, eProsima, and Eclipse Foundation.

While this flexibility is beneficial, it also means that system performance may vary depending on the selected implementation.

Implications for ROS 2 system design
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The integration of DDS fundamentally changes how robotic software systems are architected.

Key implications include:

Decentralization
~~~~~~~~~~~~~~~~

The elimination of the ROS 1 master node improves fault tolerance and system robustness.

Temporal observability
~~~~~~~~~~~~~~~~~~~~~~

QoS policies allow developers to monitor communication timing and detect deadline violations.

Scalable distributed architectures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DDS enables robotic systems to grow from single robots to large fleets without redesigning the communication infrastructure.

Improved modularity
~~~~~~~~~~~~~~~~~~~

Nodes interact through shared data abstractions rather than direct dependencies.

Conceptual significance
^^^^^^^^^^^^^^^^^^^^^^^

Perhaps the most important impact of DDS is conceptual rather than technical.

Robotic software development shifts from a process-oriented mindset to a data-oriented mindset.

Instead of designing systems around which components communicate with each other, developers design systems around information flows and data streams.

This shift aligns naturally with the structure of robotic systems, where behavior emerges from continuous streams of sensor data, state estimation, planning outputs, and control commands.

DDS therefore provides the architectural foundation for scalable, distributed, and temporally analyzable robotic systems, which is precisely the goal of modern robotic middleware such as ROS 2.

