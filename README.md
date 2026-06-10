# WRO2026_FE_QuesoVamos



# Introduction
(car pic)

Welcome to the official GitHub repository for Team QuesoVamos from Panama, participating in the WRO San Miguelito regionals of 2026. This repository will be home to resources like our project's code, as well as the materials and components used for building said project.

# Meet the team

Team QuesoVamos is made up by three unlikely friends, united by their shared ambition to step out of their comfort zone and try something new. This is our first time working with Github, BrickLink, and many other unfamiliar software. Even if we don't achieve anything major in the following competition, we'll strive to use what we learned to do a better job in the years to come and go above and beyond what we were capable of doing this time around.

# Roles

Romina Mora: Car builder

Caylee Rios: Programmer

Christopher Romero: Documentator, Car builder


# MOBILITY MANAGEMENT


## Driving base

 Our driving base and chassis are made up completely out of lego, specifically out of the official Lego Mindstorms EV3 Kit. Even though Lego projects bring up small stability and structural issues sometimes, we decided to build in this way for our ease of use and because structural inefficiencies are easy to detect and correct.


## Car dimensions

Length: ~19cm (190mm)

Height: 9.5cm (95mm)

Width: ~13cm (130mm)

Weight: ~73.61g (0.07361kg)

## Car pictures (labeled)

 


# MOTORIZATION


<img width="259" height="194" alt="image" src="https://github.com/user-attachments/assets/40150526-cb7d-4e51-bf20-e9a9cded566c" />



<img width="225" height="225" alt="image" src="https://github.com/user-attachments/assets/a6aa0007-fd3b-4add-a3f9-a1b560aa55e0" />

We used exclusively Lego motors when building our car; one large, and one medium. We used these because they would naturally be ccmpatible with our purely Lego structure and our EV3 brick, and also because they offer a good measure of speed without sacrificing any of our car's stability.

We wanted to install an externally sourced motor system (CQRobot Encoder Motor 12V 330RPM with a gear axle shaft), but we soon realized that the system was incompatible with our project's structure. Because of that and their easy-to-handle nature, we chose to use Lego motors for our car. 

 ## Steering mechanism

 
Our project uses a simple Ackerman steering mechanism. Since this our first time competing, we did not want to use an overly complicated steering mechanism; hence why we didn't use something like a steering servo, which we believed to be more complex.

## POWER SENSE AND MANAGEMENT



 ## Power supply explanation and diagram

Everything on our car is on the same voltage level. Thanks to this, our EV3 brick can serve as a battery for all of the electrical components in use.

Our ultrasonic sensors use approximately 3.3V each, and our infrared sensor uses the same amount. Our brick can supply power to all of these at once thanks to its 9V output.

## Controller

<img width="400" height="300" alt="image" src="https://github.com/user-attachments/assets/8f9bc277-206b-4b7d-9ec0-ca584912c328" />


For our controller, we used a standard EV3 Lego Mindstorms Brick. Because of this, it also serves as a battery for all of the sensors that our robot utilises.

It sports a flash memory of 16 MB, has 64 MB of RAM, And is able to output any voltage value in between 0V and 9V.


## Sensors

 ## Ultrasonic

 
<img width="259" height="194" alt="image" src="https://github.com/user-attachments/assets/518e701a-d621-406b-bfa3-8aadc2fcd178" />



In the sensors department, we settled on utilising ultrasonic sensors to their full extent. Since we had to make up for not having a camera, we mounted two ultrasonic sensors on either side of our car. These will make sure to detect any nearby walls or obstacles, making our robot able to correct its route on the fly.

 ## Infrared


 <img width="225" height="225" alt="image" src="https://github.com/user-attachments/assets/c8c3e815-77bc-4a2b-96f2-f45d3433f29c" />


 Additionally, we also mounted an infrared sensor to the front of our car to make sure there were no blind spots for obstacles. We opted to not use an ultrasonic sensor in this spot because we feared that the noise from spectators, judges, and other competitors at the competition venue would make the sensors misfire or get disrupted.

## Schematics


# PROGRAMMING

## Software development


## Obstacle challenge

During the obstacle challenge, we use our car's ultrasonic and infrared sensors to detect walls and obstacles nearby. When the sensors detect something, the car will steer clear of it and keep driving forward. Because our robot can also detect the walls of the track, it will know when to turn in order to complete laps,

This process repeats until all laps are completed and the race ends, when the robot will turn itself off.


## Obstacle program flowchart

This easy-to-follow flowchart gives insight to how our car's code works in simple terms and how it proceeds when it encounters a wall or an obstacle.


<img width="473" height="706" alt="image" src="https://github.com/user-attachments/assets/92b06526-cccd-4ed8-b62f-b08c6d17d6a1" />




## Assembly


# Bill of Materials


## Electronics

- X1 Mindstorms EV3 Brick
- X1 Ultrasonic sensor (Mindstorms EV3 model)
- X1 Ultrasonic sensor (Mindstorms NXT model)
- X1 Infrared sensor
- X1 Large motor
- X1 Medium motor
  

## Structural elements






## Car Performance Videos




# Resources





  
