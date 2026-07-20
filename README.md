

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

- [**General Project Overview**](sections/01-mobility-and-mechanical-design/project%20overview.md)
  - Introduces Cheese as our WRO Future Engineers robot.
  - Explains the robot’s main purpose, competition context, and general design direction.
  - Summarizes how the mechanical structure, sensors, software, testing process, and final strategy work together.

---

- **1. Mobility and Mechanical Design**
  - [**1.1 Mechanical Design**](sections/01-mobility-and-mechanical-design/1.1-mechanical-design.md)
    - Explains the main mechanical choices behind Cheese’s movement system.
    - Includes motor selection, wheel choice, torque and speed reasoning, and drivetrain testing observations.
    - Justifies why the EV3 Large Motor is used for propulsion and the EV3 Medium Motor is used for steering.

  - [**1.2 Structural Components**](sections/01-mobility-and-mechanical-design/1.2-structural-component.mds.md)
    - Documents the LEGO Technic components used to build the robot’s structure.
    - Explains the role of liftarms, pins, axles, connectors, and reinforced sections.
    - Connects structural choices to durability, alignment, and mechanical reliability.

  - [**1.3 Steering and Drive**](sections/01-mobility-and-mechanical-design/1.3-steering-and-drive.md)
    - Describes the rear-wheel drive system and Ackermann steering mechanism.
    - Explains how propulsion and steering work together during straight movement, curves, and corrections.
    - Includes reasoning about steering response, linkage movement, drivetrain stability, and control.

  - [**1.4 Chassis Explanation**](sections/01-mobility-and-mechanical-design/1.4-chassis-explanation.md)
    - Explains the chassis layout and how the robot’s body supports each subsystem.
    - Describes weight distribution, mounting points, upper tower support, and component placement.
    - Shows how the chassis evolved to support sensors, lights, wiring, and repeated testing.

---

- **2. Power and Sensor Architecture**
  - [**2.1 Power Supply and EV3**](sections/02-power-and-sensor-architecture/2.1-power-supply-and-ev3.md)
    - Explains how Cheese is powered during operation.
    - Describes the EV3 rechargeable battery, motor power, sensor power, Arduino Nano power, HuskyLens power, and external lighting battery.
    - Connects the power architecture to reliability, safe subsystem separation, and easier debugging.

  - [**2.2 Wiring Diagram**](sections/02-power-and-sensor-architecture/2.2-wiring-diagram.md)
    - Shows how motors, sensors, Arduino Nano, HuskyLens, and lights are connected.
    - Documents the EV3 input/output ports and the communication path between components.
    - Helps reproduce the robot’s electrical layout and avoid wiring mistakes.

  - [**2.3 Sensor Selection and Placement**](sections/02-power-and-sensor-architecture/2.3-sensor-selection-and-placement.md)
    - Explains why each sensor was selected and where it is placed on the robot.
    - Covers ultrasonic wall sensing, color sensor floor detection, and HuskyLens obstacle recognition.
    - Connects sensor placement to navigation accuracy, curve detection, obstacle strategy, and reliability.

  - [**2.4 Sensor Calibration**](sections/02-power-and-sensor-architecture/2.4-sensor-calibration.md)
    - Describes how sensors are checked and adjusted before testing.
    - Explains calibration for ultrasonic readings, color detection, HuskyLens recognition, and lighting support.
    - Helps make the robot’s sensing behavior more consistent between runs.

---

- **3. Software and Obstacle Strategy**
  - [**3.0 Cheese Logic Overview**](sections/03-software-and-obstacle-strategy/3.0%20Cheese%20Logic%20Overview.md)
    - Gives a general overview of Cheese’s software behavior.
    - Explains the robot’s priority-based decision system and main control flow.
    - Summarizes how normal driving, wall protection, curve handling, obstacle logic, tuning, and parking connect.

  - [**3.1 Algorithm Architecture**](sections/03-software-and-obstacle-strategy/3.1-algorithm-architecture.md)
    - Explains the internal structure of the robot’s code.
    - Describes the main behavior layers, including PID centering, wall correction, curve logic, recovery, obstacle response, and final stop logic.
    - Shows how software priorities prevent different behaviors from interfering with each other.

  - [**3.2 Flowchart**](sections/03-software-and-obstacle-strategy/3.2-flowchart.md)
    - Presents the general logic flow used by Cheese during a run.
    - Helps visualize how the robot initializes, reads sensors, chooses behaviors, counts curves, and stops.
    - Connects the written algorithm to a clearer visual representation.

  - [**3.3 Open Challenge**](sections/03-software-and-obstacle-strategy/3.3-open-challenge.md)
    - Explains the strategy used for the Open Challenge.
    - Describes wall following, PID centering, protected wall correction, color-based curve detection, lap tracking, and final stop planning.
    - Focuses on consistent autonomous movement without red or green obstacles.

  - [**3.4 Obstacle Challenge**](sections/03-software-and-obstacle-strategy/3.4-obstacle-challenge.md)
    - Explains how Cheese handles red and green obstacles.
    - Describes how the HuskyLens, Arduino Nano, lighting system, and movement logic support obstacle recognition.
    - Connects obstacle detection to steering decisions, controlled avoidance, recovery behavior, and safe path planning.

  - [**3.5 Corner Handling**](sections/03-software-and-obstacle-strategy/3.5-corner-handling.md)
    - Explains how Cheese detects, enters, counts, and exits corners.
    - Describes the relationship between color detection, confirmed blue/orange pairing, curve counting, and post-curve recovery.
    - Shows why corner handling is separated from normal PID driving.

  - [**3.6 Tuning Process**](sections/03-software-and-obstacle-strategy/3.6-tuning-process.md)
    - Documents how movement values were adjusted during testing.
    - Explains tuning for curve aggressiveness, steering angles, PID response, wall protection, color detection, parking, and obstacle recognition.
    - Shows how testing results influenced software changes and calibration decisions.

