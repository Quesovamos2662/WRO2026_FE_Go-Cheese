# ᯓ★ Engineering Documentation Overview ᯓ★

<p align="center">
  <em>The complete engineering story behind Cheese, our WRO Future Engineers 2026 robot.</em>
</p>

This repository documents everything about how **Cheese** was designed, built, tested, and improved across three versions. The documentation is split into five sections, each covering one area of the robot. Every section stands on its own, but together they form a complete account: not just what the robot is, but why every part of it is the way it is, and what we learned getting there.

Click any section below to expand it.

---

<details>
<summary><b>🔧 1. Mobility & Mechanical Design</b> — how Cheese physically moves</summary>

<br>

This section covers the physical machine: the parts that make Cheese drive, steer, and hold its shape.

**What's inside:**
- **1.1 Mechanical Components** — the Large Motor that drives the rear axle and the Medium Motor that steers the front, plus the wheels. Why each was chosen, how they work together, and the theoretical top-speed calculation (~0.5 m/s).
- **1.2 Structural Components** — the liftarms, pins, and axles that form the frame, how they give rigidity, and where they cost us weight.
- **1.3 Steering & Drive Mechanism** — Ackermann geometry explained with the math, how we built the linkage, what broke, and the steering timing problem we are still chasing.
- **1.4 Chassis Explanation** — how the chassis is assembled around the EV3, and its evolution across three versions.

**The core idea:** force at the rear, finesse at the front. A powerful motor for traction, a light fast one for precise steering. Every mechanical choice traces back to that split.

**The honest part:** the drivetrain never fails us, the motors never stall and the tires never slip. But the steering still fights a timing problem on fast corners, and the chassis carries weight we could shed with smarter part placement.

</details>

---

<details>
<summary><b>🔋 2. Power & Sensor Architecture</b> — how Cheese is powered and how it senses</summary>

<br>

This section covers where the robot's energy comes from and how it perceives the track.

**What's inside:**
- **2.1 Power Supply & EV3** — the single 2050 mAh battery that runs everything, and why a draining battery slows the robot and makes it crash.
- **2.2 Wiring Diagram** — how every component connects.
- **2.3 Sensor Selection & Placement** — two ultrasonic sensors for the walls, a color sensor for counting corners, the HuskyLens for pillars, and why we chose each.
- **2.4 Sensor Calibration** — how the color sensor was taught our track's lines, and why the ultrasonics run uncalibrated.

**The core idea:** everything runs off one supply, and every sensor earned its place by replacing something that did not work.

**The honest part:** the camera dies before the motors do when the battery runs low, because it sits at the end of the power chain. We lose vision before we lose motion, and we manage it by never starting a run on a low battery.

</details>

---

<details>
<summary><b>💻 3. Software Architecture & Obstacle Strategy</b> — how Cheese thinks</summary>

<br>

This section covers the program running on the EV3: how it decides, corner by corner, what to do.

**What's inside:**
- **3.0 Logic Overview** — the whole software in one map.
- **3.1 Algorithm Architecture** — the main loop, the state the robot carries, the priority chain, the PID controller, and the full constant reference.
- **3.2 Flowchart** — one decision cycle, visualized.
- **3.3 Open Challenge Logic** — corner counting and the encoder-based parking that measures its own lap length.
- **3.4 Obstacle Challenge Strategy** — pillar avoidance *(camera integration in progress)*.
- **3.5 Corner & Edge Handling** — how colors are detected and how curves are driven.
- **3.6 Tuning Process** — how we arrived at every value.

**The core idea:** minimum sufficient logic. We cut the program from over 1000 lines to roughly 300, not by removing features, but by fixing mechanical problems in hardware instead of compensating for them in code.

**The honest part:** this is the section where we scored a 0 at our regional. Everything here is our answer to that.

</details>

---

<details>
<summary><b>⚙️ 4. Engineering Decisions</b> — why Cheese is the way it is</summary>

<br>

This section steps back from the components and documents the reasoning behind them.

**What's inside:**
- **4.1 Design Decision Log** — the choices we made, the alternatives we rejected, and why.
- **4.2 What Didn't Work** — the failures we learned the most from.

**The core idea:** we can name and explain every strength and every weakness of this robot. That understanding is what let us improve it across three versions.

**The honest part:** this entire section is built on things that went wrong. The sensor we changed three times, the chassis we lengthened and then shortened, the software we deleted. Our best decisions came from our clearest failures.

</details>

---

<details>
<summary><b>📦 5. Reproducibility</b> — how to rebuild Cheese</summary>

<br>

This section is written for someone who wants to reconstruct our robot.

**What's inside:**
- **5.1 Bill of Materials** — every part and quantity.
- **5.2 Build Instructions** — how to assemble Cheese as we did.

**The core idea:** documentation is only complete if someone else could follow it and end up with the same robot.

</details>

---

## ❀ How to Read This Repository ────୨ৎ────────୨ৎ────

The five sections are ordered to build on each other:
