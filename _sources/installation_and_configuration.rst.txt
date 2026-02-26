Installation and Configuration
==============================

This section provides a comprehensive guide to installing and configuring the ROS2-based mobile manipulation app. It covers the necessary prerequisites, workspace setup, build instructions, configuration parameters, and tips for running the application effectively.

Prerequisites
-------------

- ROS2 installed on Ubuntu (any version is fine)
- Jetson Nano setup with ROS2 and necessary drivers for the robot hardware
- Android Studio installed for app development
- Basic familiarity with ROS2 concepts and Android development
- Network configuration for communication between the Android app and the robot
- Python 3 and necessary ROS2 Python packages for the robot nodes

Workspace Setup
---------------

1. Create a ROS2 workspace on the Jetson Nano:
 
   .. code-block:: bash

    mkdir -p ~/ros2_ws/src
    cd ~/ros2_ws
    colcon build
    source install/setup.bash
   

2. Clone the project repository into the ``src`` directory:

   .. code-block:: bash

      cd ~/ros2_ws/src
      git clone <repository_url>

3. Build the workspace:

   .. code-block:: bash

      cd ~/ros2_ws
      colcon build
      source install/setup.bash

4. Set up the Android project in Android Studio by importing the project from the cloned repository.

Configuration
-------------

- Update the ROS2 node parameters in the configuration files located in the `config` directory of the ROS2 package. This includes setting the correct IP address for communication and any robot-specific parameters.
- Ensure that the Android app's network settings are configured to communicate with the robot's IP address
- Adjust the waypoint navigation parameters such as speed limits, waypoint tolerance, and control gains as needed for your specific robot and environment.

Running the Application
-----------------------

1. Start the ROS2 nodes on the Jetson Nano:

   .. code-block:: bash

    source ~/ros2_ws/install/setup.bash
    ros2 run <package_name> <package_node> # repeat for all necessary nodes

2. Run the Android application from Android Studio on a connected device or emulator. Or you can just open the ``.apk`` file on the phone directly.

3. Use the app interface to set waypoints and observe the robot's behavior as it navigates to the specified locations.

.. attention ::
    This release doesn't have launch file yet. Launch file will be added in the next update release.

Common Setup Pitfalls
---------------------

- Incorrect IP address configuration leading to communication failures between the app and the robot.
- Missing dependencies or incorrect ROS2 environment setup on the Jetson Nano.
- Incompatible ROS2 versions between the robot nodes and the app's communication protocol.
- Issues with the robot's hardware drivers or sensor configurations that affect navigation performance.
- Network connectivity issues, such as firewall settings or Wi-Fi interference, that disrupt communication between the app and the robot.
