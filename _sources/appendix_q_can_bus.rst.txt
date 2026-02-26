Appendix Q: CAN Bus
===================

Overview
--------

Controller Area Network (CAN) is a robust bus protocol used in automotive and
robotic systems for reliable device communication.

Frame structure
---------------

- Identifier: arbitration and message priority.
- Data length: number of bytes (0 to 8 for classic CAN).
- Data: payload bytes.
- CRC: error detection.

Arbitration
-----------

CAN uses non-destructive bitwise arbitration. The lowest identifier wins bus
access without corrupting messages.

Bitrate and timing
------------------

All nodes must share the same bitrate and timing parameters. Mismatched timing
causes errors and bus-off states.

Error handling
--------------

CAN includes error counters and automatic retransmission. Persistent errors
can place a node into a bus-off state until recovery.

Classic CAN vs CAN FD
---------------------

- Classic CAN: 8-byte payload limit.
- CAN FD: larger payload and higher data phase bitrate.

Applied to robotics
-------------------

CAN is often used for motor controllers and sensor modules that require robust
communication in noisy electrical environments.
