

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
|  **Competition** | WRO Future Engineers 2026 |
|  **Region** | San Miguelito, Panama |
|  **Controller** | LEGO Mindstorms EV3 |
|  **Language** | Python 3 (ev3dev2) + C++ (Arduino Nano) |
|  **Vision** | HuskyLens camera |
|  **Steering** | Ackermann geometry |

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

## WRO2026_FE_Go!Cheese



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

## General Project Index

You can use this index to navigate through our robot’s documentation. Each section explains a specific part of Cheese’s development process, including the mechanical design, power and sensor architecture, software logic, engineering decisions, reproducibility materials, testing resources, source code, and visual documentation.

---

- [**General Project Overview**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/01-mobility-and-mechanical-design/project%20overview.md)
  - Introduces Cheese as our WRO Future Engineers robot.
  - Explains the robot’s main purpose, competition context, and general design direction.
  - Summarizes how the mechanical structure, sensors, software, testing process, and final strategy work together.

---

- **1. Mobility and Mechanical Design**
  - [**1.1 Mechanical Design**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/01-mobility-and-mechanical-design/1.1-mechanical-design.md)
    - Explains the main mechanical choices behind Cheese’s movement system.
    - Includes motor selection, wheel choice, torque and speed reasoning, and drivetrain testing observations.
    - Justifies why the EV3 Large Motor is used for propulsion and the EV3 Medium Motor is used for steering.

  - [**1.2 Structural Components**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/01-mobility-and-mechanical-design/1.2-structural-component.mds.md)
    - Documents the LEGO Technic components used to build the robot’s structure.
    - Explains the role of liftarms, pins, axles, connectors, and reinforced sections.
    - Connects structural choices to durability, alignment, and mechanical reliability.

  - [**1.3 Steering and Drive**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/01-mobility-and-mechanical-design/1.3-steering-and-drive.md)
    - Describes the rear-wheel drive system and Ackermann steering mechanism.
    - Explains how propulsion and steering work together during straight movement, curves, and corrections.
    - Includes reasoning about steering response, linkage movement, drivetrain stability, and control.

  - [**1.4 Chassis Explanation**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/01-mobility-and-mechanical-design/1.4-chassis-explanation.md)
    - Explains the chassis layout and how the robot’s body supports each subsystem.
    - Describes weight distribution, mounting points, upper tower support, and component placement.
    - Shows how the chassis evolved to support sensors, lights, wiring, and repeated testing.

---

- **2. Power and Sensor Architecture**
  - [**2.1 Power Supply and EV3**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/%2002-power-and-sensor-architecture/2.1-power-supply-and-ev3.md)
    - Explains how Cheese is powered during operation.
    - Describes the EV3 rechargeable battery, motor power, sensor power, Arduino Nano power, HuskyLens power, and external lighting battery.
    - Connects the power architecture to reliability, safe subsystem separation, and easier debugging.

  - [**2.2 Wiring Diagram**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/02-power-and-sensor-architecture/2.2-wiring-diagram.md)
    - Shows how motors, sensors, Arduino Nano, HuskyLens, and lights are connected.
    - Documents the EV3 input/output ports and the communication path between components.
    - Helps reproduce the robot’s electrical layout and avoid wiring mistakes.

  - [**2.3 Sensor Selection and Placement**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/%2002-power-and-sensor-architecture/2.3-sensor-selection-and-placement.md)
    - Explains why each sensor was selected and where it is placed on the robot.
    - Covers ultrasonic wall sensing, color sensor floor detection, and HuskyLens obstacle recognition.
    - Connects sensor placement to navigation accuracy, curve detection, obstacle strategy, and reliability.

  - [**2.4 Sensor Calibration**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/%2002-power-and-sensor-architecture/2.4-sensor-calibration.md)
    - Describes how sensors are checked and adjusted before testing.
    - Explains calibration for ultrasonic readings, color detection, HuskyLens recognition, and lighting support.
    - Helps make the robot’s sensing behavior more consistent between runs.

---

- **3. Software and Obstacle Strategy**
  - [**3.0 Cheese Logic Overview**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy03-software-and-obstacle-strategy/3.0%20Cheese%20Logic%20Overview.md)
    - Gives a general overview of Cheese’s software behavior.
    - Explains the robot’s priority-based decision system and main control flow.
    - Summarizes how normal driving, wall protection, curve handling, obstacle logic, tuning, and parking connect.

  - [**3.1 Algorithm Architecture**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy03-software-and-obstacle-strategy/3.1-algorithm-architecture.md)
    - Explains the internal structure of the robot’s code.
    - Describes the main behavior layers, including PID centering, wall correction, curve logic, recovery, obstacle response, and final stop logic.
    - Shows how software priorities prevent different behaviors from interfering with each other.

  - [**3.2 Flowchart**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy03-software-and-obstacle-strategy/3.2-flowchart.md)
    - Presents the general logic flow used by Cheese during a run.
    - Helps visualize how the robot initializes, reads sensors, chooses behaviors, counts curves, and stops.
    - Connects the written algorithm to a clearer visual representation.

  - [**3.3 Open Challenge**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy/3.3-open-challenge.md)
    - Explains the strategy used for the Open Challenge.
    - Describes wall following, PID centering, protected wall correction, color-based curve detection, lap tracking, and final stop planning.
    - Focuses on consistent autonomous movement without red or green obstacles.

  - [**3.4 Obstacle Challenge**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy03-software-and-obstacle-strategy/3.4-obstacle-challenge.md)
    - Explains how Cheese handles red and green obstacles.
    - Describes how the HuskyLens, Arduino Nano, lighting system, and movement logic support obstacle recognition.
    - Connects obstacle detection to steering decisions, controlled avoidance, recovery behavior, and safe path planning.

  - [**3.5 Corner Handling**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy03-software-and-obstacle-strategy/3.5-corner-handling.md)
    - Explains how Cheese detects, enters, counts, and exits corners.
    - Describes the relationship between color detection, confirmed blue/orange pairing, curve counting, and post-curve recovery.
    - Shows why corner handling is separated from normal PID driving.

  - [**3.6 Tuning Process**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/03-software-and-obstacle-strategy03-software-and-obstacle-strategy/3.6-tuning-process.md)
    - Documents how movement values were adjusted during testing.
    - Explains tuning for curve aggressiveness, steering angles, PID response, wall protection, color detection, parking, and obstacle recognition.
    - Shows how testing results influenced software changes and calibration decisions.

---

- **4. Engineering Decisions**
  - [**4.1 Design Decision Log**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/04-engineering-decisions/4.1-design-decision-log.md)
    - Explains the major decisions that shaped Cheese v3.
    - Includes controller choice, Arduino role, code simplification, sensor changes, lighting system, mechanical reinforcement, curve tuning, and parking refinement.
    - Focuses on why each decision was made, what constraint caused it, and what tradeoff it involved.

  - [**4.2 What Did Not Work**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/04-engineering-decisions/4.2-what-didnt-work.md)
    - Documents the ideas, systems, and configurations that failed during development.
    - Explains issues with Arduino main control, long code, infrared sensing, front ultrasonic sensing, lighting, broken pins, wide curves, and parking.
    - Shows how each failure became evidence for a later design improvement.

---

- **5. Reproducibility**
  - [**5.1 Bill of Materials**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/05-reproducibility/5.1-bill-of-materials.md)
    - Lists the main components required to rebuild Cheese v3.
    - Includes motors, sensors, EV3 components, HuskyLens, Arduino Nano, lights, battery, LEGO Technic parts, and structural pieces.
    - Connects each component to its role in the final robot architecture.

  - [**5.2 Build Instructions**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/05-reproducibility/5.2-build-instructions.md)
    - Provides step-by-step instructions to rebuild Cheese v3.
    - Explains the build order, chassis construction, drive system, Ackermann steering, sensor placement, wiring, lights, calibration, and testing workflow.
    - Helps another builder reproduce the robot and understand the purpose of each subsystem.

---

- **6. Additional Resources**
  - [**6.1 Additional Resources**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/blob/main/sections/06-other-resources/6.1-additional-resources.md)
    - Contains supporting materials that do not fit directly into the main engineering sections.
    - Can include testing graphs, code-based data, sensor logs, extra diagrams, future 3D model references, and development notes.
    - Supports deeper analysis of Cheese’s performance and testing process.

---

- **7. Source Code**
  - [**Source Code Folder**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/src)
    - Contains the robot’s program files and code versions.
    - Includes the software used to control movement, steering, sensors, curve logic, obstacle behavior, tuning, and final stopping.
    - Supports reproducibility by connecting the documentation to the actual robot logic.

---

- **8. Digital Models and Schemes**
  - [**Robot Models**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/models)
    - Contains digital model references for Cheese’s chassis, steering system, and version-based development.
    - Helps document the robot’s structure beyond physical photos.

  - [**Schemes**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/schemes)
    - Contains supporting diagrams and technical reference files.
    - Includes wiring and robot reference documents such as final robot PDFs and wiring diagram images.

---

- **9. Visual Documentation**
  - [**Version 1 Photos**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/v-photos/v1)
    - Shows the first physical version of Cheese.
    - Helps compare early mechanical ideas with later improvements.

  - [**Version 2 Photos**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/v-photos/v2)
    - Documents the second version of the robot.
    - Shows changes in structure, sensor placement, steering layout, and design direction before the final v3 design.

  - [**Version 3 Photos**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/v-photos/v3)
    - Shows the current Cheese v3 build from multiple angles.
    - Includes front, back, side, top, bottom, sensor placement, camera placement, and dual-light system photos.

  - [**Cheese v3 Named Angles**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/v-photos/v3/named%20angles)
    - Contains labeled images of the final robot.
    - Identifies the EV3 Brick, motors, sensors, HuskyLens, Arduino Nano, lights, and main structural components.

---

