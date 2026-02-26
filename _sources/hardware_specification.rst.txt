Hardware Specification
======================

This section outlines the hardware components and specifications for the mobile robot platform used in this project. The hardware selection is based on the requirements for waypoint navigation, odometry estimation, and client-server communication with an Android application.

Robot platform
--------------

- **Type:** omnidirectional mobile robot with mecanum wheels (holonomic motion)
- **Dimensions:** 0.5 m x 0.5 m x 0.3 m (approximately) 

Sensors
-------

The robot is equipped with 4 independent DC motors, driving 4 mecanum wheels with encoders attached for feedback. To compenstate for yaw estimation, an IMU (Inertial Measurement Unit) is included, providing angular velocity and linear acceleration data. 

Drive system
------------

- **Motors:** 4 DC motors, each driving on mecanum wheel
- **Motor specifications:** 24 V, 200 W max, integrated encoders
- **Motor drivers:** custom-built smart driver boards, each supporting 2 motors
- **Wheel type:** mecanum 0.06 radius (approximately)
- **Feedback:** quadrature encoders for wheel odometry 

Sensors
-------

**Inertial Measurement Unit (IMU):** provides angular velocity and linear acceleration

- **Model:** HFI-A9
- **Sampling rate:** 100 Hz

**Encoder:** integrated with each motor; used for odometry estimation

Compute hardware
----------------

**High-level processor:** NVIDIA Jetson Xavier

- **OS:** Ubuntu 20.04
- **Middleware:** ROS2 Foxy
- **Cooling:** cooling fan

**Low-level controller:** STM32 microcontroller

- Interfaces with motor driver and encoders for real-time control

**Communication:** CAN bus at 115200 bps

Network infrastructure
----------------------

- **High-level control:** UDP of Wi-Fi between Android application and Jetson
- **IP configuration:** dynamic IP over DHCP
- **Indoor deployment:** Wi-Fi network required
- **Security:** basic
- **Remote access:** SSH for development and debugging purposes

Power system
------------

**Motors:** 24 V Li-ion battery pack, DC-DC converter (12 V) for motor drivers

**Electronics:** 12 V Li-ion battery pack, voltage regulator for Jetson, sensors, and STM32

**Safety features:**

- Fuses on smart driver boards
- Overcurrent protection
- Emergency stop push button

Safety constraints
------------------

**Hardware-level safety:** fuses and emergency stop

**Software-level safety:**

- Speed limits enforced in control software
- Communication failure handling
- Watchdog timers for microcontroller to prevent system hang

Notes
-----

1. Ensure CAN bus termination is correct to prevent communication errors
2. Confirm battery voltages before operation; over/under-voltage may damage electronics
3. When adding additional sensors, update ROS2 launch files for proper integration
4. For software testing, always use the emergency stop and verify motor driver fuses
