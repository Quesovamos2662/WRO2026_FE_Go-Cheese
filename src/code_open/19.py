#!/usr/bin/env python3
# WRO Future Engineers: PID centering + protected walls + color curves
# Written from scratch for Python 3.5.3 / ev3dev2

from ev3dev2.motor import (
    LargeMotor,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    SpeedPercent
)
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.button import Button
from ev3dev2.display import Display
from time import sleep, time


# ================================================================
# HARDWARE
# ================================================================
steering = MediumMotor(OUTPUT_A)
drive = LargeMotor(OUTPUT_B)

left_sensor = UltrasonicSensor(INPUT_1)
color_sensor = ColorSensor(INPUT_2)
right_sensor = UltrasonicSensor(INPUT_3)

buttons = Button()
screen = Display()

left_sensor.mode = 'US-DIST-CM'
right_sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'RGB-RAW'

steering.reset()
sleep(0.5)


# ================================================================
# MAIN SETTINGS
# ================================================================
# Negative drive values move this robot forward.
STRAIGHT_SPEED = -62
CURVE_SPEED = -54
GENTLE_WALL_SPEED = -46
SEVERE_WALL_SPEED = -40
POST_CURVE_SPEED = -38

# Steering motor speed is intentionally limited to 20%.
STEERING_SPEED = 23
POST_CURVE_STEERING_SPEED = 40
STEER_DIRECTION = -1

# Steering angles.
MAX_PID_ANGLE = 24
CURVE_ANGLE = 55
GENTLE_WALL_ANGLE = 18
SEVERE_WALL_ANGLE = 32

# Brief counter-steer after leaving a curve.
# This points the ultrasonic sensors back toward the walls before PID returns.
POST_CURVE_ANGLE = 16
POST_CURVE_TIME = 0.16

# Wall layers.
# 21.5 cm is the early/gentle layer.
# 19.0 cm is the closer/severe layer.
WALL_GENTLE_DISTANCE = 21.5
WALL_SEVERE_DISTANCE = 19.0

# Less-aggressive PID than the reference program.
KP = 0.28
KI = 0.001
KD = 0.08
INTEGRAL_LIMIT = 70.0

# Color calibration values from the reference structure.
BLUE_RGB = (36, 74, 165)
ORANGE_RGB = (245, 113, 20)
COLOR_THRESHOLD = 45.0

# Four completed curves make one lap. Each completed curve contains
# one first color and one opposite/exit color.
CURVES_PER_LAP = 4
TOTAL_LAPS = 3
TOTAL_CURVES = CURVES_PER_LAP * TOTAL_LAPS

# One valid color reading is accepted immediately so the second color
# triggers the post-curve correction without an extra loop delay.
COLOR_CONFIRM_READINGS = 1

LOOP_DELAY = 0.01


# ================================================================
# PROGRAM STATE
# ================================================================
curve_active = False
curve_direction = None
required_exit_color = None
last_accepted_color = None
candidate_color = None
candidate_count = 0

post_curve_active = False
post_curve_direction = None
post_curve_end_time = None

integral = 0.0
last_error = 0.0

completed_curves = 0
completed_laps = 0

start_time = None
first_color_delay = None
stop_deadline = None
parking_active = False


# ================================================================
# GENERAL HELPERS
# ================================================================
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def reset_pid():
    global integral, last_error
    integral = 0.0
    last_error = 0.0


def set_steering(angle, steering_speed=None):
    """Move steering to an absolute angle.

    Normal movement uses STEERING_SPEED. Post-curve recovery can pass its own
    faster steering speed without changing PID, wall, or curve steering.
    """
    if steering_speed is None:
        steering_speed = STEERING_SPEED

    angle = clamp(angle, -90, 90)
    target = int(angle * STEER_DIRECTION)

    steering.on_to_position(
        SpeedPercent(steering_speed),
        target,
        brake=True,
        block=False
    )


def stop_robot():
    drive.off(brake=True)
    steering.off(brake=True)


# ================================================================
# COLOR READING
# ================================================================
def color_distance(rgb_a, rgb_b):
    return (
        (rgb_a[0] - rgb_b[0]) ** 2 +
        (rgb_a[1] - rgb_b[1]) ** 2 +
        (rgb_a[2] - rgb_b[2]) ** 2
    ) ** 0.5


