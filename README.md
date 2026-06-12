# WRO2026_FE_QuesoVamos


[banner + team photo]

## Meet the Team    
Team QuesoVamos is made up by three unlikely friends, united by their shared ambition to step out of their comfort zone and try something new. This is our first time working with Github, BrickLink, and many other unfamiliar software. Even if we don't achieve anything major in the following competition, we'll strive to use what we learned to do a better job in the years to come and go above and beyond what we were capable of doing this time around.


## Robot Overview     

Length: ~28cm (280mm)

Height: ~9.5cm (95mm)

Width: ~13cm (130mm)

Weight: ~73.61g (0.07361kg)

(~200 chars — specs rápidos)

---

## 1. Mobility & Mechanical Design     [Criterion 1]
### Driving base & chassis             (~500 chars)

Our driving base and chassis are constructed entirely from the official LEGO Mindstorms EV3 Kit. This decision was driven by several practical and technical factors.
First, LEGO components offer native compatibility with the EV3 brick, eliminating integration overhead for mounting sensors and motors. Second, the modular nature of LEGO allows structural issues to be identified and corrected rapidly during testing, without requiring new parts or fabrication tools.

But an all-LEGO build introduces limitations. These come in the form of the plastic frame having measurable flex at higher speeds, and connection points being able to loosen if the frame withstands powerful impacts. Despite these possible shortcomings, we still believed that we could make our car work, so we chose to build in this manner.



### Motor selection & torque reasoning (~500 chars) 


Our vehicle uses two LEGO Mindstorms EV3 motors — one large and one medium — connected directly to the EV3 brick via ports A and B. Both motors were chosen for their native compatibility with the EV3 ecosystem and their ability to provide reliable speed and torque without requiring external drivers or voltage regulators.

The large motor, used for moving back and forth, has a top speed of 170 RPM, a running and stall torque of 20Nxcm and 40 Nxcm respectively, an operating voltage of 9V, and a weight of 76g. For a Lego component, these specs are very respectable and are just what we were looking for in our robot.

Finally, the medium motor, which we decided to use for steering, has a top speed of 250 RPM, a running torque of 8Nxcm, a stall torque of 12Nxcm, an operating voltage of 9V and a weight of only 36g. This motor's higher RPM and lower torque make it better suited for steering. Its low weight also helps on making or robot lighter, benefiting its speed overall.


### Steering mechanism (Ackermann)     (~400 chars)

Our robot uses a simple Ackermann steering mechanism to achieve stable and controlled turning. Since this is our first time competing in the WRO, we decided to not make things harder on ourselves by using a more complex steering system. For this reason, we did not implement a servo-based steering mechanism, as we considered it more difficult to build, and troubleshoot with our current experience.

← AMPLIAR
### Chassis iterations                 (~300 chars)  ← FALTA (Lamina mandara el previous iteration)

## 2. Power & Sensor Architecture      [Criterion 2]
### Power supply & EV3 brick specs     (~300 chars)

For our controller, we used a standard EV3 Lego Mindstorms Brick. We decided on using this Brick as our controller because it can also serves as a battery for all of the sensors and components that our robot utilises.

It sports a flash memory of 16 MB, has 64 MB of RAM, is able to output any voltage value in between 0V and 9V, and has a rechargable battery with a maximum capacity of 2000 mAh

### Wiring diagram                     [imagen + tabla de puertos]  ← FALTA
### Sensor selection & placement       (~600 chars) 

In the sensors department, we settled on utilising ultrasonic sensors to their full extent. Since we had to make up for not having a camera, we mounted three ultrasonic sensors on either side and on the front of our car. These will make sure to detect any nearby walls or obstacles, making our robot able to correct its route on the fly.

We also decided on choosing ultrasonic sensors because of their ease of calibration and efficiency. They are more intuitive to adjust than Lego EV3 infrared sensors and have almost no competition in terms of efficiency and accuracy.

### Sensor calibration                 (~200 chars)  ← FALTA

## 3. Software Architecture            [Criterion 3]
### Algorithm description              (~600 chars)  ← FALTA
### Flowchart                          [imagen existente]
### Obstacle & corner handling         (~400 chars)  ← FALTA
### Tuning process                     (~300 chars)  ← FALTA

## 4. Engineering Decisions            [Criterion 4]  ← SECCIÓN NUEVA
### Design decision log                (~700 chars)
### What didn't work                   (~400 chars)

## 5. Reproducibility                  [Criterion 5]
### Bill of Materials                  (~200 chars)

Electronic Materials

- X1 Lego Mindstorms EV3 Brick
- X1 Lego Mindstorms EV3 Large Motor
- X1 Lego Mindstorms EV3 Medium Motor
- X3 Lego Mindstorms EV3 Ultrasonic Sensor
- 
### Build instructions                 (~300 chars)  ← FALTA

## Vehicle Photos
## Team Photos
## Performance Videos
## Resources



  
