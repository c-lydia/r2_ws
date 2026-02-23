Introduction
============

Background
----------

Motivation
^^^^^^^^^^

Following the previous year in Android application development for robotics system, we have been using Android app as the controller for the robots. 

However, this approach works with the xbox gamepad that acts as the main controller for our robots, using the buttons and joystick to navigate the robots manually. While this method provides real-time control, it limits automation and precise waypoint navigation. The initial idea of this project originated from Mr.PHOLL Chanphayuk, who proposed an Android-based interface that allows users to interact with the robot through touch inputs on the screen, combined with odometry feedback and a virtual joystick. The concept was intended for interactive tasks, such as robot basketball playing.


After changes in term members and project direction, the focus of the project evolved from manual joystick control to a waypoint-based navigation system. This shift was encouraged by Dr.SRANG Sarot, aiming to reduce dependency on gamepad controllers and to explore a more autonomous navigation approach using Android applications as the main interface.

Problem Statement
^^^^^^^^^^^^^^^^^

Manual control using gamepads or joysticks presents several limitations in robotic navigation systems:

- Continuous use input is required, increasing operator workload
- Precise positioning is difficult due to human reaction time and control sensitivity
- The system lacks scalability for autonomous behaviors
	      
To address these issues, a waypoint navigation system is proposed, where uses can define target positions (waypoints) through an Android application, and the robot navigates to these positions using odometry and orientation data.

However, implementing such a system introduces challenges, including:

- Accurate coordinate transformation between Android interface and the robot’s reference frame
- Proper handling of robot orientation (yaw) in navigation calculations
- Reliable communication between the Android application and the robot’s ROS2-based control system
- Managing waypoint editing, execution, and return behaviors without causing state conflicts

These challenges motivated the need to redesign the calculation logic and communication protocol to ensure compatibility with ROS2 and improve navigation accuracy.

Literature Review
^^^^^^^^^^^^^^^^^

Waypoint-based navigation is a common approach in mobile robotics, especially in autonomous systems using frameworks such as ROS and ROS2. Previous works and standard robotics literature describe waypoint navigation as a method where a robot moves through a sequence of pre-defined target positions using localization and motion control algorithms.

Odometry-based navigation is widely used for estimating a robot’s position by integrating wheel encoder data over time. Although odometry is simple to implement, it is sensitive to drift and orientation errors, particularly in yaw estimation. Many systems combine odometry with higher-level navigation logic to mitigate these issues.

Mobile interfaces for robot control, including Android-based applications, have also been explored as flexible and user-friendly solutions. Touch-based interfaces allow intuitive interaction, but require careful mapping between screen coordinates and real-world robot motion. 

This project builds upon these established concepts, focusing on practical implementation rather than theoretical optimization.

Concepts
^^^^^^^^

The waypoint navigation system in this project is based on the following key concepts:

- Waypoint navigation: the robot is instructed to move toward pre-defined target positions instead of being continuously controlled by the user.
- Odometry: the robot’s position and orientation are estimated using incremental motion data.
- Yaw orientation: the robot’s heading angle is critical for accurate navigation and must be correctly handled in coordinate transformations.
- Client-sever communication: the Android application acts as a client that sends waypoints data to the robot, while the robot processes these commands within a ROS2 environment.

For simplification, the system assumes:

- A planar (2D) environment
- Reliable odometry data without sensor fusion
- Pre-defined motion control handled by the robot’s existing control stack
	      
The Android application focuses on target setting, waypoint management, and command transmission, while the robot handles low-level motion execution.

Objective
---------

This project is developed in order to:

- Design and implement Android app to define, edit, and manage navigation waypoints on a pre-defined map
- Develop custom ROS2 control logic to receive waypoint data and execute navigation commands on the robot
- Implement accurate coordinate transformation and scaling between Android interface and the robot’s reference frame
- Handle robot orientation (yaw) correctly during waypoint navigation to improve positioning accuracy
- Establish reliable client-server communication between the Android app and the ROS2-based robot system
- Implement waypoint execution features including sequential navigation, editing, and return-to-previous-waypoint behaviors
- Test and evaluate system performance, identifying limitations related to map alignment, yaw accuracy, and state management.

Scope of work
-------------

This project covers:

- Android application development (Target_Setter)
- Communication system
- Robotic software development (ROS2)
- System integration and testing

This project does not include:
- Full autonomous robot navigation
- Sensor fusion beyond basic odometry and IMU integration
- Algorithm optimization
- Low-level communication protocol
- Hardware-level motor driver design
- Network security mechanism