- **10. Team Documentation**
  - [**Team Photos**](https://github.com/Quesovamos2662/WRO2026_FE_Go-Cheese/tree/main/t-photos)
    - Contains team-related images and documentation.
    - Supports the human side of the project by showing the people behind Cheese.

---

<p align="center">
  <strong>This index connects every major part of the repository so the full engineering process can be followed from concept, to design, to testing, to final reproduction.</strong>
</p>

---


<h2 align="center"> Team Goals: Road to the National Finals 🧀</h2>

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

<h2 align="center">Meet the Big Cheese! — Robot Overview</h2>

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

# ᯓ★ Meet the Team ᯓ★

<p align="center">
  <img src="https://img.shields.io/badge/Team-Go!Cheese-FFD43B?style=for-the-badge">
  <img src="https://img.shields.io/badge/Country-Panama-4A90E2?style=for-the-badge">
  <img src="https://img.shields.io/badge/Season-WRO_2026-57C785?style=for-the-badge">
  <img src="https://img.shields.io/badge/Members-2-FF8FAB?style=for-the-badge">
</p>

<p align="center">
  <em>Two students, one robot, many late tests, many changes, and one very determined piece of cheese.</em>
</p>

<p align="center">
  <img src="t-photos/team_photo.jpg" alt="Go!Cheese Team Photo" width="72%">
</p>

<p align="center">
  <strong>We are Go!Cheese</strong>, a robotics team of two from San Miguelito, Panama, competing in the 
  <strong>WRO Future Engineers 2026</strong> season. Our team is built on collaboration, patience, testing, and trust. 
  Romina focuses on programming, robot changes, and physical building, while Caylee focuses on documentation, software explanation, 
  engineering analysis, and organizing the project so others can understand how Cheese works.
</p>

<p align="center">
  <em>What makes our team special is not that we always get things right on the first try. It is that we keep testing, fixing, explaining, rebuilding, and trying again until Cheese gets closer to the robot we imagine.</em>
</p>

---

## ❀ Team at a Glance ────୨ৎ────────୨ৎ────

<div align="center">

| Member | Main Role | Superpower | Project Focus |
| :---: | :--- | :--- | :--- |
| **Caylee Rios** | Software Explanation & Documentation | Turning ideas, tests, and failures into clear engineering documentation | README structure, logic explanation, tuning analysis, visual organization |
| **Romina Mora** | Programming & Robot Builder | Turning ideas into physical robot changes and functional code | Robot building, code implementation, mechanical adjustments, testing support |

</div>

<p align="center">
  <strong>Our teamwork works because one of us organizes and explains the process, while the other transforms those ideas into code and robot changes. Together, we connect the story, the software, and the physical robot.</strong>
</p>

---

## ❀ Our Team Dynamic ────୨ৎ────────୨ৎ────

<div align="center">

| What Happens During Testing | How We Work Together |
| :--- | :--- |
| **Cheese crashes into a wall** | We identify whether the issue is mechanical, sensor-based, or software-based. |
| **The curve is too wide or too sharp** | We discuss the behavior, adjust values, and test again. |
| **The color sensor misses a marker** | We check lighting, color calibration, sensor height, and detection logic. |
| **Parking becomes inaccurate** | We review curve counting, timing, final stop logic, and run consistency. |
| **The robot improves** | We document what changed and why it worked. |

</div>

This process helped us grow as a team because we learned that robotics is not only about building or coding. It is also about observing, communicating, making decisions, and understanding why each change matters.

---
# ✦ Member Profiles ─── ⋆⋅☆⋅⋆ ───

<p align="center">
  <em>Each member of Go!Cheese has a different role, but both profiles are connected by testing, communication, problem-solving, and the shared goal of making Cheese better.</em>
</p>

---

## ❀ Caylee Rios ────୨ৎ────────୨ৎ────

<p align="center">
  <img src="https://img.shields.io/badge/Role-Documentation_&_Software_Analysis-57C785?style=for-the-badge">
  <img src="https://img.shields.io/badge/Age-16-FFD43B?style=for-the-badge">
</p>

<p align="center">
  <img src="t-photos/caylee.jpg" alt="Caylee Rios" width="45%">
</p>

<div align="center">

| Category | Description |
| :--- | :--- |
| **Main Focus** | Documentation, software explanation, engineering reasoning, README structure, and testing analysis. |
| **Project Strength** | Turning tests, failures, and robot behavior into clear engineering explanations. |
| **Favorite Part** | Organizing ideas and explaining how Cheese works. |
| **Biggest Challenge** | Making sure every failure becomes useful evidence for improvement. |
| **Main Contribution** | Documentation, project structure, software explanation, engineering decisions, visual organization, and tuning analysis. |

</div>

### About Caylee

Hii! My name is **Caylee**, and this is my first time competing in WRO. I am really happy to be part of a competition that pushes us toward hard work, problem-solving, and personal growth.

In Go!Cheese, my role focuses on documentation, software explanation, engineering reasoning, and project organization. I work on making the README clear, structured, and complete so that anyone reading our repository can understand not only what Cheese does, but also why we made each decision.

I enjoy asking questions, understanding how things work, and turning confusing testing problems into explanations that make sense. For me, this project is not only about building a robot; it is also about showing our process, our teamwork, and our improvement through every test.

<p align="center">
  <a href="https://www.instagram.com/caymrr">
    <img src="https://img.shields.io/badge/Instagram-caymrr-FF69B4?style=for-the-badge&logo=instagram&logoColor=white">
  </a>
  <a href="mailto:cayleerios@gmail.com">
    <img src="https://img.shields.io/badge/Email-cayleerios%40gmail.com-4A90E2?style=for-the-badge&logo=gmail&logoColor=white">
  </a>
</p>

---

## ❀ Romina Mora ────୨ৎ────────୨ৎ────

<p align="center">
  <img src="https://img.shields.io/badge/Role-Programmer_&_Robot_Builder-FF8FAB?style=for-the-badge">
  <img src="https://img.shields.io/badge/Age-16-FFD43B?style=for-the-badge">
</p>

<p align="center">
  <img src="t-photos/Romina-photos/Romina%20pic.jpg" alt="Romina Mora" width="45%">
</p>

<div align="center">

| Category | Description |
| :--- | :--- |
| **Main Focus** | Programming, robot building, mechanical changes, code implementation, and testing support. |
| **Project Strength** | Turning ideas into physical robot changes and functional code. |
| **Favorite Part** | Solving challenges through building, coding, and testing. |
| **Biggest Challenge** | Adjusting the robot until the physical behavior matches the idea in the code. |
| **Main Contribution** | Programming, robot construction, mechanism adjustments, software implementation, and physical testing. |

</div>

### About Romina

Helloo!!! I’m **Romina**, and I am a very passionate gamer. I enjoy anything that represents a challenge, and this project has definitely been one of them. Since 2025, I have been interested in robotics, and in 2026 I finally had the chance to join a team and work on a real WRO robot.

In Go!Cheese, my role focuses on programming and robot building. I help turn ideas into real changes on the robot, whether that means adjusting the structure, modifying code, testing a new behavior, or helping Cheese move closer to the result we want.

I hope to keep learning from this experience so I can improve my skills for future competitions. For me, robotics is exciting because every problem feels like a challenge to solve, and every improvement shows that the work was worth it.

<p align="center">
  <img src="https://img.shields.io/badge/Socials-Reach_out_through_partner-lightgrey?style=for-the-badge">
</p>


## ❀ How Our Roles Connect ────୨ৎ────────୨ৎ────

<p align="center">
  <img src="https://img.shields.io/badge/Caylee-Documents_&_Explains-57C785?style=for-the-badge">
  <img src="https://img.shields.io/badge/Romina-Builds_&_Programs-FF8FAB?style=for-the-badge">
  <img src="https://img.shields.io/badge/Together-Test_Improve_Repeat-FFD43B?style=for-the-badge">
</p>

<div align="center">

| Caylee | Together | Romina |
| :--- | :--- | :--- |
| Organizes documentation | Share observations | Builds robot changes |
| Explains software logic | Discuss failures | Programs behavior |
| Writes engineering decisions | Compare test results | Adjusts mechanisms |
| Creates README structure | Choose next improvement | Tests physical changes |
| Connects evidence to reasoning | Improve Cheese step by step | Helps implement solutions |

</div>

Our roles are different, but they are connected in every part of the project. When the robot fails, we do not treat it as just a mistake. We treat it as information. One observation becomes a discussion, the discussion becomes a change, the change becomes a test, and the test becomes documentation.

---

## ❀ What Go!Cheese Means to Us ────୨ৎ────────୨ৎ────

Go!Cheese is more than the name of our team. It represents our first serious step into the WRO Future Engineers category, our learning process, and our determination to keep improving even when the robot does not behave the way we expected.

Throughout the season, Cheese has changed many times. We adjusted the structure, changed sensor strategies, improved lighting, modified software logic, worked on curve behavior, and documented the decisions behind each improvement. Every version taught us something different.

<p align="center">
  <strong>For us, Go!Cheese means learning by doing, improving through testing, and proving that a small team can still build something meaningful with creativity, discipline, and teamwork.</strong>
</p>

---

## ❀ Team Motto ────୨ৎ────────୨ৎ────

<p align="center">
  <strong>“Test it, fix it, explain it, and try again.”</strong>
</p>

<p align="center">
  <em>That is how Cheese keeps getting better.</em>
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
