# ᯓ★ Engineering Documentation Overview ᯓ★

This repository documents the full engineering process behind **Cheese**, our autonomous robot for WRO Future Engineers 2026. The documentation is organized into five sections, each mapping to one area of the robot's design. This overview explains what each section covers and how they fit together. Every section lives in its own folder and can be read on its own, but together they tell the complete story of how Cheese was built, why it works the way it does, and what we learned making it.

---

## ❀ 1. Mobility & Mechanical Design ────୨ৎ────────୨ৎ────

How Cheese physically moves. This section covers the two motors (a Large Motor driving the rear axle, a Medium Motor steering the front through Ackermann geometry), the wheels, the structural parts that hold the frame together, and the chassis itself. It documents the theoretical top-speed calculation, the steering geometry with its math, and the three versions the chassis went through before it was stable.

**The core idea:** force at the rear, finesse at the front. Every mechanical choice traces back to that split.

---

## ❀ 2. Power & Sensor Architecture ────୨ৎ────────୨ৎ────

How Cheese is powered and how it senses the world. This section covers the single EV3 battery that runs everything, why a draining battery changes the robot's behavior, the wiring that connects the components, and the sensors themselves: two ultrasonic sensors for the walls, a color sensor for counting corners, and a HuskyLens camera for the pillars. It also documents how each sensor is calibrated and where each one fails.

**The core idea:** everything runs off one supply, and the sensor we replaced three times taught us to match the sensor to the question, not the question to the sensor.

---

## ❀ 3. Software Architecture & Obstacle Strategy ────୨ৎ────────୨ৎ────

How Cheese thinks. This section covers the program that runs on the EV3: a single loop that reads the sensors, counts the corners, and steers through a priority chain built on a PID controller. It documents the full algorithm, the state the robot carries, every tunable constant, the challenge strategies, and the tuning process that got each value to where it is.

**The core idea:** minimum sufficient logic. We cut the program from over 1000 lines to roughly 300 by fixing mechanical problems in hardware instead of compensating for them in code.

---

## ❀ 4. Engineering Decisions ────୨ৎ────────୨ৎ────

Why Cheese is the way it is. This section steps back from individual components and documents the decisions behind them: the choices we made, the alternatives we rejected, and the things that did not work. It is the section where the reasoning across all the others comes together, including the failures we learned the most from.

**The core idea:** we can name and explain every strength and every weakness of this robot, and that understanding is what let us improve it.

---

## ❀ 5. Reproducibility ────୨ৎ────────୨ৎ────

How to rebuild Cheese. This section is written for someone who wants to reproduce our work: the full bill of materials, the parts and quantities, and the build instructions needed to assemble the robot as we did. It is what turns this repository from a description of our robot into something another team could actually reconstruct.

**The core idea:** documentation is only complete if someone else could follow it and end up with the same robot.

---

## ❀ How to Read This Repository ────୨ৎ────────୨ৎ────

The sections are ordered to build on each other. Section 1 gives you the physical robot, Section 2 powers and equips it, Section 3 makes it think, Section 4 explains the reasoning behind all of it, and Section 5 tells you how to build your own.

If you only have a few minutes, this overview plus the opening of each section gives you the whole picture. If you want the depth, each numbered file inside a section develops one subsystem in full technical detail, with the real values from our code, the real measurements from our robot, and an honest account of what still needs work.