def read_color():
    try:
        rgb = color_sensor.rgb
        rgb = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    except Exception:
        return None

    blue_distance = color_distance(rgb, BLUE_RGB)
    orange_distance = color_distance(rgb, ORANGE_RGB)

    if blue_distance <= COLOR_THRESHOLD and blue_distance < orange_distance:
        return 'BLUE'

    if orange_distance <= COLOR_THRESHOLD and orange_distance < blue_distance:
        return 'ORANGE'

    return None


# ================================================================
# ULTRASONIC READING
# ================================================================
def valid_distance(value):
    # Reject impossible, zero, and extreme readings.
    return value is not None and 1.0 <= value <= 255.0


def read_walls():
    try:
        left = float(left_sensor.distance_centimeters)
        right = float(right_sensor.distance_centimeters)
    except Exception:
        return None, None

    if not valid_distance(left):
        left = None
    if not valid_distance(right):
        right = None

    return left, right


# ================================================================
# CURVE AND LAP LOGIC
# ================================================================
def begin_curve(color):
    global curve_active, curve_direction, required_exit_color

    curve_active = True
    reset_pid()

    if color == 'BLUE':
        curve_direction = 'LEFT'
        required_exit_color = 'ORANGE'
    else:
        curve_direction = 'RIGHT'
        required_exit_color = 'BLUE'


def start_parking():
    """Start the final timed run without changing the recorded timer formula."""
    global parking_active, stop_deadline

    if parking_active:
        return

    delay = first_color_delay if first_color_delay is not None else 0.0
    parking_active = True
    stop_deadline = time() + (delay * 2.0)

    screen.clear()
    screen.text_pixels('STOPPING', x=42, y=45, font='luBS18')
    screen.update()


def finish_curve():
    global curve_active, curve_direction, required_exit_color
    global post_curve_active, post_curve_direction, post_curve_end_time
    global completed_curves, completed_laps

    # Save the curve direction before clearing it.
    post_curve_direction = curve_direction
    post_curve_active = True
    post_curve_end_time = time() + POST_CURVE_TIME

    curve_active = False
    curve_direction = None
    required_exit_color = None
    reset_pid()

    # The opposite/second color has now completed exactly one curve.
    completed_curves += 1
    completed_laps = completed_curves // CURVES_PER_LAP

    # Alternate parking trigger: the 12th confirmed completed curve
    # starts parking immediately. This does not depend on separate
    # blue/orange totals matching perfectly.
    if completed_curves >= TOTAL_CURVES:
        start_parking()


def accept_stable_color(raw_color):
    """Return a color only after consecutive matching readings."""
    global candidate_color, candidate_count

    if raw_color is None:
        candidate_color = None
        candidate_count = 0
        return None

    if raw_color == candidate_color:
        candidate_count += 1
    else:
        candidate_color = raw_color
        candidate_count = 1

    if candidate_count >= COLOR_CONFIRM_READINGS:
        return candidate_color

    return None


def update_color_logic(raw_color):
    global last_accepted_color, first_color_delay

    if parking_active:
        return

    color = accept_stable_color(raw_color)

    # No confirmed color yet. Rearm only after the sensor leaves all colors.
    if raw_color is None:
        last_accepted_color = None
        return

    if color is None:
        return

    # Prevent one continuous stripe from being counted repeatedly.
    if color == last_accepted_color:
        return

    last_accepted_color = color

    if first_color_delay is None:
        first_color_delay = max(0.0, time() - start_time)

    if not curve_active:
        begin_curve(color)
        return

    # Only the opposite color can finish the active curve.
    if color == required_exit_color:
        finish_curve()


# ================================================================
# MOVEMENT LOGIC
# ================================================================
def drive_curve():
    """Highest-priority movement mode; PID and wall logic cannot override it."""
    drive.on(SpeedPercent(CURVE_SPEED))

    if curve_direction == 'LEFT':
        set_steering(CURVE_ANGLE)
    else:
        set_steering(-CURVE_ANGLE)



def drive_post_curve():
    """Briefly counter-steer opposite to the completed curve.

    PID and wall protection stay disabled during this short phase so bad
    ultrasonic readings near a corner cannot immediately steer the robot
    into the wall.
    """
    global post_curve_active, post_curve_direction, post_curve_end_time

    if post_curve_end_time is None or time() >= post_curve_end_time:
        post_curve_active = False
        post_curve_direction = None
        post_curve_end_time = None
        reset_pid()
        return False

    drive.on(SpeedPercent(POST_CURVE_SPEED))

    if post_curve_direction == 'LEFT':
        # Completed a left curve, so briefly steer right.
        set_steering(-POST_CURVE_ANGLE, POST_CURVE_STEERING_SPEED)
    elif post_curve_direction == 'RIGHT':
        # Completed a right curve, so briefly steer left.
        set_steering(POST_CURVE_ANGLE, POST_CURVE_STEERING_SPEED)
    else:
        set_steering(0, POST_CURVE_STEERING_SPEED)

    return True


