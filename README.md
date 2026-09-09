<h1 align="center">🧀 Welcome to the Go!Cheese Repository 🧀</h1>

<div align="center">

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

<img src="img/Banner_GoCheese%20(2).png" alt="Go!Cheese" width="700">

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>

<h3 align="center"><em>"Cheese does run away from rats, right?"</em></h3>

<p align="center">
  <img src="https://img.shields.io/badge/WRO-Future_Engineers_2026-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Team-Go!Cheese-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Robot-Cheese_v4-FF8FAB?style=for-the-badge">
  <img src="https://img.shields.io/badge/Panama-🇵🇦-red?style=for-the-badge">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Controller-LEGO_EV3-green?style=flat-square">
  <img src="https://img.shields.io/badge/Software-Python_3_(ev3dev2)-3776AB?style=flat-square">
  <img src="https://img.shields.io/badge/Vision-HuskyLens-orange?style=flat-square">
  <img src="https://img.shields.io/badge/Bridge-Arduino_Nano-00979D?style=flat-square">
  <img src="https://img.shields.io/badge/Mass-666_g-FFD43B?style=flat-square">
</p>

---

<p align="center">
Welcome to the official engineering repository of <strong>Go!Cheese</strong>, a robotics team from Panama competing in the <strong>WRO Future Engineers 2026</strong> season.
</p>

<p align="center">
This repository documents the complete development of our autonomous vehicle, <strong>Cheese</strong>, including mechanical design, sensor architecture, software, testing, failures, redesigns, and the evolution from our earliest concepts to the current <strong>Cheese v4</strong>.
</p>

<div align="center">

| Project | Current Configuration |
| :--- | :--- |
| **Competition** | WRO Future Engineers 2026 |
| **Robot** | Cheese v4 |
| **Main Controller** | LEGO Mindstorms EV3 |
| **Programming** | Python 3 (`ev3dev2`) |
| **Vision Processing** | HuskyLens + Arduino Nano |
| **Drive** | Rear-wheel drive |
| **Steering** | Front Ackermann steering |
| **Distance Sensing** | 3 EV3 Ultrasonic Sensors |
| **Floor Detection** | EV3 Color Sensor |
| **Current Mass** | **666 g** |

</div>

---

<h3 align="center">Check us out! 👇</h3>

<p align="center">
  <a href="https://www.youtube.com/@GoCheese-pty">
    <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white">
  </a>
  <a href="https://github.com/Quesovamos2662">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white">
  </a>
</p>

---

# ᯓ★ Meet Cheese v4 ᯓ★

<p align="center">
  <img src="v-photos/v4/hero_angle_v4.jpg"
       alt="Cheese v4"
       width="80%">
</p>

<p align="center">
  <em>Cheese v4 — the current competition configuration of Go!Cheese.</em>
</p>

Cheese v4 represents the largest redesign of our vehicle so far.

After testing v3, we realized that simply adding more structural support and hardware was not always an improvement. The robot had reached approximately **888 g**, had a taller upper structure, longer wiring routes, additional lighting hardware, and more LEGO elements than were necessary for reliable operation.

Version 4 was redesigned around a different idea:

> **Keep what directly improves reliability, and remove what does not.**

The resulting vehicle has a mass of approximately **666 g**, meaning that around **222 g** were removed while maintaining the systems required for autonomous navigation.

Major v4 changes include:

- lower and flatter EV3 Brick placement;
- horizontal EV3 Large Motor placement;
- redesigned front steering structure;
- LEGO SPIKE front wheels;
- reduced upper structure;
- shorter cable routing;
- three ultrasonic sensors;
- lower color-sensor positioning;
- lower HuskyLens mounting;
- removal of the previous auxiliary lighting system;
- simplified Arduino Nano integration.

The result is a lighter, lower, cleaner, and easier-to-debug platform.

---

# ❀ How Cheese Thinks ────୨ৎ────────୨ৎ────

Cheese does not simply execute one fixed sequence of movements.

Its software continuously reads the available sensors and decides which behavior currently has the highest priority.

During normal Open Challenge driving, the control structure can be summarized as:

```text
READ SENSORS
      ↓
SAFETY CHECK
      ↓
WALL PROTECTION
      ↓
PID CORRECTION
      ↓
COLOR / CURVE DETECTION
      ↓
STEERING COMMAND
      ↓
CURVE COUNT
      ↓
12 CURVES?
   ↓       ↓
  NO      YES
   ↓       ↓
CONTINUE  PARK
