
<h1 align="center">🧀 Welcome to the Go!Cheese Repository 🧀</h1>

<div align="center">

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
<img src="img/Banner_GoCheese (2).png" alt="Go!Cheese" width="700">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>


<h3 align="center"><em>"Cheese does run away from rats, right?"</em></h3>

<p align="center">
  <img src="https://img.shields.io/badge/WRO-Future_Engineers_2026-blue?style=for-the-badge">
  <img src="https://img.shields.io/badge/Team-Go!Cheese-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Panama-🇵🇦-red?style=for-the-badge">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/LEGO-EV3-green?style=flat-square">
  <img src="https://img.shields.io/badge/Python-ev3dev2-3776AB?style=flat-square">
  <img src="https://img.shields.io/badge/Camera-HuskyLens-orange?style=flat-square">
  <img src="https://img.shields.io/badge/Arduino-Nano-00979D?style=flat-square">
</p>

---

Welcome to the official repository of Go!Cheese, a robotics team from San Miguelito, Panama, competing in the WRO Future Engineers 2026 season. This repo documents the full engineering journey behind our self-driving vehicle, from the first chassis sketch to the code that runs on the track. To make navigation easier for viewing, we have labeled each section according to the 2026 WRO Rulebook.

| | |
|---|---|
| 🏆 **Competition** | WRO Future Engineers 2026 |
| 📍 **Region** | San Miguelito, Panama |
| 🧠 **Controller** | LEGO Mindstorms EV3 |
| 💻 **Language** | Python 3 (ev3dev2) + C++ (Arduino Nano) |
| 👁️ **Vision** | HuskyLens camera |
| 🤖 **Steering** | Ackermann geometry |

---
<h3 align="center">Check us out! 👇</h3>

<p align="center">
  <a href="https://www.youtube.com/@GoCheese-pty" target="_blank">
    <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube">
  </a>
  <a href="https://www.instagram.com/teamgocheese?igsh=aXV5bTluZTg4aGFi" target="_blank">
    <img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram">
  </a>
  <a href="https://github.com/Quesovamos2662" target="_blank">
    <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub">
  </a>
</p>

---

# General Index
## WRO2026_FE_Go!Cheese

