# Autonomous Sorting Robot 🤖

## Overview

This project consists of the design and implementation of a semi-autonomous pick and place robotic arm capable of sorting ping pong balls based on their color. The system integrates computer vision, control systems, and embedded programming using the Arduino UNO Q platform.

The main objective is to detect colored objects (ping pong balls), determine their position in space, and execute a sequence of movements to pick and place them into their corresponding containers.

---

## System Architecture

The system is divided into two main subsystems:

### 1. Low-Level Control (MCU / Arduino Sketch)

* Controls all servo motors of the robotic arm
* Receives commands via serial communication
* Executes joint movements (forward kinematics)
* Maintains constraints such as angle limits and synchronized joints

### 2. High-Level Control (Linux / Python)

* Captures image from a USB camera
* Processes the image using OpenCV
* Detects objects using HSV color segmentation
* Computes object position in workspace coordinates
* Sends movement commands to the robotic arm

---

## Hardware Components

* Arduino UNO Q (main platform)
* 4x MG995 / MG996R Servos (high torque joints)
* 3x MG90S Servos (wrist and gripper)
* External 5V Power Supply (recommended ≥ 8–10A)
* USB Camera (webcam)
* Breadboard and wiring
* 3D printed robotic arm structure

---

## Software Structure

```text
autonomous-sorting-robot/
│
├── sketch/
│   └── robot_arm_base.ino        # Low-level servo control
│
├── python/
│   └── vision_color_detect.py   # Computer vision pipeline
│
├── docs/
│   └── notes.md                 # Calibration, tests, etc.
│
├── README.md
```

---

## Control Strategy

The robot operates in two modes:

### Manual Mode

* Controlled via serial commands or external GUI
* Used for calibration and testing
* Allows direct manipulation of joint angles

### Autonomous Mode

* Vision system detects object color and position
* Coordinates are transformed into robot reference frame
* Inverse kinematics determines joint angles
* Robot executes pick-and-place routine

---

## Key Concepts

* HSV color segmentation for robust object detection
* Serial communication between Python and Arduino
* Forward and inverse kinematics
* Workspace calibration
* Real-time control of servo motors

---

## Current Status

* [x] Project structure defined
* [x] Firmware base for servo control
* [ ] Vision system (HSV detection)
* [ ] Coordinate calibration
* [ ] Inverse kinematics implementation
* [ ] Full autonomous pick-and-place

---

## Future Improvements

* Smooth trajectory planning
* PID control or motion interpolation
* Multi-object tracking
* Improved lighting robustness
* GUI for manual control in Python

---

## Notes

This project is developed as part of an academic challenge involving robotics, automation, and computer vision. The focus is on system integration and practical implementation rather than industrial-level precision.

---

## Author

Developed by [Patricio D'Abbwrtt Juárez]

---
