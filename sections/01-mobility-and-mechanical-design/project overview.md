# ᯓ★ Engineering Documentation Overview ᯓ★

<p align="center">
  <img src="https://img.shields.io/badge/Project-WRO_2026_Future_Engineers-4A90E2?style=for-the-badge">
  <img src="https://img.shields.io/badge/Robot-Cheese-FFD43B?style=for-the-badge">
  <img src="https://img.shields.io/badge/Current_Version-v4-57C785?style=for-the-badge">
</p>

<p align="center">
  <em>The complete engineering story behind Cheese, our WRO Future Engineers 2026 robot.</em>
</p>

<p align="center">
  ✦ ─── ⋆⋅☆⋅⋆ ─── (❁´◡`❁) ─── ⋆⋅☆⋅⋆ ─── ✦
</p>

This repository documents how **Cheese** was designed, built, tested, tuned, and improved across multiple development versions. It explains not only what the robot is, but also **why each decision was made, how each system works, what problems appeared during testing, and how the design changed because of those problems**.

The current documented version is **Cheese v4**. This version became lighter, cleaner, more compact, and easier to inspect after removing unnecessary upper structure, simplifying the camera mount, shortening cable routing, and keeping only the support needed for movement, sensors, stability, and wiring organization.

---

## ❀ Project Snapshot ────୨ৎ────────୨ৎ────

<div align="center">

| Category | Current Description |
| :--- | :--- |
| **Competition** | WRO Future Engineers 2026 |
| **Robot Name** | Cheese |
| **Current Physical Version** | v4 |
| **Main Controller** | LEGO EV3 Brick |
| **Main Challenge Focus** | Open Challenge navigation and Obstacle Challenge detection |
| **Drive System** | EV3 Large Motor with rear-wheel drive |
| **Steering System** | EV3 Medium Motor with Ackermann-style front steering |
| **Sensors** | Ultrasonic sensors, color sensor, HuskyLens camera, lighting support |
| **Main v4 Improvement** | Reduced mass from approximately **888 g to 666 g** and simplified the structure |

</div>

This overview works as the main index for the engineering documentation. Each section focuses on a different subsystem, but all sections connect to the same idea: **Cheese improves when mechanical design, sensors, software, wiring, and testing are treated as one complete system**.

---

## ❀ Main Documentation Sections ────୨ৎ────────୨ৎ────

Click any section below to expand it.

---

<details>
<summary><strong>🔧 1. Mobility and Mechanical Design</strong> — how Cheese physically moves</summary>

<br>

This section explains the mechanical structure of Cheese, including the drivetrain, steering system, chassis layout, component placement, and structural choices. It focuses on how the robot moves, turns, supports its weight, and keeps its mechanical systems stable during testing.

The v4 update is especially important in this section because the robot became lighter and more compact. The mechanical documentation explains how this change affects acceleration, steering response, stability, inspection, and reproducibility.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **1.1 Mechanical Design** | [Open Document](sections/01-mobility-and-mechanical-design/1.1-mechanical-design.md) | Motors, wheels, torque, speed, mass reduction, and drivetrain reasoning. |
| **1.2 Structural Components** | [Open Document](sections/01-mobility-and-mechanical-design/1.2-structural-component.mds.md) | LEGO Technic parts, reinforcements, axles, pins, structural reliability, and v4 simplification. |
| **1.3 Steering and Drive** | [Open Document](sections/01-mobility-and-mechanical-design/1.3-steering-and-drive.md) | Rear-wheel drive, Ackermann steering, linkage behavior, steering stability, and v4 steering impact. |
| **1.4 Chassis Explanation** | [Open Document](sections/01-mobility-and-mechanical-design/1.4-chassis-explanation.md) | Chassis layout, weight distribution, sensor support, lights, EV3 placement, wiring space, and reproducibility. |

</div>

</details>

---

<details>
<summary><strong>🔋 2. Power and Sensor Architecture</strong> — how Cheese is powered and how it senses</summary>

<br>

This section explains the electronic and sensing architecture of Cheese. It documents how power is distributed, how sensors are selected and placed, how wiring is organized, and how calibration improves consistency during real runs.

This section connects strongly to the v4 redesign because the sensor layout became more compact, the ultrasonic sensors were lowered, cable routing became easier to inspect, and the camera support was simplified while keeping the camera forward-facing for obstacle detection.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **2.1 Power Supply and EV3** | [Open Document](sections/02-power-and-sensor-architecture/2.1-power-supply-and-ev3.md) | EV3 battery, motor power, sensor power, Arduino Nano, HuskyLens, and lights. |
| **2.2 Wiring Diagram** | [Open Document](sections/02-power-and-sensor-architecture/2.2-wiring-diagram.md) | EV3 ports, wiring layout, communication paths, cable organization, and subsystem connections. |
| **2.3 Sensor Selection and Placement** | [Open Document](sections/02-power-and-sensor-architecture/2.3-sensor-selection-and-placement.md) | Ultrasonic sensors, color sensor, HuskyLens, placement reasoning, and field geometry. |
| **2.4 Sensor Calibration** | [Open Document](sections/02-power-and-sensor-architecture/2.4-sensor-calibration.md) | Sensor testing, color readings, ultrasonic consistency, lighting support, and calibration decisions. |

</div>

</details>

---

<details>
<summary><strong>💻 3. Software Architecture and Obstacle Strategy</strong> — how Cheese thinks</summary>

<br>

This section explains the logic behind Cheese’s behavior. It covers how the robot uses wall following, PID-style corrections, curve counting, color detection, obstacle recognition, tuning, recovery logic, and final stopping decisions.

The software documentation is connected to the mechanical design because code decisions depend on the robot’s physical behavior. Steering response, speed layers, sensor placement, lighting, and structural stability all affect whether the software can make reliable decisions.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **3.0 Cheese Logic Overview** | [Open Document](sections/03-software-and-obstacle-strategy/3.0%20Cheese%20Logic%20Overview.md) | General software behavior and priority-based control. |
| **3.1 Algorithm Architecture** | [Open Document](sections/03-software-and-obstacle-strategy/3.1-algorithm-architecture.md) | PID, wall correction, curve logic, obstacle response, and final stop structure. |
| **3.2 Flowchart** | [Open Document](sections/03-software-and-obstacle-strategy/3.2-flowchart.md) | Visual explanation of Cheese’s main decision flow. |
| **3.3 Open Challenge** | [Open Document](sections/03-software-and-obstacle-strategy/3.3-open-challenge.md) | Wall following, curve detection, lap progress, and final stopping. |
| **3.4 Obstacle Challenge** | [Open Document](sections/03-software-and-obstacle-strategy/3.4-obstacle-challenge.md) | HuskyLens recognition, red/green obstacles, avoidance, and recovery. |
| **3.5 Corner Handling** | [Open Document](sections/03-software-and-obstacle-strategy/3.5-corner-handling.md) | Color confirmation, curve counting, curve exit, and post-curve recovery. |
| **3.6 Tuning Process** | [Open Document](sections/03-software-and-obstacle-strategy/3.6-tuning-process.md) | Curve aggressiveness, steering angles, color detection, parking, lighting, and testing adjustments. |

</div>

</details>

---

<details>
<summary><strong>⚙️ 4. Engineering Decisions</strong> — why Cheese is the way it is</summary>

<br>

This section explains the engineering reasoning behind the final design. It documents the decisions, failures, trade-offs, and improvements that shaped Cheese across its versions.

The goal of this section is to show that the final robot was not built by guessing. It was shaped by repeated testing, mechanical failures, sensor problems, lighting issues, steering instability, wiring limitations, and design trade-offs.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **4.1 Design Decision Log** | [Open Document](sections/04-engineering-decisions/4.1-design-decision-log.md) | Major design choices, constraints, trade-offs, v4 changes, and final decisions. |
| **4.2 What Did Not Work** | [Open Document](sections/04-engineering-decisions/4.2-what-didnt-work.md) | Failed ideas, unstable systems, sensor problems, lighting issues, mechanical issues, and lessons learned. |

</div>

</details>

---

<details>
<summary><strong>📦 5. Reproducibility</strong> — how to rebuild Cheese</summary>

<br>

This section supports anyone who wants to understand or rebuild Cheese. It includes the materials, components, build sequence, wiring preparation, sensor placement, and testing workflow.

Reproducibility matters because engineering documentation should allow another person to understand how the robot was assembled and why each component was placed where it was. The v4 photos and evidence links help make the final version easier to inspect and recreate.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **5.1 Bill of Materials** | [Open Document](sections/05-reproducibility/5.1-bill-of-materials.md) | Motors, sensors, EV3 parts, HuskyLens, Arduino Nano, lights, wiring, and Technic parts. |
| **5.2 Build Instructions** | [Open Document](sections/05-reproducibility/5.2-build-instructions.md) | Step-by-step construction, chassis, steering, sensors, lights, wiring, and calibration. |

</div>

</details>

---

<details>
<summary><strong>🧀 6. Other Resources</strong> — graphs, diagrams, models, and extra evidence</summary>

<br>

This section works as the final resource hub of the repository. It contains supplementary materials that support the main documentation, including Chart.js graphs, flowcharts, wiring references, models, calculation images, visual evidence, and extra technical resources.

These resources make the documentation easier to explore visually. They also support the engineering story by showing diagrams, comparisons, tuning evidence, and additional material that does not fit inside only one section.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **6.1 Additional Resources** | [Open Document](sections/06-other-resources/6.1-additional-resources.md) | Interactive graphs, diagrams, models, wiring resources, calibration references, evidence images, and final support materials. |

</div>

</details>

---

## ❀ How to Read This Repository ────୨ৎ────────୨ৎ────

The six sections are ordered to build on each other. The recommended reading path starts with the physical robot, then moves into sensors, software, decisions, reproducibility, and extra evidence.

<div align="center">

| Order | Section | Why It Comes Here |
| :---: | :--- | :--- |
| **1** | Mobility and Mechanical Design | First, understand how Cheese physically moves and supports its systems. |
| **2** | Power and Sensor Architecture | Then, understand how the robot is powered and how it senses the track. |
| **3** | Software and Obstacle Strategy | Next, understand how Cheese makes decisions during a run. |
| **4** | Engineering Decisions | After that, understand why the final choices were made and what failed before. |
| **5** | Reproducibility | Then, see how the final robot can be rebuilt and tested. |
| **6** | Other Resources | Finally, explore extra graphs, diagrams, models, calculations, and evidence. |

</div>

<p align="center">
  <strong>Recommended reading path:</strong><br>
  Mechanical design → sensors and power → software logic → engineering decisions → reproducibility → additional resources.
</p>

---

## ❀ Current Documentation Focus ────୨ৎ────────୨ৎ────

The current improvement focus of the documentation is to make the v4 design decisions clear and supported with evidence.

<div align="center">

| Focus Area | What We Are Showing |
| :--- | :--- |
| **Mechanical redesign** | Why v4 became lighter, cleaner, and more compact. |
| **Chassis reasoning** | How the chassis supports motors, sensors, wiring, lights, camera, and EV3 Brick. |
| **Sensor placement** | Why each sensor is placed according to what it needs to detect. |
| **Software tuning** | How steering, speed, curve behavior, and obstacle logic were adjusted through testing. |
| **Engineering decisions** | What failed, what changed, and why the final choices were made. |
| **Visual evidence** | Photos, diagrams, tables, flowcharts, and graphs that support the written explanation. |

</div>

This repository is written to show the full engineering process: planning, building, failing, testing, improving, and documenting the final result.

---

## ✦ Final Overview Summary ─── ⋆⋅☆⋅⋆ ───

Cheese is not only a robot that drives around a track. It is a complete engineering project where mechanical design, sensor placement, software logic, wiring, power, testing, and documentation all depend on each other.

The v4 redesign made the robot more intentional. Extra structure was removed, cables were shortened, the chassis became cleaner, and the robot became easier to inspect and explain. These changes support the main goal of the documentation: to show how every part of Cheese contributes to performance, reliability, and reproducibility.

<p align="center">
  <strong>Final overview lesson:</strong><br>
  A strong engineering repository does not only show the final robot. It explains the decisions, tests, failures, evidence, and improvements that created it.
</p>

<p align="center">
  ✦ ─── ⋆⋅☆⋅⋆ ─── (❁´◡`❁) ─── ⋆⋅☆⋅⋆ ─── ✦
</p>

<p align="center">
  <a href="#general-project-index">
    <img src="https://img.shields.io/badge/Go_to_General_Project_Index-FFD43B?style=for-the-badge">
  </a>
</p>
