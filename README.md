# Target_Setter_v1

![License](https://img.shields.io/badge/license-Apache%202.0-blue)
![ROS2](https://img.shields.io/badge/ROS2-humble-22314E?logo=ros&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-3776ab?logo=python&logoColor=white)
![Java](https://img.shields.io/badge/Java-ED8B00?logo=openjdk&logoColor=white)
![Docs](https://img.shields.io/badge/docs-RST-8CA1AF?logo=readthedocs&logoColor=white)
![venv](https://img.shields.io/badge/venv-enabled-4B8BBE?logo=python&logoColor=white)
![Stars](https://img.shields.io/github/stars/c-lydia/r2_ws?style=flat)
![Forks](https://img.shields.io/github/forks/c-lydia/r2_ws?style=flat)
![Watchers](https://img.shields.io/github/watchers/c-lydia/r2_ws?style=flat)
![Release](https://img.shields.io/github/v/release/c-lydia/r2_ws)
![Issues](https://img.shields.io/github/issues/c-lydia/r2_ws?color=yellow)
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=c-lydia.r2_ws)

## Packages

This project has 2 packages:

- Target_Setter app
- src (src files for Robot R2 2024)

---

## Features

---

### Target_Setter App

- Changing field based on user inputs
- Waypoints display to control robot's position
- Undo and Clear all the waypoints
- Waypoints can be added up to 27 waypoints
- Sending and receiving positions to and from robot via UDP
- Editing position
- Sending return signal
- Send all waypoints at once

---

### r2_src

- Moving based on data from Target_Setter app
- Receiving and sending odometry from app and to app
- Auto-detecting app's IP address using `/target_info` topic
- Robot position live editing (position)
- Robot return function to previous waypoints
- Lock robot only to receive data from one source and terminate connection if no data is received within 15 minutes
- New custom messages `TargetSetter`, `Waypoint`, `UpdateWaypoint`, and `Return` for topic `target_info`, `/waypoint`, `/update_wp`, and `/return_flag` respectively
- UDP can receive data up to 64kB
- Sending data to app at 10Hz
- The port of the UDP socket for binding with the app is set to `5050`
- Automatically filp the local frame if the frame transformation is reversed

---

## Configuration

- copy `r2_src` into your workspace, rename it to `src`
- Then build the packages

``` bash
colcon build
```

- Install the provided `.apk` file on your android phone (if it asks you to scan, don't scan, just proceed to installation directly)

---

## How to operate

- after building the workspace, source your workspace, then run all the packages
- on the app, input the IP address of the robot, and set the port to 5050
- click on the gamefield to set waypoint
- click Change button if you wish to change the field dimension
- click Send button if you wish to send all the waypoints
- if the robot terminates the connection, you have to bind again

---

## how to use the app

![alt text](img/photo_2025-12-06_17-05-38.jpg)

- To add waypoint click on the field
- Change button is for changing field dimension
- Undo button deletes the last waypoint
- Clear button deletes all waypoint
- Edit button lets you edit the position of the waypoint with the ID you select
- Send button sends all the data of every waypoints you added
- Return button signals the robot to return to previous waypoint
- Bind button is UDP bridge, allowing robot to bind with app
  
---

## Limitations

- The odometry (`current_odometry`) is off by a few centimeters, and the orientation is also off by a few radians
- The app can't handle too high frequency, it will lag
- There's no launch file for this version
- No emergency stop is set on the app
