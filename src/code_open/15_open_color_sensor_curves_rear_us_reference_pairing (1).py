#!/usr/bin/env python3
# WRO Future Engineers 2026 - Open Challenge
# EV3 color sensor counts curves using simple BLUE/ORANGE pairing. INPUT_4 records the rear-wall distance
# while stationary at startup, is ignored during the race, and is read again
# only after curve 12 to stop at the saved rear-wall distance.
# Python 3.5.3 / ev3dev2

from ev3dev2.motor import (
    LargeMotor,
    MediumMotor,
    OUTPUT_A,
    OUTPUT_B,
    SpeedPercent
)
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
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
rear_sensor = UltrasonicSensor(INPUT_4)

buttons = Button()
screen = Display()

left_sensor.mode = 'US-DIST-CM'
right_sensor.mode = 'US-DIST-CM'
rear_sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'COL-COLOR'

steering.reset()
sleep(0.5)


# ================================================================
# MOVEMENT SETTINGS
# ================================================================
STRAIGHT_SPEED = -62
GENTLE_WALL_SPEED = -46
SEVERE_WALL_SPEED = -40
FINAL_SEARCH_SPEED = -20
FINAL_CREEP_SPEED = -10

STEERING_SPEED = 23
STEER_DIRECTION = -1
MAX_PID_ANGLE = 24
GENTLE_WALL_ANGLE = 18
SEVERE_WALL_ANGLE = 32

WALL_GENTLE_DISTANCE = 21.5
WALL_SEVERE_DISTANCE = 19.0

KP = 0.28
KI = 0.001
KD = 0.08
INTEGRAL_LIMIT = 70.0

LOOP_DELAY = 0.01


# ================================================================
# FLOOR COLOR SENSOR SETTINGS
# ================================================================
ORANGE_COLOR_GROUP = (
    ColorSensor.COLOR_RED,
    ColorSensor.COLOR_YELLOW,
    ColorSensor.COLOR_BROWN
)

# Inspired by the simpler and more reliable curve logic from 12.py:
# one stable color starts a curve, and the opposite stable color completes it.
COLOR_CONFIRM_READINGS = 2
COLOR_RELEASE_READINGS = 3

# Reject only obvious duplicate/flicker events, without long lockouts that can
# make the next real corner invisible.
PAIR_MIN_DISTANCE = 25.0
PAIR_MIN_TIME = 0.06
MIN_COMPLETED_CURVE_DISTANCE = 300.0
MIN_COMPLETED_CURVE_TIME = 0.30

# If the opposite color is genuinely missed, abandon the half-finished pair
# after a generous limit so the counter can recover on the next corner.
CURVE_SEQUENCE_MAX_DISTANCE = 3200.0
CURVE_SEQUENCE_MAX_TIME = 9.0

CURVES_PER_LAP = 4
TOTAL_CURVES = 12


# ================================================================
# START ROW CLASSIFICATION
# ================================================================
# Calibrate this between the measured first-row and last-row times.
START_ROW_TIME_THRESHOLD = 2.20


# ================================================================
# REAR ULTRASONIC PARKING SETTINGS
# ================================================================
# The rear sensor on INPUT_4 is sampled while the robot is stationary.
# It is NOT used by PID, wall protection, or normal driving.
REAR_START_SAMPLES = 25
REAR_SAMPLE_DELAY = 0.025
REAR_PARK_TOLERANCE_CM = 2.5
REAR_MATCH_CONFIRMATIONS = 6

# Do not allow an accidental equal reading immediately after curve 12.
REAR_DEPARTURE_CM = 8.0
REAR_DEPARTURE_CONFIRMATIONS = 5
MIN_FINAL_TRAVEL_DEGREES = 300.0

FINAL_SEARCH_TIMEOUT = 20.0
FINAL_SEARCH_MAX_DISTANCE = 5000.0

# ================================================================
# STATE
# ================================================================
integral = 0.0
last_error = 0.0

candidate_color = None
candidate_count = 0
release_count = COLOR_RELEASE_READINGS
color_event_armed = True

curve_active = False
required_exit_color = None
curve_start_position = None
curve_start_time = None
completed_curves = 0
last_curve_position = None
last_curve_time = None

run_start_time = None
start_to_first_curve_time = None
start_to_first_curve_distance = None
start_row = None

rear_start_distance = None
rear_match_count = 0
rear_departure_count = 0
rear_return_armed = False