- [Meet the Team](#meet-the-team)
- [Robot Overview](#robot-overview)
- [1. Mobility & Mechanical Design](#1-mobility--mechanical-design)
  - [Driving base & chassis](#-driving-base--chassis)
  - [Motor selection & torque reasoning](#motor-selection--torque-reasoning)
  - [Steering mechanism](#steering-mechanism-ackermann)
  - [Chassis iterations](#chassis-iterations)
    - [Chassis modifications](#chassis-modifications)
    - [Vision & obstacle readiness](#vision--obstacle-readiness)
- [2. Power & Sensor Architecture](#2-power--sensor-architecture)
  - [Power supply & EV3 brick specs](#power-supply--ev3-brick-specs)
  - [Wiring diagram](#wiring-diagram)
  - [Sensor selection & placement](#sensor-selection--placement)
  - [Sensor calibration](#sensor-calibration)
- [3. Software Architecture & Obstacle Strategy](#3-software-architecture--obstacle-strategy)
  - [Algorithm description](#algorithm-description)
  - [Flowchart](#flowchart)
  - [Open Challenge logic](#open-challenge-logic)
  - [Obstacle Challenge strategy](#obstacle-challenge-strategy)
  - [Corner & edge handling](#corner--edge-handling)
  - [Tuning process](#tuning-process)
- [4. Engineering Decisions](#4-engineering-decisions)
  - [Design decision log](#design-decision-log)
  - [What didn't work](#what-didnt-work)
- [5. Reproducibility](#5-reproducibility)
  - [Bill of Materials](#bill-of-materials)
  - [Build instructions](#build-instructions)
- [Vehicle Photos](#vehicle-photos)
- [Team Photos](#team-photos)
- [Performance Video](#performance-videos)
- [Resources](#resources)

---

## 📌 Project Rundown

### Cheese Goal & Structure 

Cheese uses a priority-based control system that checks its sensors continuously and chooses the most important action for each moment. Instead of following one fixed sequence, the robot reacts in real time to the walls and its position on the track.
During normal movement, a PID controller compares the distance from the left and right walls and adjusts the steering to keep the robot centered. If Cheese gets too close to a wall, the wall-protection system takes priority, slows the robot down, and steers it away more strongly.
The color sensor is used to count completed curves. A blue–orange or orange–blue pair counts as one curve, and twelve curves represent the full three laps. After the final curve, the robot uses motor-position data and a backup timer to estimate where it should stop near its starting area.
For version 3, we are keeping this same structure while improving the PID values, wall corrections, steering angles, speeds, curve counting, and final parking position. The goal is to make the robot move more smoothly, avoid walls more consistently, and complete each lap with better accuracy.
The full explanation of the control system, priority levels, sensor use, and tuning values is included in the Software Architecture & Obstacle Strategy section below.

For the **v3** version, we are keeping this same logic but refining it: tuning how the robot reacts to corners, how sharply it steers, and how it manages speed, aiming for smoother and more consistent laps.

> The full technical breakdown of the algorithm, the priority levels and the tuning data is documented in the Software Architecture & Obstacle Strategy section below.

---

### Team Goals (Road to the National Finals)

<h2 align="center">🎯 Team Goals: Road to the National Finals 🧀</h2>

<p align="center">
  <em>Building Cheese is not only about competing. It is about learning how to think, test, fail, document, and improve like engineers.</em>
</p>

<div align="center">

| Goal                                        | What We Want to Achieve                                                                                                                                                                                                                                                                                                                                |
| :------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🧊 Freeze the Code Early**                | We plan to lock our final obstacle and parking builds at least two weeks before the competition. This gives us time to test consistently, collect data, tune values on the track, and improve reliability without creating new problems right before competition day.                                                                                  |
| **📚 Make Our Documentation Count**         | Last season, we scored **15/30** on documentation. For the next regional, our goal is to build a clear engineering journal where every decision, test, failure, and iteration is explained and supported with evidence. We also want the repository to be detailed enough for others to understand and reproduce our LEGO Mindstorms EV3-based design. |
| **🏁 Earn Our Place at Nationals**          | We want this repository to show the full engineering journey behind Cheese across all three versions of the robot. Our goal is to prove the depth of our work, not only the final result, by showing what we learned during competitions, practice sessions, and redesign cycles.                                                                      |
| **🌱 Set an Example for Our Future Selves** | Since this is our first time in the WRO Future Engineers category, we want to create a strong foundation for future improvement. We aim to meet our current goals, define new ones, and leave behind a reference that both we and other beginner teams can learn from.                                                                                 |

</div>

<p align="center">
  <strong>Our main objective is to make Cheese more than a robot:</strong><br>
  a documented engineering project built through testing, iteration, teamwork, and constant improvement.

  
</p>

<div align="center">

## 🏎️ Meet the Big Cheese! — Robot Overview

<p align="center">
  <img src="v-photos/v3/side_v3.jpg" alt="Cheese v3 Side View" width="85%">
</p>

<p align="center">
  <em>Cheese v3 side view showing the current chassis structure, wheelbase, and component layout.</em>
</p>


### 1. Dimension Table
*Cheese* has been engineered to comply strictly with the official physical constraints dictated by the WRO Future Engineers rulebook (30 x 20 x 30 cm):

| Dimension Parameter | Vehicle Metric (v3) | WRO Maximum Limit | Verification Status |
| :--- | :--- | :--- | :--- |
| **Total Length** | ~28.0 cm | 30.0 cm | 🟩 Fully Compliant |
| **Total Width** | ~13.0 cm | 20.0 cm | 🟩 Fully Compliant |
| **Total Height** | ~27.0 cm | 30.0 cm | 🟩 Fully Compliant |
| **Chassis Weight** | **888.1 g** | - | ⚡ Weight-Optimized |

---

### 2. Feature Table
A quick technical summary of the main technical specifications embedded into our platform:

| Core Subsystem | Technical Implementation Specifications |
| :--- | :--- |
| **Main Controller** | LEGO Mindstorms EV3 Brick running Python 3 (`ev3dev2`) |
| **Co-Processing Unit** | Arduino Nano (ATmega328) running C++ |
| **Vision Sensor** | HuskyLens AI Smart Camera via high-speed I2C communication |
| **Propulsion System** | Rear-wheel drive driven by a LEGO EV3 Large Motor |
| **Steering Assembly** | Front-axle Ackermann steering geometry driven by a LEGO EV3 Medium Motor |
| **Sensing** | 2x Ultrasonic + Color sensor + HuskyLens camera |
| **Sensing Array** | 2x Ultrasonic sensors (wall-following) + 1x Color sensor (corner timing) |

---

<h3 align="center">3. Achievements & Track Milestones</h3>

<p align="center">
  This section summarizes the main milestones that shaped the development of Cheese. Each achievement represents a design lesson, a technical improvement, or a feedback point that influenced the current version of the robot.
</p>

<table>
  <tr>
    <td width="28%" align="center"><strong>Regional Experience</strong></td>
    <td>
      We competed in the regional stage, which became a turning point for our team. It gave us a documentation baseline of <strong>15/30</strong> and showed us exactly where we were losing points. Seeing a <strong>0 in Software & Obstacle Strategy</strong> made it clear where we needed to focus, and that feedback shaped many of our decisions for the current season.
    </td>
  </tr>
  <tr>
    <td width="28%" align="center"><strong>Stronger Chassis</strong></td>
    <td>
      Our redesign added structural reinforcements, including cross-bracing and a central liftarm spine that connects the front and rear of the vehicle. This improved rigidity and reduced frame twisting during sharp turns. Although the weight increased from <strong>763.5 g</strong> in v2 to <strong>888.1 g</strong> in v3, we accepted the tradeoff because stability and predictable movement were more important than reducing mass at our current speed.
    </td>
  </tr>
  <tr>
    <td width="28%" align="center"><strong>Improved Sensing Setup</strong></td>
    <td>
      We redesigned how the robot senses the track. The HuskyLens camera performs its own image processing and communicates through an Arduino Nano, keeping that workload separate from the EV3 navigation code. We also replaced the unreliable front ultrasonic sensor with a color sensor for corner timing, which made the robot detect track events more consistently.
    </td>
  </tr>
</table>


---

### 4. Structural Evolution (v1, v2, & v3)

*Cheese* went through three versions before reaching its current form, and each one was a direct response to the problems we ran into with the version before it. Our changes were never random: every redesign chased more stability, more reliable sensing, or a fix to something that had failed on the track. Along the way we reworked the position of the EV3, rebuilt the steering so the motor could actually move it, swapped tires and sensors, added a camera, and reinforced the chassis, gaining a bit of weight in exchange for a much steadier robot. Here is a quick overview of how it evolved, with the full reasoning behind each change explained further down in the documentation.

| Aspect | v1 (digital model) | v2 (first regional) | v3 (current) |
| :--- | :--- | :--- | :--- |
| **Stage** | BrickLink model, never fully built | First physical build | Current competition build |
| **EV3 position** | Vertical | Horizontal | Horizontal |
| **Sensors** | 2 ultrasonic + 1 infrared | 3 ultrasonic | 2 ultrasonic + 1 color |
| **Rear tires** | Same size front/rear | 56 x 28 ZR | 56 x 28 ZR |
| **Camera** | None | None | HuskyLens on custom mount |
| **Chassis** | Compact | Compact | Lengthened front |
| **Weight** | Not measurable (model only) | 763.5 g | 888.1 g |

In short: v1 was only a digital model that proved unstable when built, v2 became our first real robot with a stable steering base, and v3 added vision and a color sensor for reliable corner timing, trading a little extra weight for noticeably more stability.

---

### 5. Cheese's logic (Flowchart Logic)

This flowchart represents the full decision cycle used by *Cheese* during the WRO Future Engineers run and circuit. The robot first initializes its motors, sensors, steering position, constants, and lap counters. Before starting, it performs a row-alignment routine by reading both ultrasonic sensors to determine if it's closer to the left or right wall and adjust its position to start the laps.

Once the run begins, the main loop repeats continuously. In every cycle, the robot reads the ultrasonic sensors and the color sensor, then decides which behavior has priority. During normal driving, the ultrasonic sensors feed a PID system that keeps the robot between the walls. If a wall is too close, wall-protection logic overrule the normal PID and applies stronger steering corrections, continiung the logic during all three laps.

When the color sensor detects a valid color, the robot confirms it through multiple readings to avoid false detections. Accepted colors are used to start or finish curves. A first color starts a curve, while the opposite color ends it, increases the curve counter, and activates recovery after the curve has been succesfully executed. After each set of curves, the robot updates the lap counter.

After completing the number of laps, the robot enters the final stop and parking logic. It uses timing and position references recorded during the run to stop near its starting row, realign itself, and finish the program.

<p align="center">
  <img src="img/Flowchart_logic_cheese.png" alt="Cheese Flowchart Logic" width="85%">
</p>

> **Note**: This flowchart was made using artificial inteligence as a support tool, keeping the logic used to develop the functioning of Cheese.
---
## 6. Cheese's Angles

This section shows the labeled angle views of **Cheese v3**. These images identify the main mechanical, electrical, and sensing components from different perspectives, making it easier to understand how the robot is physically organized.

Instead of only showing plain photos, these named angles act as a visual map of the robot. They allow readers to see where each subsystem is placed, how the components are distributed across the chassis, and how the final v3 layout supports stability, sensor access, wiring organization, and future obstacle detection.


<h3 align="center">Quick View Index</h3>

<table align="center">
  <tr>
    <th>Angle</th>
    <th>Jump to view</th>
  </tr>
  <tr>
    <td>Front angle</td>
    <td><a href="#-front-named-angle-">View front</a></td>
  </tr>
  <tr>
    <td>Left angle</td>
    <td><a href="#-left-named-angle-">View left</a></td>
  </tr>
  <tr>
    <td>Back angle</td>
    <td><a href="#-back-named-angle-">View back</a></td>
  </tr>
  <tr>
    <td>Right angle</td>
    <td><a href="#-right-named-angle-">View right</a></td>
  </tr>
  <tr>
    <td>Top angle</td>
    <td><a href="#-top-named-angle-">View top</a></td>
  </tr>
  <tr>
    <td>Bottom angle</td>
    <td><a href="#-bottom-named-angle-">View bottom</a></td>
  </tr>
</table>

---

<p align="center">
  <img src="v-photos/v3/named%20angles/named_angle_front.jpeg" alt="Cheese v3 front named angle" width="85%">
</p>

<p align="center"><em>Front named angle: shows the front layout, HuskyLens camera, helping lamp, ultrasonic sensors, color sensor, Arduino Nano, and steering area.</em></p>

---

<p align="center">
  <img src="v-photos/v3/named%20angles/named_angle_left.jpeg" alt="Cheese v3 left named angle" width="85%">
</p>

<p align="center"><em>Left named angle: shows the side structure, EV3 Brick placement, motors, sensor alignment, lighting system, and chassis support.</em></p>

---

<p align="center">
  <img src="v-photos/v3/named%20angles/named_angle_back.jpeg" alt="Cheese v3 back named angle" width="85%">
</p>

<p align="center"><em>Back named angle: shows the rear structure, Large Motor position, Arduino Nano, HuskyLens camera, wiring area, and lighting battery.</em></p>

---

<p align="center">
  <img src="v-photos/v3/named%20angles/named_angle_right.jpeg" alt="Cheese v3 right named angle" width="85%">
</p>

<p align="center"><em>Right named angle: shows the right-side component layout, motors, sensors, EV3 Brick position, and support structure.</em></p>

---

<p align="center">
  <img src="v-photos/v3/named%20angles/named_angle_top.jpeg" alt="Cheese v3 top named angle" width="85%">
</p>

<p align="center"><em>Top named angle: shows the top-down organization, wiring path, camera system, Arduino Nano placement, and rear motor area.</em></p>

---

<p align="center">
  <img src="v-photos/v3/named%20angles/named_angle_bottom.jpeg" alt="Cheese v3 bottom named angle" width="85%">
</p>

<p align="center"><em>Bottom named angle: shows the underside structure, wheelbase, chassis support, EV3 position, sensor visibility, and motor placement.</em></p>

---

## Meet the Team

We are **Go!Cheese**, a robotics team of two from San Miguelito, Panama, competing in the WRO Future Engineers 2026 season. Romina and Caylee work collaboratively: Romina handles the changes and builds on the robot itself, while Caylee handles the documentation. Our roles complement each other step by step, since we constantly rely on one another, sharing observations and feedback to keep improving and moving forward.

<p align="center">
  <img src="t-photos/team_photo.jpg" alt="Go!Cheese Team" width="70%">
</p>

---

### Caylee Rios

![Role](https://img.shields.io/badge/Role-Software_&_Documentation-brightgreen?style=for-the-badge)

- **Age:** 16
- **Description:** Hii! My name is Caylee and this is my first time competing in WRO. I'm really happy to be part of a sport that pushes you toward hard work and personal growth. I'm in charge of the software and the documentation. I love smiling, asking lots of questions, and having people I care about around me who inspire me and push me to be better every day.

[Instagram](https://www.instagram.com/caymrr) · [Email](mailto:cayleerios@gmail.com)

<p align="center">
  <img src="t-photos/caylee.jpg" alt="Caylee Rios" width="45%">
</p>

---

### Romina Mora

![Role](https://img.shields.io/badge/Role-Programmer_&_Robot_Builder-ff69b4?style=for-the-badge)

- **Age:** 16
- **Description:** Helloo!!! I'm Romina, a very passionate gamer. I enjoy anything that represents a challenge, including this project. Since 2025 I've shown interest in robotics in general, and I finally managed to join a team in 2026. I wish to learn plenty to improve my skills next year. My role is programmer and robot builder.

*No socials, so reach out through my partner.*

<p align="center">
  <img src="t-photos/romina.jpg" alt="Romina Mora" width="45%">
</p>

---

<h2 align="center">🧀 Why "Cheese"? 🧀</h2>

<p align="center">
  <em>"From a childhood rhyme to the competition track."</em>
</p>

<div align="center">

────────୨ৎ────────

</div>

Our name comes from a little recess rhyme we used to play back when we were kids. It always stuck with us, so when it came time to name our team, we picked something that carries a piece of that memory with us. That is how **Go!Cheese** was born, a name that reminds us of where we started and of the season of our lives we are living right now.

Our robot is named **Cheese** as a pun on our team name. The idea is simple, and it is the heart of everything we build:

<p align="center">
  <strong>Cheese is the one who goes.</strong>
</p>

<div align="center">

────────୨ৎ────────

</div>

