Troubleshooting Guide
=====================

Communication issues
--------------------

Symptom: robot doesn't repond to app command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Wi-Fi connectivity issues:**

- Check that the robot is connected to the correct Wi-Fi network and has a valid IP address
- Verify IP address of the robot matches the one configured in the app
- Use ``ifconfig`` on the Jetson to check network interfaces and IP configuration

**UDP packets not received:**

- Confirm the correct port (default ``5050``) is used
- Ensure packets are sent in **Little Endian** format

**Firewall blocking UDP:**

- Disable firewall or allow UDP traffic on port 5050

Symptom: waypoints not updating/edits ignored
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Possible causes and solutions:**

- Plan ID mismatch between app and robot
- Edited waypoint index out of range
- Packet corruption: check Little Endian encoding and packet size

Motor/driver issues
-------------------

Symptom: robot does not move or moves incorrectly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Possible causes and solutions:**

- Motor driver fuse blown: replace fuse and test
- Motors not powered: verify 24 V motor battery and DC-DC converter
- Encoder feedback lost: check encoder connections to STM32
- Wheels misaligned: check mecanum wheel orientation
- Incorrect velocities from controller: verify PD controller gains

Symptom: robot moves jerkily or overshoots targets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Derivative term too noisy: verufy ``ALPHA_D`` filtering
- Low update frequency: check odometry reception at 10 Hz
- Active waypoint updates cause jumps: ensure complementary smoothing is applied

Sensor issues
-------------

Symptom: odometry is incorrect/robot drifts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Checks IMU calibration and orientation
- Verify encoder counts correspond to expected wheel rotation
- Confirm yaw offset calculation (``yaw_start``, ``overflow_counter``)
- Dead reckoning integration might accumulate error: check ``dt`` values

Symptom: robot reports zero movement despite motor command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Motor velocities not reaching STM32: verify CAN bus communication
- Verify low-level motor control code maaps velocities correctly to wheels

App issues
----------

Symptom: robot position not displayed correctly
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Verify coordinate conversions from meters to pixels (``metersToPxX/Y``) are correct
- Check ``latestOdometry`` is being updated from UDP socket
- Confirm screen boundary and field dimensions (``GAME_FIELD_X/Y``) match robot workspace

Symptom: touch input does not map to correct target
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Check touch, normalized, percentage, global meter conversion
- Ensure ``boundaruView`` dimensions match the UI

Safety/emergency stop
---------------------

Symptom: robot does not stop when emergency button pressed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Verify emergency stop wiring and fuses are intact
- Ensure software checks for emergency stop signal are active
- Test manually by cutting power to confirm hardware response

PD controller/motion control
----------------------------

Symptom: robot oscillates around waypoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Decreases ``k_p_linear`` or ``k_p_yaw`` gains
- Increase derivative damping (``ALPHA_D``)
- Verify derivative errors are computed correctly using ``dt``

Symptom: robot fails to reach waypoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Check ``goal_tolerance_pos`` and pause duration
- Confirm ``active_target`` queue is populated and not empty
- Make sure velocity limits allow the robot to reach target within constraints

Low-level hardware checks
-------------------------

- **Jetson:** check power LED, CPU usage, and fan
- **STM32:** verify firmware is running; check CAN message counts
- **Batteries:** measure voltage under load; replace if below threshold
- **Motor drivers:** check for overcurrent events or thermal shutdowns

.. attention::

   1. Always start troubleshooting from connectivity, sensors, motion, control logic
   2. Use logs from app (``sendWaypoints()``, ``latestOdometry``) to verify packet flow
   3. Test motor and wheel functionality before running autonomous commands
   4. Keep fuses, emergency stop, and emergency protocols ready during testing