final_search_active = False
final_search_start_position = None
final_search_start_time = None
start_position_found = False



# ================================================================
# HELPERS
# ================================================================
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def average(values):
    if not values:
        return None
    return sum(values) / float(len(values))


def reset_pid():
    global integral, last_error
    integral = 0.0
    last_error = 0.0


def set_steering(angle):
    angle = clamp(angle, -90, 90)
    target = int(angle * STEER_DIRECTION)
    steering.on_to_position(
        SpeedPercent(STEERING_SPEED),
        target,
        brake=True,
        block=False
    )


def stop_robot():
    drive.off(brake=True)
    steering.off(brake=True)


def show_message(text, x=10, font='luBS14'):
    screen.clear()
    screen.text_pixels(text, x=x, y=45, font=font)
    screen.update()


# ================================================================
# REAR ULTRASONIC SENSOR
# ================================================================
def read_rear_distance():
    try:
        value = float(rear_sensor.distance_centimeters)
    except Exception:
        return None

    if not valid_distance(value):
        return None
    return value


def record_rear_start_distance():
    values = []

    for _ in range(REAR_START_SAMPLES):
        value = read_rear_distance()
        if value is not None:
            values.append(value)
        sleep(REAR_SAMPLE_DELAY)

    if not values:
        return None

    # Sort and trim the highest/lowest readings to reduce ultrasonic spikes.
    values.sort()
    if len(values) >= 10:
        trim = max(1, len(values) // 5)
        values = values[trim:-trim]

    return average(values)


# ================================================================
# FLOOR COLOR SENSOR
# ================================================================
def read_floor_color():
    try:
        detected = color_sensor.color
    except Exception:
        return None

    if detected == ColorSensor.COLOR_BLUE:
        return 'BLUE'

    if detected in ORANGE_COLOR_GROUP:
        return 'ORANGE'

    return None


def stable_floor_color(raw_color):
    global candidate_color, candidate_count
    global release_count, color_event_armed

    if raw_color is None:
        candidate_color = None
        candidate_count = 0

        if release_count < COLOR_RELEASE_READINGS:
            release_count += 1

        if release_count >= COLOR_RELEASE_READINGS:
            color_event_armed = True

        return None

    release_count = 0

    if raw_color == candidate_color:
        candidate_count += 1
    else:
        candidate_color = raw_color
        candidate_count = 1

    if not color_event_armed:
        return None

    if candidate_count >= COLOR_CONFIRM_READINGS:
        color_event_armed = False
        candidate_count = 0
        return candidate_color

    return None


def arm_final_search(position, now):
    global final_search_active
    global final_search_start_position, final_search_start_time
    global rear_match_count, rear_departure_count, rear_return_armed

    if final_search_active:
        return

    final_search_active = True
    final_search_start_position = position
    final_search_start_time = now
    rear_match_count = 0
    rear_departure_count = 0
    rear_return_armed = False
    reset_pid()

    drive.on(SpeedPercent(FINAL_SEARCH_SPEED))

    print('FINAL REAR-US PARKING ARMED at {:.1f}'.format(position))
    print('RECORDED REAR DISTANCE: {}'.format(rear_start_distance))
    show_message('REAR SEARCH', x=15, font='luBS14')


def show_progress():
    # Update only after an accepted curve, so the display does not slow the loop.
    completed_laps = completed_curves // CURVES_PER_LAP
    if completed_curves >= TOTAL_CURVES:
        lap_text = 'LAP 3/3 DONE'
    else:
        current_lap = min(3, completed_laps + 1)
        lap_text = 'LAP {}/3'.format(current_lap)

    try:
        screen.clear()
        screen.text_pixels(lap_text, x=42, y=25, font='luBS14')
        screen.text_pixels('CURVES {}/12'.format(completed_curves),
                           x=32, y=55, font='luBS14')
        screen.update()
    except Exception:
        pass


def register_completed_curve(position, now):
    global completed_curves, last_curve_position, last_curve_time

    if completed_curves >= TOTAL_CURVES:
        return False

    if last_curve_position is not None and last_curve_time is not None:
        distance = position - last_curve_position
        elapsed = now - last_curve_time

        if (distance < MIN_COMPLETED_CURVE_DISTANCE or
                elapsed < MIN_COMPLETED_CURVE_TIME):
            print('CURVE REJECTED: count={} d={:.1f} t={:.2f}'.format(
                completed_curves, distance, elapsed
            ))
            return False

    completed_curves += 1
    last_curve_position = position
    last_curve_time = now

    completed_laps = completed_curves // CURVES_PER_LAP
    current_lap = min(3, completed_laps + 1)

    print('CURVE COUNT: {} | COMPLETED LAPS: {} | CURRENT LAP: {}'.format(
        completed_curves,
        completed_laps,
        current_lap
    ))
    show_progress()

    if completed_curves == TOTAL_CURVES:
        print('TWELFTH CURVE CONFIRMED')
        arm_final_search(position, now)

    return True


def reset_curve_sequence():
    global curve_active, required_exit_color
    global curve_start_position, curve_start_time

    curve_active = False
    required_exit_color = None
    curve_start_position = None
    curve_start_time = None


def update_curve_count(raw_color):
    global curve_active, required_exit_color
    global curve_start_position, curve_start_time
    global run_start_time, start_to_first_curve_time
    global start_to_first_curve_distance, start_row

    if final_search_active:
        return

    position = abs(float(drive.position))
    now = time()
    color = stable_floor_color(raw_color)

    # Recover only when a half-finished sequence has lasted far too long.
    # This does not add a post-curve lockout, so the next real corner remains
    # detectable even when corners are close together.
    if curve_active and curve_start_position is not None:
        sequence_distance = position - curve_start_position
        sequence_time = now - curve_start_time
        if (sequence_distance > CURVE_SEQUENCE_MAX_DISTANCE or
                sequence_time > CURVE_SEQUENCE_MAX_TIME):
            print('CURVE SEQUENCE RESET: missing {} d={:.1f} t={:.2f}'.format(
                required_exit_color, sequence_distance, sequence_time
            ))
            reset_curve_sequence()

    if color is None:
        return

    if not curve_active:
        curve_active = True
        curve_start_position = position
        curve_start_time = now
        required_exit_color = 'ORANGE' if color == 'BLUE' else 'BLUE'

        if completed_curves == 0 and start_to_first_curve_time is None:
            start_to_first_curve_time = now - run_start_time
            start_to_first_curve_distance = position
            start_row = ('LAST ROW' if
                         start_to_first_curve_time >= START_ROW_TIME_THRESHOLD
                         else 'FIRST ROW')
            print('FIRST CURVE START: {} at {:.2f}s / {:.1f} deg'.format(
                color,
                start_to_first_curve_time,
                start_to_first_curve_distance
            ))
            print('START ROW CLASSIFIED: {}'.format(start_row))

        print('CURVE START: {} -> waiting for {}'.format(
            color, required_exit_color
        ))
        return

    if color == required_exit_color:
        pair_distance = position - curve_start_position
        pair_time = now - curve_start_time

        if pair_distance < PAIR_MIN_DISTANCE or pair_time < PAIR_MIN_TIME:
            print('CURVE PAIR REJECTED: d={:.1f} t={:.2f}'.format(
                pair_distance, pair_time
            ))
            return

        if register_completed_curve(position, now):
            reset_curve_sequence()
        return

    # Seeing the same first color again does not count and does not restart the
    # sequence. The code simply keeps waiting for the true opposite color.
    print('WAITING FOR {} | SAW {}'.format(required_exit_color, color))


# ================================================================
# ULTRASONIC + PID
# ================================================================
def valid_distance(value):
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


def steer_away_from_wall(left, right, angle):
    if left is not None and right is not None:
        if left < right:
            set_steering(-angle)
        else:
            set_steering(angle)
    elif left is not None:
        set_steering(-angle)
    elif right is not None:
        set_steering(angle)


def wall_protection(left, right, speed):
    severe = (
        (left is not None and left <= WALL_SEVERE_DISTANCE) or
        (right is not None and right <= WALL_SEVERE_DISTANCE)
    )

    if severe:
        drive.on(SpeedPercent(speed))
        steer_away_from_wall(left, right, SEVERE_WALL_ANGLE)
        reset_pid()
        return True

    gentle = (
        (left is not None and left <= WALL_GENTLE_DISTANCE) or
        (right is not None and right <= WALL_GENTLE_DISTANCE)
    )

    if gentle:
        drive.on(SpeedPercent(speed))
        steer_away_from_wall(left, right, GENTLE_WALL_ANGLE)
        reset_pid()
        return True

    return False


def drive_pid(left, right, speed):
    global integral, last_error

    error = right - left
    integral += error
    integral = clamp(integral, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)
    derivative = error - last_error
    last_error = error

    correction = KP * error + KI * integral + KD * derivative
    steering_angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive.on(SpeedPercent(speed))
    set_steering(steering_angle)


def drive_without_two_walls(left, right, speed):
    drive.on(SpeedPercent(speed))

    if left is not None and right is None and left <= WALL_GENTLE_DISTANCE:
        set_steering(-GENTLE_WALL_ANGLE)
    elif right is not None and left is None and right <= WALL_GENTLE_DISTANCE:
        set_steering(GENTLE_WALL_ANGLE)
    else:
        set_steering(0)


# ================================================================
# FINAL PARKING
# ================================================================
def update_rear_parking(position, now):
    global start_position_found, rear_match_count

    if not final_search_active:
        return False

    # INPUT_4 becomes active again only here, after curve 12.
    drive.on(SpeedPercent(FINAL_SEARCH_SPEED))

    if rear_start_distance is None:
        rear_match_count = 0
        return False

    current_rear = read_rear_distance()
    if current_rear is None:
        rear_match_count = 0
        return False

    error = abs(current_rear - rear_start_distance)

    if error <= REAR_PARK_TOLERANCE_CM:
        rear_match_count += 1
        print('REAR MATCH {}/{} | current={:.1f} target={:.1f} error={:.1f}'.format(
            rear_match_count,
            REAR_MATCH_CONFIRMATIONS,
            current_rear,
            rear_start_distance,
            error
        ))
    else:
        rear_match_count = 0

    if rear_match_count >= REAR_MATCH_CONFIRMATIONS:
        start_position_found = True
        stop_robot()
        print('SAVED REAR DISTANCE REACHED - PARKED')
        print('FINAL REAR: {:.1f} cm | TARGET: {:.1f} cm'.format(
            current_rear, rear_start_distance
        ))
        show_message('PARKED!', x=52, font='luBS18')
        return True

    return False

def final_search_safety_stop(position, now):
    if not final_search_active:
        return False

    if start_position_found:
        return True

    distance = position - final_search_start_position
    elapsed = now - final_search_start_time

    if distance >= FINAL_SEARCH_MAX_DISTANCE:
        print('FINAL SEARCH DISTANCE SAFETY')
        show_message('NO TARGET', x=35, font='luBS18')
        return True

    if elapsed >= FINAL_SEARCH_TIMEOUT:
        print('FINAL SEARCH TIMEOUT')
        show_message('TIMEOUT', x=52, font='luBS18')
        return True

    return False


# ================================================================
# START
# ================================================================
def wait_for_left_button():
    show_message('READY!', x=66, font='luBS24')

    while buttons.left:
        sleep(0.02)
    while not buttons.left:
        sleep(0.02)
    while buttons.left:
        sleep(0.02)


try:
    wait_for_left_button()

    show_message('RECORD REAR', x=14, font='luBS14')
    rear_start_distance = record_rear_start_distance()
    if rear_start_distance is None:
        print('ERROR: NO VALID REAR ULTRASONIC START DISTANCE')
        show_message('REAR ERROR', x=28, font='luBS18')
        raise RuntimeError('Rear ultrasonic sensor did not return a valid start distance')

    print('REAR START DISTANCE: {:.1f} cm'.format(rear_start_distance))

    drive.position = 0
    reset_pid()
    run_start_time = time()
    print('START TIMER ARMED')
    show_message('RUNNING', x=49, font='luBS18')

    while True:
        now = time()
        position = abs(float(drive.position))

        if buttons.backspace:
            break

        if final_search_safety_stop(position, now):
            break

        # INPUT_4 is not read anywhere during normal driving.
        # The floor color sensor alone updates the curve counter.
        update_curve_count(read_floor_color())

        speed = FINAL_SEARCH_SPEED if final_search_active else STRAIGHT_SPEED
        left, right = read_walls()

        # Parking recognition gets first priority after curve 12.
        if update_rear_parking(position, now):
            break

        if wall_protection(left, right, speed):
            pass
        elif left is not None and right is not None:
            drive_pid(left, right, speed)
        else:
            drive_without_two_walls(left, right, speed)

        sleep(LOOP_DELAY)

finally:
    stop_robot()

    if not start_position_found:
        show_message('STOPPED', x=50, font='luBS18')
