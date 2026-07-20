#!/usr/bin/env python3
# Simple wall-centering PID + color-controlled curves
# Faster version with a softer close-wall emergency protection
# Python 3.5.3 / ev3dev2 compatible

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.button import Button
from time import sleep

# -------------------------
# HARDWARE
# -------------------------
# OUTPUT_A = steering motor
# OUTPUT_B = drive motor
# INPUT_1  = left ultrasonic
# INPUT_2  = color sensor
# INPUT_3  = right ultrasonic

steering = MediumMotor(OUTPUT_A)
drive = LargeMotor(OUTPUT_B)

left_sensor = UltrasonicSensor(INPUT_1)
color_sensor = ColorSensor(INPUT_2)
right_sensor = UltrasonicSensor(INPUT_3)
button = Button()

left_sensor.mode = 'US-DIST-CM'
right_sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'RGB-RAW'

steering.reset()
sleep(0.5)

# -------------------------
# SETTINGS
# -------------------------
DRIVE_SPEED = -78
CURVE_SPEED = -60
EMERGENCY_SPEED = -55

WALL_DANGER_CM = 42
EMERGENCY_ANGLE = 55

MAX_PID_ANGLE = 30
CURVE_ANGLE = 65
STEERING_SPEED = 100

KP = 0.45
KI = 0.002
KD = 0.15

BLUE_RGB = (36, 74, 165)
ORANGE_RGB = (245, 113, 20)
COLOR_THRESHOLD = 45.0

# Change this only if the steering directions are reversed on your robot.
STEER_DIRECTION_FIX = 1

# -------------------------
# VARIABLES
# -------------------------
curve_active = False
curve_direction = None
exit_color = None

integral = 0.0
last_error = 0.0

# Prevent one colored line from being detected repeatedly.
color_locked = False

# -------------------------
# SIMPLE HELPERS
# -------------------------
def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def rgb_distance(rgb_a, rgb_b):
    return ((rgb_a[0] - rgb_b[0]) ** 2 +
            (rgb_a[1] - rgb_b[1]) ** 2 +
            (rgb_a[2] - rgb_b[2]) ** 2) ** 0.5


def detect_color():
    try:
        rgb = color_sensor.rgb
        rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception:
        return None

    blue_distance = rgb_distance(rgb, BLUE_RGB)
    orange_distance = rgb_distance(rgb, ORANGE_RGB)

    if blue_distance <= COLOR_THRESHOLD and blue_distance < orange_distance:
        return 'BLUE'

    if orange_distance <= COLOR_THRESHOLD and orange_distance < blue_distance:
        return 'ORANGE'

    return None


def set_steering(angle):
    angle = clamp(angle, -90, 90)
    steering.on_to_position(
        SpeedPercent(STEERING_SPEED),
        int(angle * STEER_DIRECTION_FIX),
        brake=True,
        block=False
    )


def reset_pid():
    global integral, last_error
    integral = 0.0
    last_error = 0.0

# -------------------------
# PID WALL CENTERING
# -------------------------
def drive_with_pid():
    global integral, last_error

    try:
        left = float(left_sensor.distance_centimeters)
        sleep(0.015)
        right = float(right_sensor.distance_centimeters)
    except Exception:
        return

    # Simple emergency protection. If one wall is too close, temporarily
    # override PID, slow down slightly, and steer moderately toward the open side.
    if left <= WALL_DANGER_CM or right <= WALL_DANGER_CM:
        reset_pid()
        drive.on(SpeedPercent(EMERGENCY_SPEED))

        if left < right:
            set_steering(-EMERGENCY_ANGLE)
        else:
            set_steering(EMERGENCY_ANGLE)

        return

    # Positive error means the robot is closer to the left wall,
    # so it must steer right. Negative means steer left.
    error = right - left

    integral += error
    integral = clamp(integral, -100, 100)

    derivative = error - last_error
    last_error = error

    correction = (KP * error) + (KI * integral) + (KD * derivative)
    steering_angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive.on(SpeedPercent(DRIVE_SPEED))
    set_steering(steering_angle)

# -------------------------
# COLOR-CONTROLLED CURVE
# -------------------------
def update_curve_state(detected_color):
    global curve_active, curve_direction, exit_color, color_locked

    if detected_color is None:
        color_locked = False
        return

    if color_locked:
        return

    color_locked = True

    # First color starts the curve.
    if not curve_active:
        curve_active = True
        reset_pid()

        if detected_color == 'BLUE':
            curve_direction = 'LEFT'
            exit_color = 'ORANGE'
        else:
            curve_direction = 'RIGHT'
            exit_color = 'BLUE'

        return

    # The opposite color ends the curve.
    if detected_color == exit_color:
        curve_active = False
        curve_direction = None
        exit_color = None
        reset_pid()


def drive_through_curve():
    drive.on(SpeedPercent(CURVE_SPEED))

    if curve_direction == 'LEFT':
        set_steering(CURVE_ANGLE)
    else:
        set_steering(-CURVE_ANGLE)

# -------------------------
# MAIN LOOP
# -------------------------
try:
    while not button.backspace:
        detected_color = detect_color()
        update_curve_state(detected_color)

        if curve_active:
            drive_through_curve()
        else:
            drive_with_pid()

        sleep(0.01)

finally:
    drive.off()
    steering.off()

