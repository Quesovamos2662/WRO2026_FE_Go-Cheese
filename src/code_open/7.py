#!/usr/bin/env python3
# Simple PID wall centering + color curve + 20 cm wall protection
# Python 3.5.3 / ev3dev2 compatible

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.button import Button
from time import sleep, monotonic

# Motors and sensors
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

# Speed and steering
STRAIGHT_SPEED = -72
CURVE_SPEED = -58
WARNING_SPEED = -45
CRITICAL_SPEED = -35

MAX_PID_ANGLE = 22
CURVE_ANGLE = 60

WARNING_ANGLE = 45
CRITICAL_ANGLE = 65

WALL_WARNING = 21.5
WALL_CRITICAL = 14.0

STEERING_SPEED = 100

# Run timer: 1 minute, 6 seconds, and 25 milliseconds
RUN_TIME_SECONDS = 66.025

# PID
KP = 0.50
KI = 0.002
KD = 0.18

# Colors
BLUE_RGB = (36, 74, 165)
ORANGE_RGB = (245, 113, 20)
COLOR_THRESHOLD = 45.0

# Change to -1 only if steering is reversed
STEER_DIRECTION_FIX = 1

curve_active = False
curve_direction = None
exit_color = None
color_locked = False
integral = 0.0
last_error = 0.0
pid_first_reading = True
last_valid_left = None
last_valid_right = None


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def set_steering(angle):
    angle = clamp(angle, -90, 90)
    steering.on_to_position(
        SpeedPercent(STEERING_SPEED),
        int(angle * STEER_DIRECTION_FIX),
        brake=True,
        block=False
    )


def color_distance(rgb1, rgb2):
    return ((rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2) ** 0.5


def read_color():
    try:
        rgb = color_sensor.rgb
        rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception:
        return None

    blue = color_distance(rgb, BLUE_RGB)
    orange = color_distance(rgb, ORANGE_RGB)

    if blue <= COLOR_THRESHOLD and blue < orange:
        return 'BLUE'
    if orange <= COLOR_THRESHOLD and orange < blue:
        return 'ORANGE'
    return None


def read_walls():
    global last_valid_left, last_valid_right

    try:
        left = float(left_sensor.distance_centimeters)
        right = float(right_sensor.distance_centimeters)
    except Exception:
        return last_valid_left, last_valid_right

    # Reject unrealistic far readings that can appear when a sensor
    # points through a corner gap or temporarily loses the wall.
    if 0.0 < left <= 80.0:
        last_valid_left = left
    else:
        left = last_valid_left

    if 0.0 < right <= 80.0:
        last_valid_right = right
    else:
        right = last_valid_right

    return left, right


def update_curve(color):
    global curve_active, curve_direction, exit_color, color_locked
    global integral, last_error, pid_first_reading

    if color is None:
        color_locked = False
        return

    if color_locked:
        return

    color_locked = True

    if not curve_active:
        curve_active = True
        integral = 0.0
        last_error = 0.0
        pid_first_reading = True

        if color == 'BLUE':
            curve_direction = 'LEFT'
            exit_color = 'ORANGE'
        else:
            curve_direction = 'RIGHT'
            exit_color = 'BLUE'

    elif color == exit_color:
        curve_active = False
        curve_direction = None
        exit_color = None
        integral = 0.0
        last_error = 0.0
        pid_first_reading = True


def avoid_wall(left, right):
    if left is None or right is None:
        return False

    # Layer 1: critical distance — slow down and steer sharply.
    if left <= WALL_CRITICAL or right <= WALL_CRITICAL:
        drive.on(SpeedPercent(CRITICAL_SPEED))

        if left <= WALL_CRITICAL and right <= WALL_CRITICAL:
            set_steering(CRITICAL_ANGLE if left < right else -CRITICAL_ANGLE)
        elif left <= WALL_CRITICAL:
            set_steering(-CRITICAL_ANGLE)
        else:
            set_steering(CRITICAL_ANGLE)

        return True

    # Layer 2: warning distance — use a gentler correction.
    if left <= WALL_WARNING or right <= WALL_WARNING:
        drive.on(SpeedPercent(WARNING_SPEED))

        if left <= WALL_WARNING and right <= WALL_WARNING:
            set_steering(WARNING_ANGLE if left < right else -WARNING_ANGLE)
        elif left <= WALL_WARNING:
            set_steering(-WARNING_ANGLE)
        else:
            set_steering(WARNING_ANGLE)

        return True

    return False


def drive_pid(left, right):
    global integral, last_error, pid_first_reading

    error = right - left
    integral = clamp(integral + error, -100, 100)

    # On the first PID reading after a curve, initialize last_error
    # instead of calculating a large derivative spike.
    if pid_first_reading:
        derivative = 0.0
        last_error = error
        pid_first_reading = False
    else:
        derivative = error - last_error
        last_error = error

    correction = KP * error + KI * integral + KD * derivative
    angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive.on(SpeedPercent(STRAIGHT_SPEED))
    set_steering(angle)


def drive_curve():
    drive.on(SpeedPercent(CURVE_SPEED))

    if curve_direction == 'LEFT':
        set_steering(CURVE_ANGLE)
    else:
        set_steering(-CURVE_ANGLE)


try:
    # Wait until the EV3 right-arrow button is pressed.
    while not button.right and not button.backspace:
        sleep(0.01)

    if not button.backspace:
        start_time = monotonic()

        while not button.backspace:
            if monotonic() - start_time >= RUN_TIME_SECONDS:
                break

            color = read_color()
            left, right = read_walls()

            update_curve(color)

            # During a color-controlled curve, the curve command has priority.
            # This prevents cached ultrasonic readings from blocking the turn.
            if curve_active:
                drive_curve()
            elif avoid_wall(left, right):
                pass
            elif left is not None and right is not None:
                drive_pid(left, right)

            sleep(0.01)

finally:
    drive.off()
    steering.off()