def steer_away_from_wall(left, right, angle):
    """Choose the direction that moves the robot away from the closest wall."""
    if left is not None and right is not None:
        if left < right:
            set_steering(-angle)
        else:
            set_steering(angle)
    elif left is not None:
        set_steering(-angle)
    elif right is not None:
        set_steering(angle)


def wall_protection(left, right):
    """Two wall-protection layers, used only outside color curves."""
    left_severe = left is not None and left <= WALL_SEVERE_DISTANCE
    right_severe = right is not None and right <= WALL_SEVERE_DISTANCE

    if left_severe or right_severe:
        drive.on(SpeedPercent(SEVERE_WALL_SPEED))
        steer_away_from_wall(left, right, SEVERE_WALL_ANGLE)
        reset_pid()
        return True

    left_gentle = left is not None and left <= WALL_GENTLE_DISTANCE
    right_gentle = right is not None and right <= WALL_GENTLE_DISTANCE

    if left_gentle or right_gentle:
        drive.on(SpeedPercent(GENTLE_WALL_SPEED))
        steer_away_from_wall(left, right, GENTLE_WALL_ANGLE)
        reset_pid()
        return True

    return False


def drive_pid(left, right):
    global integral, last_error

    # Centering error: positive means the right wall is farther away.
    error = right - left

    integral += error
    integral = clamp(integral, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)

    derivative = error - last_error
    last_error = error

    correction = (
        (KP * error) +
        (KI * integral) +
        (KD * derivative)
    )

    steering_angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive.on(SpeedPercent(STRAIGHT_SPEED))
    set_steering(steering_angle)


def drive_safely_without_two_walls(left, right):
    """Fallback when only one or neither ultrasonic reading is valid."""
    drive.on(SpeedPercent(GENTLE_WALL_SPEED))

    if left is not None and right is None:
        if left <= WALL_GENTLE_DISTANCE:
            set_steering(-GENTLE_WALL_ANGLE)
        else:
            set_steering(0)
    elif right is not None and left is None:
        if right <= WALL_GENTLE_DISTANCE:
            set_steering(GENTLE_WALL_ANGLE)
        else:
            set_steering(0)
    else:
        set_steering(0)


# ================================================================
# START SCREEN AND BUTTON
# ================================================================
def show_ready():
    screen.clear()
    screen.text_pixels('READY!', x=66, y=45, font='luBS24')
    screen.update()


def wait_for_left_button():
    # Avoid starting from a button that was already held down.
    while buttons.left:
        sleep(0.02)

    while not buttons.left:
        sleep(0.02)

    # Wait for release so one press counts once.
    while buttons.left:
        sleep(0.02)


# ================================================================
# MAIN PROGRAM
# ================================================================
try:
    show_ready()
    wait_for_left_button()

    start_time = time()

    while True:
        now = time()

        # Back button remains an emergency stop.
        if buttons.backspace:
            break

        # This deadline exists only after the second color finishes curve 4 of lap 3.
        if stop_deadline is not None and now >= stop_deadline:
            break

        detected_color = read_color()
        left_distance, right_distance = read_walls()

        update_color_logic(detected_color)

        # Priority order:
        # 1. Active color curve
        # 2. Brief opposite-direction counter-steer
        # 3. Final parking run or normal wall protection/PID
        #
        # During parking_active, later color detections are ignored, but the robot
        # still uses wall protection and PID until the doubled time expires.
        if curve_active:
            drive_curve()
        elif post_curve_active and drive_post_curve():
            pass
        elif wall_protection(left_distance, right_distance):
            pass
        elif left_distance is not None and right_distance is not None:
            drive_pid(left_distance, right_distance)
        else:
            drive_safely_without_two_walls(left_distance, right_distance)

        sleep(LOOP_DELAY)

finally:
    stop_robot()
    screen.clear()
    screen.text_pixels('STOPPED', x=50, y=45, font='luBS18')
    screen.update()



