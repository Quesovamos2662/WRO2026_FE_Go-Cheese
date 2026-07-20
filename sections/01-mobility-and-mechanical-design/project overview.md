# ᯓ★ Engineering Documentation Overview ᯓ★

<p align="center">
  <em>The complete engineering story behind Cheese, our WRO Future Engineers 2026 robot.</em>
</p>

This repository documents how Cheese was designed, built, tested, tuned, and improved across multiple development versions. The documentation is organized into **six main engineering sections**, each focused on a different part of the robot. Together, these sections explain not only what Cheese is, but also **why each decision was made, how each system works, and what we learned through testing**.

Click any section below to expand it.

---

<details>
<summary><strong>🔧 1. Mobility and Mechanical Design</strong> — how Cheese physically moves</summary>

<br>

This section explains the mechanical structure of Cheese, including the drivetrain, steering system, chassis layout, component placement, and structural choices. It focuses on how the robot moves, turns, supports its weight, and keeps its mechanical systems stable during testing.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **1.1 Mechanical Design** | [Open Document](sections/01-mobility-and-mechanical-design/1.1-mechanical-design.md) | Motors, wheels, torque, speed, and drivetrain reasoning. |
| **1.2 Structural Components** | [Open Document](sections/01-mobility-and-mechanical-design/1.2-structural-component.mds.md) | LEGO Technic parts, reinforcements, axles, pins, and structural reliability. |
| **1.3 Steering and Drive** | [Open Document](sections/01-mobility-and-mechanical-design/1.3-steering-and-drive.md) | Rear-wheel drive, Ackermann steering, linkage behavior, and movement stability. |
| **1.4 Chassis Explanation** | [Open Document](sections/01-mobility-and-mechanical-design/1.4-chassis-explanation.md) | Chassis layout, weight distribution, sensor support, lights, and wiring space. |

</div>

</details>

---

<details>
<summary><strong>🔋 2. Power and Sensor Architecture</strong> — how Cheese is powered and how it senses</summary>

<br>

This section explains the electronic and sensing architecture of Cheese. It documents how power is distributed, how sensors are selected and placed, how wiring is organized, and how calibration improves consistency during real runs.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **2.1 Power Supply and EV3** | [Open Document](sections/02-power-and-sensor-architecture/2.1-power-supply-and-ev3.md) | EV3 battery, motor power, sensor power, Arduino Nano, HuskyLens, and lights. |
| **2.2 Wiring Diagram** | [Open Document](sections/02-power-and-sensor-architecture/2.2-wiring-diagram.md) | EV3 ports, wiring layout, communication paths, and subsystem connections. |
| **2.3 Sensor Selection and Placement** | [Open Document](sections/02-power-and-sensor-architecture/2.3-sensor-selection-and-placement.md) | Ultrasonic sensors, color sensor, HuskyLens, and placement reasoning. |
| **2.4 Sensor Calibration** | [Open Document](sections/02-power-and-sensor-architecture/2.4-sensor-calibration.md) | Sensor testing, color readings, ultrasonic consistency, and lighting support. |

</div>

</details>

---

<details>
<summary><strong>💻 3. Software Architecture and Obstacle Strategy</strong> — how Cheese thinks</summary>

<br>

This section explains the logic behind Cheese’s behavior. It covers how the robot uses PID, wall protection, color detection, curve counting, obstacle recognition, tuning, recovery logic, and final stopping decisions.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **3.0 Cheese Logic Overview** | [Open Document](sections/03-software-and-obstacle-strategy/3.0%20Cheese%20Logic%20Overview.md) | General software behavior and priority-based control. |
| **3.1 Algorithm Architecture** | [Open Document](sections/03-software-and-obstacle-strategy/3.1-algorithm-architecture.md) | PID, wall correction, curve logic, obstacle response, and final stop structure. |
| **3.2 Flowchart** | [Open Document](sections/03-software-and-obstacle-strategy/3.2-flowchart.md) | Visual explanation of Cheese’s main decision flow. |
| **3.3 Open Challenge** | [Open Document](sections/03-software-and-obstacle-strategy/3.3-open-challenge.md) | Wall following, curve detection, lap progress, and final stopping. |
| **3.4 Obstacle Challenge** | [Open Document](sections/03-software-and-obstacle-strategy/3.4-obstacle-challenge.md) | HuskyLens recognition, red/green obstacles, avoidance, and recovery. |
| **3.5 Corner Handling** | [Open Document](sections/03-software-and-obstacle-strategy/3.5-corner-handling.md) | Color confirmation, curve counting, curve exit, and post-curve recovery. |
| **3.6 Tuning Process** | [Open Document](sections/03-software-and-obstacle-strategy/3.6-tuning-process.md) | Curve aggressiveness, steering angles, color detection, parking, and lighting tuning. |

</div>

</details>

---

<details>
<summary><strong>⚙️ 4. Engineering Decisions</strong> — why Cheese is the way it is</summary>

<br>

This section explains the engineering reasoning behind the final design. It documents the decisions, failures, tradeoffs, and improvements that shaped Cheese v3.

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **4.1 Design Decision Log** | [Open Document](sections/04-engineering-decisions/4.1-design-decision-log.md) | Major design choices, constraints, tradeoffs, and final decisions. |
| **4.2 What Did Not Work** | [Open Document](sections/04-engineering-decisions/4.2-what-didnt-work.md) | Failed ideas, unstable systems, sensor problems, lighting issues, and lessons learned. |

</div>

</details>

---

<details>
<summary><strong>📦 5. Reproducibility</strong> — how to rebuild Cheese</summary>

<br>

This section supports anyone who wants to understand or rebuild Cheese v3. It includes the materials, components, build sequence, wiring preparation, sensor placement, and testing workflow.

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

<div align="center">

| Subsection | Link | Focus |
| :--- | :--- | :--- |
| **6.1 Additional Resources** | [Open Document](sections/06-other-resources/6.1-additional-resources.md) | Interactive graphs, diagrams, models, wiring resources, calibration references, evidence images, and final support materials. |

</div>

This section helps close the documentation by showing the evidence behind the robot’s development process. It connects the technical story to visual resources that make the project easier to explore.

</details>

---

## ❀ How to Read This Repository ────୨ৎ────────୨ৎ────

The six sections are ordered to build on each other:

<div align="center">

| Order | Section | Why It Comes Here |
| :---: | :--- | :--- |
| **1** | Mobility and Mechanical Design | First, understand how Cheese physically moves and supports its systems. |
| **2** | Power and Sensor Architecture | Then, understand how the robot is powered and how it senses the track. |
| **3** | Software and Obstacle Strategy | Next, understand how Cheese makes decisions during a run. |
| **4** | Engineering Decisions | After that, understand why the final choices were made. |
| **5** | Reproducibility | Then, see how the final robot can be rebuilt and tested. |
| **6** | Other Resources | Finally, explore extra graphs, diagrams, models, calculations, and evidence. |

</div>

<p align="center">
  <strong>Recommended reading path:</strong><br>
  Mechanical design → sensors and power → software logic → engineering decisions → reproducibility → additional resources.
</p>

---

<p align="center">
  ✦ ─── ⋆⋅☆⋅⋆ ─── (❁´◡`❁) ─── ⋆⋅☆⋅⋆ ─── ✦
</p>

<p align="center">
  <a href="#general-project-index">
    <img src="https://img.shields.io/badge/Go_to_General_Project_Index-FFD43B?style=for-the-badge">
  </a>
</p>
