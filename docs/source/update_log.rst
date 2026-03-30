Update Log
==========

V1.0
----

Features
^^^^^^^^

Target_Setter app
~~~~~~~~~~~~~~~~~

- Basic waypoints coordinate
- Communicate with robot over UDP, JSON array packets
- Send waypoint one by one (when user adds one waypoint, send automatically)
- Implemented virtual joystick

.. attention::

    - This version has no edit and return functionalities
    - No emergency stop is implemented on software

ROS2 packages
~~~~~~~~~~~~~

- PD controller with complementary filtering for translation
- P controller with velocity saturation for rotation
- Communicate with app at 10Hz over UDP
- Basic waypoint controller
- Feedback odometry to app
- Deadzone is implemented

.. attention:: 

    No emergency stop is implementedon software layer

Performance
^^^^^^^^^^^

- Communication is sufficient
- PD controller is effective
- Yaw drifts due to mistakes in localization

V2.0
----

Updates
^^^^^^^

Target_Setter app
~~~~~~~~~~~~~~~~~

- Removed virtual joystick
- Communication is updated to binary packet with Little Endian byte order
- Definition of new packet structures
- Implemented edit and return functionalities
- Send waypoints only when user triggered

ROS2 packages
~~~~~~~~~~~~~

- Removed redundent nodes
- Added packet validation checked
- PD controller with complementary filtering
- Arrival detection added
- Added emergency stop

Performance
^^^^^^^^^^^

- Communication is efficient
- Yaw drift
- Controller is effective
- Undefined state behavior occurred

V3.0
----

Updates
^^^^^^^

ROS2 packages
~~~~~~~~~~~~~

- Corrects inverse kinematic equation
- Implements wheel odometry instead is using forward kinematic for odometry
- Simplifies controller to P controller with velocity saturation and rate limiting
- Improves arrival detection and planning logic
- Implements state machine

.. attention::

    This version doesn't have any updates on Target_Setter app