#!/usr/bin/env python3
# Simple wall-centering PID + color-controlled curves
# Faster version with a softer close-wall emergency protection
# Python 3.5.3 / ev3dev2 compatible

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.button import Button
from time import sleep

# -------------------------
# HARDWARE
# -------------------------
# OUTPUT_A = steering motor
# OUTPUT_B = drive motor
# INPUT_1  = left ultrasonic
# INPUT_2  = color sensor
# INPUT_3  = right ultrasonic

steering = MediumMotor(OUTPUT_A)
drive = LargeMotor(OUTPUT_B)

left_sensor = UltrasonicSensor(INPUT_1)
color_sensor = ColorSensor(INPUT_2)
right_sensor = UltrasonicSensor(INPUT_3)
button = Button()

left_sensor.mode = 'US-DIST-CM'
right_sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'RGB-RAW'

steering.reset()
sleep(0.5)

# -------------------------
# SETTINGS
# -------------------------
DRIVE_SPEED = -78
CURVE_SPEED = -60
EMERGENCY_SPEED = -55

WALL_DANGER_CM = 38
EMERGENCY_ANGLE = 55

MAX_PID_ANGLE = 30
CURVE_ANGLE = 65
STEERING_SPEED = 100

KP = 0.45
KI = 0.002
KD = 0.15

BLUE_RGB = (36, 74, 165)
ORANGE_RGB = (245, 113, 20)
COLOR_THRESHOLD = 45.0

# Change this only if the steering directions are reversed on your robot.
STEER_DIRECTION_FIX = 1

# -------------------------
# VARIABLES
# -------------------------
curve_active = False
curve_direction = None
exit_color = None

integral = 0.0
last_error = 0.0

# Prevent one colored line from being detected repeatedly.
color_locked = False

# -------------------------
# SIMPLE HELPERS
# -------------------------
def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def rgb_distance(rgb_a, rgb_b):
    return ((rgb_a[0] - rgb_b[0]) ** 2 +
            (rgb_a[1] - rgb_b[1]) ** 2 +
            (rgb_a[2] - rgb_b[2]) ** 2) ** 0.5


def detect_color():
    try:
        rgb = color_sensor.rgb
        rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception:
        return None

    blue_distance = rgb_distance(rgb, BLUE_RGB)
    orange_distance = rgb_distance(rgb, ORANGE_RGB)

    if blue_distance <= COLOR_THRESHOLD and blue_distance < orange_distance:
        return 'BLUE'

    if orange_distance <= COLOR_THRESHOLD and orange_distance < blue_distance:
        return 'ORANGE'

    return None


def set_steering(angle):
    angle = clamp(angle, -90, 90)
    steering.on_to_position(
        SpeedPercent(STEERING_SPEED),
        int(angle * STEER_DIRECTION_FIX),
        brake=True,
        block=False
    )


def reset_pid():
    global integral, last_error
    integral = 0.0
    last_error = 0.0

# -------------------------
# PID WALL CENTERING
# -------------------------
def drive_with_pid():
    global integral, last_error

    try:
        left = float(left_sensor.distance_centimeters)
        sleep(0.015)
        right = float(right_sensor.distance_centimeters)
    except Exception:
        return

    # Simple emergency protection. If one wall is too close, temporarily
    # override PID, slow down slightly, and steer moderately toward the open side.
    if left <= WALL_DANGER_CM or right <= WALL_DANGER_CM:
        reset_pid()
        drive.on(SpeedPercent(EMERGENCY_SPEED))

        if left < right:
            set_steering(-EMERGENCY_ANGLE)
        else:
            set_steering(EMERGENCY_ANGLE)

        return

    # Positive error means the robot is closer to the left wall,
    # so it must steer right. Negative means steer left.
    error = right - left

    integral += error
    integral = clamp(integral, -100, 100)

    derivative = error - last_error
    last_error = error

    correction = (KP * error) + (KI * integral) + (KD * derivative)
    steering_angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive.on(SpeedPercent(DRIVE_SPEED))
    set_steering(steering_angle)

# -------------------------
# COLOR-CONTROLLED CURVE
# -------------------------
def update_curve_state(detected_color):
    global curve_active, curve_direction, exit_color, color_locked

    if detected_color is None:
        color_locked = False
        return

    if color_locked:
        return

    color_locked = True

    # First color starts the curve.
    if not curve_active:
        curve_active = True
        reset_pid()

        if detected_color == 'BLUE':
            curve_direction = 'LEFT'
            exit_color = 'ORANGE'
        else:
            curve_direction = 'RIGHT'
            exit_color = 'BLUE'

        return

    # The opposite color ends the curve.
    if detected_color == exit_color:
        curve_active = False
        curve_direction = None
        exit_color = None
        reset_pid()


def drive_through_curve():
    drive.on(SpeedPercent(CURVE_SPEED))

    if curve_direction == 'LEFT':
        set_steering(CURVE_ANGLE)
    else:
        set_steering(-CURVE_ANGLE)

# -------------------------
# MAIN LOOP
# -------------------------
try:
    while not button.backspace:
        detected_color = detect_color()
        update_curve_state(detected_color)

        if curve_active:
            drive_through_curve()
        else:
            drive_with_pid()

        sleep(0.01)

finally:
    drive.off()
    steering.off()

