# ᯓ★ Source Code Documentation ᯓ★

<p align="center">
  <img src="https://img.shields.io/badge/Folder-src-4A90E2?style=for-the-badge">
  <img src="https://img.shields.io/badge/Robot-Cheese_v3-FFD43B?style=for-the-badge">
  <img src="https://img.shields.io/badge/Focus-Code_Evolution_+_Logic-57C785?style=for-the-badge">
</p>

<p align="center">
  <em>This folder contains the program files developed for Cheese during the WRO Future Engineers 2026 season. The files are organized by challenge type and development stage, showing how the robot’s logic evolved through testing, failures, tuning, and redesign.</em>
</p>

<p align="center">
  ✦ ─── ⋆⋅☆⋅⋆ ─── (❁´◡`❁) ─── ⋆⋅☆⋅⋆ ─── ✦
</p>

---

## ❀ Folder Purpose ────୨ৎ────────୨ৎ────

The `src/` folder is used to store Cheese’s code versions. Instead of keeping only one final program, we kept different versions to document the development process. This helps show how the robot’s software changed as we tested different movement strategies, curve methods, sensor logic, and stopping systems.

Not every file in this folder is meant to be used as a final competition program. Some files are experimental, some are older versions, and some were kept as evidence of what was tested before reaching the current logic.

This is important because Cheese’s final behavior was not created in one attempt. The code evolved through repeated testing, including problems with wall following, curve detection, color readings, parking accuracy, obstacle detection, and code complexity.

---

## ❀ Source Code Structure ────୨ৎ────────୨ৎ────

```text
src/
├── code_obstacles/
│   └── idk
│
├── code_open/
│   ├── 14.py
│   ├── 15.py
│   ├── 15_open_color_sensor_curves_rear_us_reference_...
│   ├── 18.py
│   ├── 19.py
│   ├── 7.py
│   ├── A2.py
│   └── A3.py
│
└── v2 coding/
    └── pidWITHstop.py
```

---

## ❀ Code Folder Overview ────୨ৎ────────୨ৎ────

<div align="center">

| Folder | Status | Purpose |
| :--- | :--- | :--- |
| **`code_open/`** | Main development folder | Contains the Open Challenge code versions used to test wall following, curve detection, lap counting, and final stopping behavior. |
| **`code_obstacles/`** | Broken / incomplete | Contains obstacle-related experiments. This folder is not considered final because the obstacle code was still unstable and not ready for reliable competition use. |
| **`v2 coding/`** | Older version | Contains earlier PID and stopping logic from the v2 development stage. It is kept as evidence of the code evolution before Cheese v3. |

</div>

---

## ❀ Open Challenge Code Logic ────୨ৎ────────୨ৎ────

The most developed logic is inside the `code_open/` folder. These files focus on the **Open Challenge**, where Cheese must drive around the track without obstacles, complete the required laps, detect curves, and stop after the run.

The general Open Challenge logic follows this structure:

```text
1. Initialize motors and sensors.
2. Wait for the start command.
3. Read ultrasonic sensors and color sensor.
4. Use PID or wall correction to stay between the walls.
5. Detect floor colors used for curve tracking.
6. Confirm color readings before accepting them.
7. Count completed curves using color logic.
8. Track lap progress through curve count.
9. Activate final stopping logic after the required progress.
10. Stop the robot safely.
```

This structure helped separate the robot’s behavior into different responsibilities. Ultrasonic sensors support wall awareness, the color sensor supports curve counting, and the drive/steering motors execute the movement decisions.

---

## ❀ Main Behavior Layers ────୨ৎ────────୨ৎ────

Cheese’s software does not rely on only one control behavior. Instead, it uses several behavior layers that work together.

<div align="center">

| Behavior Layer | Purpose |
| :--- | :--- |
| **Normal PID Driving** | Keeps Cheese centered between the walls during stable movement. |
| **Wall Protection** | Overrides normal movement when the robot gets too close to a wall. |
| **Color Detection** | Reads floor markers used to identify curve progress. |
| **Curve Counting** | Tracks completed curves and connects them to lap progress. |
| **Post-Curve Recovery** | Helps the robot stabilize after completing a curve. |
| **Final Stop Logic** | Stops the robot after the required Open Challenge progress is completed. |

</div>

This layered structure was necessary because one behavior alone was not reliable enough. PID helped with normal driving, but it could not solve every situation. Wall protection was needed when Cheese got too close to a wall. Color logic was needed to track progress. Recovery was needed because the robot often exited curves at difficult angles.

---

## ❀ Code Evolution ────୨ৎ────────୨ৎ────

The code evolved through many tests. Early versions focused mainly on basic movement and PID correction. Later versions added curve detection, color logic, wall protection, lap counting, and final stopping behavior.

<div align="center">

| Stage | Main Focus | What Changed |
| :--- | :--- | :--- |
| **Early PID versions** | Basic wall following | The robot used ultrasonic readings to stay between walls, but the movement was not always consistent after curves. |
| **v2 code** | PID with stopping attempts | Older logic tested basic stopping and control behavior, but it was not reliable enough for the final robot. |
| **Open Challenge experiments** | Curve detection and lap tracking | Different versions tested how to count curves, detect colors, and connect curve progress to the final stop. |
| **Color-based curve versions** | Blue/orange marker detection | The color sensor was used to detect floor markers and improve curve counting. |
| **Tuning versions** | Stability and reliability | Speed, steering response, wall protection, color confirmation, and curve logic were adjusted through repeated tests. |
| **Obstacle experiments** | Camera-based obstacle detection | Early obstacle code was tested but kept separate because it was unstable and not final. |

</div>

The code history shows that Cheese’s software was developed through trial, testing, and correction. Each version helped identify what needed to change.

---

## ❀ Open Challenge Version Notes ────୨ৎ────────୨ৎ────

The `code_open/` folder contains several versions. These files should be understood as part of the testing history, not as identical final programs.

<div align="center">

| File / Version | Purpose |
| :--- | :--- |
| **`7.py`** | Earlier Open Challenge experiment. Kept as part of the code history. |
| **`14.py`** | Open Challenge testing version used during development. |
| **`15.py`** | Main experimental branch for color sensor curves, steering behavior, and navigation improvements. |
| **`18.py`** | Additional Open Challenge test version. |
| **`19.py`** | Later Open Challenge test version, used during curve and movement experiments. |
| **`A2.py`** | Alternative test version for Open Challenge behavior. |
| **`A3.py`** | Alternative test version for Open Challenge behavior. |
| **`15_open_color_sensor_curves_rear_us_reference_...`** | Experimental version involving color-sensor curve logic and rear ultrasonic reference ideas. This is kept as evidence, but it is not the main documented final strategy. |

</div>

Because several files were created during testing, the most important thing is not the file number alone, but the logic being tested inside each version. Some versions focused on curves, others on parking, and others on sensor behavior.

---

## ❀ Obstacle Code Status ────୨ৎ────────୨ৎ────

The `code_obstacles/` folder is currently marked as **broken / incomplete**.

This folder contains obstacle-related experiments, but it is not considered a final working version. The obstacle challenge required stable red and green obstacle detection, lighting support, camera communication, and safe avoidance behavior. During testing, this logic was harder to stabilize because the HuskyLens camera was affected by lighting conditions and recognition consistency.

For this reason, the obstacle code is kept in the repository as development evidence, but it should not be used as the final reference for a reliable competition run.

<div align="center">

| Obstacle Code Area | Status |
| :--- | :--- |
| **Obstacle recognition** | Experimental |
| **Camera-based decision logic** | Not fully stable |
| **Avoidance movement** | Still needs refinement |
| **Lighting dependency** | Requires more calibration |
| **Final reliability** | Not final |

</div>

The obstacle strategy is documented in the software section, but the actual obstacle code remains under development.

Related documentation:

<div align="center">

| Document | Link |
| :--- | :--- |
| **Obstacle Challenge** | [Open Document](../sections/03-software-and-obstacle-strategy/3.4-obstacle-challenge.md) |
| **Sensor Calibration** | [Open Document](../sections/02-power-and-sensor-architecture/2.4-sensor-calibration.md) |
| **Tuning Process** | [Open Document](../sections/03-software-and-obstacle-strategy/3.6-tuning-process.md) |

</div>

---

## ❀ Main Open Challenge Logic Summary ────୨ৎ────────୨ৎ────

The Open Challenge code is based on the idea that Cheese needs to drive, correct, detect, count, and stop in a controlled order.

```text
Start
 ↓
Initialize sensors and motors
 ↓
Begin movement
 ↓
Read ultrasonic sensors
 ↓
Read color sensor
 ↓
Choose behavior:
   - Normal PID driving
   - Wall protection
   - Curve handling
   - Post-curve recovery
 ↓
Confirm color events
 ↓
Count completed curves
 ↓
Check lap progress
 ↓
Activate final stop logic
 ↓
Stop
```

This logic connects the robot’s physical movement to its software state. Cheese does not simply drive forward; it continuously reacts to sensor readings and updates its internal progress.

---

## ❀ Why the Code Needed Many Versions ────୨ৎ────────୨ৎ────

The code needed many versions because the robot’s real behavior changed depending on the track, lighting, sensor readings, steering angle, and speed. A value that worked in one test could fail in another.

Some of the main problems we tried to solve through code changes were:

<div align="center">

| Problem | Why It Mattered |
| :--- | :--- |
| **Curves too wide or too sharp** | A bad curve angle could cause Cheese to hit a wall after the turn. |
| **Color sensor inconsistency** | If the robot missed a marker, the curve count became wrong. |
| **Parking descalibration** | If the robot counted wrong or stopped late, it did not finish where expected. |
| **Wall correction too aggressive** | Strong corrections could make the robot zig-zag or hit the opposite wall. |
| **Wall correction too weak** | Weak corrections could allow the robot to drift into the wall. |
| **Obstacle detection instability** | Irregular lighting affected camera recognition. |
| **Code complexity** | Long code made it harder to debug and tune specific behaviors. |

</div>

Because of these problems, the code was adjusted gradually. We changed values, tested the robot again, observed the behavior, and kept improving.

---

## ❀ Final Software Direction ────୨ৎ────────୨ৎ────

The final software direction for Cheese prioritizes **clear behavior layers** instead of one large, confusing control structure.

The most important software decisions were:

```text
Use ultrasonic sensors for wall awareness.
Use PID for normal centering.
Use wall protection when the robot is too close to walls.
Use the color sensor to support curve counting.
Use confirmation logic to reduce false color readings.
Use curve count as a progress reference.
Use final stop logic after the required run progress.
Keep obstacle code separate until it becomes stable.
```

This approach made the software easier to test and explain. It also made the documentation stronger because each behavior has a clear purpose.

---

## ❀ Related Documentation ────୨ৎ────────୨ৎ────

For a deeper explanation of Cheese’s software and testing process, visit these sections:

<div align="center">

| Section | Link |
| :--- | :--- |
| **3.0 Cheese Logic Overview** | [Open Document](../sections/03-software-and-obstacle-strategy/3.0%20Cheese%20Logic%20Overview.md) |
| **3.1 Algorithm Architecture** | [Open Document](../sections/03-software-and-obstacle-strategy/3.1-algorithm-architecture.md) |
| **3.2 Flowchart** | [Open Document](../sections/03-software-and-obstacle-strategy/3.2-flowchart.md) |
| **3.3 Open Challenge** | [Open Document](../sections/03-software-and-obstacle-strategy/3.3-open-challenge.md) |
| **3.4 Obstacle Challenge** | [Open Document](../sections/03-software-and-obstacle-strategy/3.4-obstacle-challenge.md) |
| **3.5 Corner Handling** | [Open Document](../sections/03-software-and-obstacle-strategy/3.5-corner-handling.md) |
| **3.6 Tuning Process** | [Open Document](../sections/03-software-and-obstacle-strategy/3.6-tuning-process.md) |

</div>

---

## ❀ Final Note ────୨ৎ────────୨ৎ────

The `src/` folder is not only a place to store code. It shows the evolution of Cheese’s logic across the season. Each version represents a test, an adjustment, or a problem that helped guide the next improvement.

<p align="center">
  <strong>The final code direction for Cheese is based on testing, simplification, sensor feedback, curve counting, and controlled behavior priorities.</strong>
</p>

<p align="center">
  ✦ ─── ⋆⋅☆⋅⋆ ─── (❁´◡`❁) ─── ⋆⋅☆⋅⋆ ─── ✦
</p>

<p align="center">
  <a href="../README.md">
    <img src="https://img.shields.io/badge/Back_to_Main_README-FFD43B?style=for-the-badge">
  </a>
</p>
