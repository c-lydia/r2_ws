Appendix H: UDP
===============

Overview
--------

User Datagram Protocol (UDP) is a connectionless transport protocol that sends
independent datagrams. It is fast and lightweight but provides no delivery or
ordering guarantees.

Characteristics
---------------

- Connectionless and stateless.
- Packets can be dropped, duplicated, or reordered.
- Lower overhead than TCP.

Packet size and MTU
-------------------

UDP payloads that exceed the path MTU may be fragmented, which increases loss
risk. Design packet formats to be compact and avoid fragmentation where
possible.

Checksums
---------

UDP includes a checksum for error detection but no retransmission. Applications
must decide whether to drop or tolerate corrupted packets.

Best practices for control systems
----------------------------------

- Include sequence numbers or plan IDs to identify stale data.
- Use fixed-size binary formats for consistent parsing.
- Keep send rates bounded to avoid congestion.
- For critical commands, consider sending multiple times or adding acknowledgments.

Applied to target setting
-------------------------

The waypoint protocol favors low latency and simplicity. The app can tolerate
occasional packet loss while maintaining responsiveness.