---

- **4. Engineering Decisions**
  - [**4.1 Design Decision Log**](sections/04-engineering-decisions/4.1-design-decision-log.md)
    - Explains the major decisions that shaped Cheese v3.
    - Includes controller choice, Arduino role, code simplification, sensor changes, lighting system, mechanical reinforcement, curve tuning, and parking refinement.
    - Focuses on why each decision was made, what constraint caused it, and what tradeoff it involved.

  - [**4.2 What Did Not Work**](sections/04-engineering-decisions/4.2-what-didnt-work.md)
    - Documents the ideas, systems, and configurations that failed during development.
    - Explains issues with Arduino main control, long code, infrared sensing, front ultrasonic sensing, lighting, broken pins, wide curves, and parking.
    - Shows how each failure became evidence for a later design improvement.

---

- **5. Reproducibility**
  - [**5.1 Bill of Materials**](sections/05-reproducibility/5.1-bill-of-materials.md)
    - Lists the main components required to rebuild Cheese v3.
    - Includes motors, sensors, EV3 components, HuskyLens, Arduino Nano, lights, battery, LEGO Technic parts, and structural pieces.
    - Connects each component to its role in the final robot architecture.

  - [**5.2 Build Instructions**](sections/05-reproducibility/5.2-build-instructions.md)
    - Provides step-by-step instructions to rebuild Cheese v3.
    - Explains the build order, chassis construction, drive system, Ackermann steering, sensor placement, wiring, lights, calibration, and testing workflow.
    - Helps another builder reproduce the robot and understand the purpose of each subsystem.

---

- **6. Additional Resources**
  - [**6.1 Additional Resources**](sections/06-other-resources/6.1-additional-resources.md)
    - Contains supporting materials that do not fit directly into the main engineering sections.
    - Can include testing graphs, code-based data, sensor logs, extra diagrams, future 3D model references, and development notes.
    - Supports deeper analysis of Cheese’s performance and testing process.

---

- **7. Source Code**
  - [**Source Code Folder**](src/)
    - Contains the robot’s program files and code versions.
    - Includes the software used to control movement, steering, sensors, curve logic, obstacle behavior, tuning, and final stopping.
    - Supports reproducibility by connecting the documentation to the actual robot logic.

---

- **8. Digital Models and Schemes**
  - [**Robot Models**](models/)
    - Contains digital model references for Cheese’s chassis, steering system, and version-based development.
    - Helps document the robot’s structure beyond physical photos.

  - [**Schemes**](schemes/)
    - Contains supporting diagrams and technical reference files.
    - Includes wiring and robot reference documents such as `finalrobot.pdf` and wiring diagram images.

---

- **9. Visual Documentation**
  - [**Version 1 Photos**](v-photos/v1/)
    - Shows the first physical version of Cheese.
    - Helps compare early mechanical ideas with later improvements.

  - [**Version 2 Photos**](v-photos/v2/)
    - Documents the second version of the robot.
    - Shows changes in structure, sensor placement, steering layout, and design direction before the final v3 design.

  - [**Version 3 Photos**](v-photos/v3/)
    - Shows the current Cheese v3 build from multiple angles.
    - Includes front, back, side, top, bottom, sensor placement, camera placement, and dual-light system photos.

  - [**Cheese v3 Named Angles**](v-photos/v3/named%20angles/)
    - Contains labeled images of the final robot.
    - Identifies the EV3 Brick, motors, sensors, HuskyLens, Arduino Nano, lights, and main structural components.

---

- **10. Team Documentation**
  - [**Team Photos**](t-photos/)
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
  <img src="t-photos/Romina-photos/Romina%20pic.jpg" alt="Romina Mora" width="45%">
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
