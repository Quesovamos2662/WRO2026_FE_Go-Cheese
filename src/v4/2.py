#!/usr/bin/env python3
# WRO Future Engineers 2026 - Open Challenge
# Python 3.5.3 / ev3dev2
#
# Simple unified PID version.
# All normal steering, wall avoidance, and curve steering pass through one PID.
# The curve counter is preserved.
#
# Curve counter:
#   - Only BLUE -> ORANGE or ORANGE -> BLUE count.
#   - The second color must appear within 3 seconds.
#   - A valid transition counts exactly one curve and updates the counter.
#
# Hardware:
#   Ultrasonic left:   INPUT_1
#   Ultrasonic right:  INPUT_2
#   Ultrasonic front:  INPUT_3
#   Color sensor:      INPUT_4
#   Medium steering:   OUTPUT_A
#   Large drive motor: OUTPUT_B

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
from ev3dev2.sound import Sound
from time import sleep, time


# ================================================================
# HARDWARE
# ================================================================
steering = MediumMotor(OUTPUT_A)
drive = LargeMotor(OUTPUT_B)

left_sensor = UltrasonicSensor(INPUT_1)
right_sensor = UltrasonicSensor(INPUT_2)
front_sensor = UltrasonicSensor(INPUT_3)
color_sensor = ColorSensor(INPUT_4)

buttons = Button()
screen = Display()
sound = Sound()

left_sensor.mode = 'US-DIST-CM'
right_sensor.mode = 'US-DIST-CM'
front_sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'COL-COLOR'

steering.reset()
sleep(0.5)


# ================================================================
# MOVEMENT SETTINGS
# ================================================================
# Negative speed is forward for this robot.
NORMAL_SPEED = -62
GENTLE_WALL_SPEED = -46
SEVERE_WALL_SPEED = -40

# Positive speed is backward.
EMERGENCY_REVERSE_SPEED = 28

# The motor moves quickly, but requested angles still ramp smoothly.
STEERING_SPEED = 70
STEERING_DEADBAND = 0.4
STEERING_TURN_STEP = 3.5
STEERING_RETURN_STEP = 8.0
STEER_DIRECTION = 1
# Use this only to correct a small mechanical centering offset. For example,
# if zero points 2 degrees left, try +2.0 or -2.0 and verify at low speed.
STEERING_CENTER_OFFSET = 0.0

MAX_PID_ANGLE = 30.0

# KEEP THESE DISTANCES THE SAME.
WALL_GENTLE_DISTANCE = 20.0
WALL_SEVERE_DISTANCE = 18.0

KP = 0.62
KI = 0.0
KD = 0.14

INTEGRAL_LIMIT = 0.0

# Filters remove tiny ultrasonic jumps and derivative spikes.
# Higher SENSOR_FILTER_ALPHA = faster response to new sensor readings.
SENSOR_FILTER_ALPHA = 0.75
DERIVATIVE_FILTER_ALPHA = 0.40

# A diagonal sensor can see past a corner and report a very large distance.
# Limit only the values used by steering; safety still uses raw readings.
MAX_CONTROL_DISTANCE_CM = 110.0
MAX_CONTROL_STEP_CM = 18.0

LOOP_DELAY = 0.01


# ================================================================
# MINIMUM-CORRECTION PID STEERING
# ================================================================
# The robot normally commands zero steering. PID activates only for a confirmed
# curve or when a side wall is extremely close.
CURVE_FRONT_TRIGGER_CM = 70.0
CURVE_OPEN_SIDE_MIN_CM = 32.0
CURVE_OPENING_DIFFERENCE_CM = 9.0
CURVE_ERROR_GAIN = 0.85
CURVE_ERROR_MIN = 22.0
CURVE_ERROR_MAX = 46.0

# Start early enough that a small correction can prevent an emergency. Above
# 24 cm the robot still drives straight without continuous centering.
CORRECTION_WALL_DISTANCE_CM = 24.0
WALL_ERROR_GAIN = 2.3
WALL_ERROR_MIN = 8.0
WALL_ERROR_MAX = 28.0

CORRECTION_SPEED = -50


# ================================================================
# FRONT COLLISION RECOVERY
# ================================================================
FRONT_TOO_CLOSE_CM = 5.0
FRONT_RECOVERY_DISTANCE_CM = 55.0
FRONT_RECOVERY_CONFIRMATIONS = 3
FRONT_RECOVERY_TIMEOUT = 4.0
FRONT_RECOVERY_LOOP_DELAY = 0.02


# ================================================================
# CURVE COUNTER SETTINGS
# ================================================================
TOTAL_CURVES = 12

# Maximum time allowed between two different detected colors.
COLOR_CHANGE_WINDOW = 3.0

# After a curve is counted, ignore new curve counts for 1.5 seconds.
CURVE_COOLDOWN = 1.5

# Corner detection:
# Any non-zero steering angle can confirm the turn.
# 0.1 deg is used because steering commands are rounded to one decimal place;
# this prevents perfectly straight (0.0 deg) driving from qualifying.
CORNER_TURN_MIN_ANGLE = 0.1
CORNER_TURN_MIN_TIME = 0.03

# After the opposite/second color is detected, steering is still allowed to
# confirm the same curve for this long.
POST_COLOR_STEERING_WINDOW = 0.9

# Loud beep when one curve is counted.
CURVE_BEEP_FREQUENCY = 1200
CURVE_BEEP_DURATION_MS = 350
CURVE_BEEP_VOLUME = 100


# ================================================================
# STATE
# ================================================================
integral = 0.0
last_error = 0.0
filtered_derivative = 0.0
last_steering_target = 0.0

filtered_left = None
filtered_right = None
filtered_front = None

last_curve_color = None
last_curve_color_time = None
last_curve_count_time = None
# Current possible curve sequence.
first_curve_color = None
first_curve_color_time = None

# True once a qualifying steering movement happens after the first color.
steering_seen_between_colors = False
steering_start_time = None
steering_direction = 0

# If the opposite color arrives before steering is confirmed, keep the same
# curve attempt open briefly so steering just AFTER the second color can count.
waiting_for_post_color_steering = False
pending_second_color = None
pending_second_color_time = None

completed_curves = 0

front_too_close_count = 0

# ================================================================
# GENERAL HELPERS
# ================================================================
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def valid_distance(value):
    return value is not None and 1.0 <= value <= 255.0


def reset_pid():
    global integral, last_error, filtered_derivative
    integral = 0.0
    last_error = 0.0
    filtered_derivative = 0.0


def set_steering(angle, immediate=False):
    global last_steering_target
    global steering_seen_between_colors
    global steering_start_time, steering_direction
    global waiting_for_post_color_steering
    global pending_second_color, pending_second_color_time

    requested_angle = clamp(angle, -90, 90)

    # Test 4 uses different rates for entering and leaving a correction:
    #   - turn-in stays smooth at 2.5 deg/update
    #   - return-to-center or direction reversal is faster at 4.0 deg/update
    if immediate:
        commanded_angle = requested_angle
    else:
        returning_or_reversing = (
            last_steering_target != 0.0
            and (
                requested_angle * last_steering_target <= 0.0
                or abs(requested_angle) < abs(last_steering_target)
            )
        )

        if returning_or_reversing:
            max_step = STEERING_RETURN_STEP
        else:
            max_step = STEERING_TURN_STEP

        difference = requested_angle - last_steering_target
        difference = clamp(
            difference,
            -max_step,
            max_step
        )
        commanded_angle = last_steering_target + difference

    commanded_angle = clamp(commanded_angle, -90, 90)
    commanded_angle = round(commanded_angle, 1)

    now = time()

    # ------------------------------------------------------------
    # STEERING CONFIRMATION BETWEEN THE TWO COLORS
    # ------------------------------------------------------------
    # Confirm the ACTUAL smoothed steering command, not the unsmoothed request.
    if first_curve_color is not None and not steering_seen_between_colors:
        if abs(commanded_angle) >= CORNER_TURN_MIN_ANGLE:
            direction = 1 if commanded_angle > 0 else -1

            if steering_start_time is None or direction != steering_direction:
                steering_start_time = now
                steering_direction = direction

            elif now - steering_start_time >= CORNER_TURN_MIN_TIME:
                steering_seen_between_colors = True

                post_color_counted = False

                if waiting_for_post_color_steering:
                    # The second color already arrived. Steering is still valid
                    # for up to 0.9 s after that color.
                    post_color_elapsed = now - pending_second_color_time

                    if post_color_elapsed <= POST_COLOR_STEERING_WINDOW:
                        print(
                            'CURVE CONFIRMED: {} -> {} -> STEERING '
                            '{:.2f}s after second color'.format(
                                first_curve_color,
                                pending_second_color,
                                post_color_elapsed
                            )
                        )
                        register_curve()
                        post_color_counted = True

                if not post_color_counted:
                    print(
                        'STEERING CONFIRMED between colors: {:.1f} deg'.format(
                            commanded_angle
                        )
                    )
        else:
            steering_start_time = None
            steering_direction = 0

    # Ignore only very tiny final changes. Large requested changes still keep
    # stepping toward their target on the following loops.
    if abs(commanded_angle - last_steering_target) < STEERING_DEADBAND:
        return

    last_steering_target = commanded_angle
    target = int(round(
        commanded_angle * STEER_DIRECTION + STEERING_CENTER_OFFSET
    ))

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
    try:
        screen.clear()
        screen.text_pixels(text, x=x, y=45, font=font)
        screen.update()
    except Exception:
        pass


def show_curve_count():
    try:
        screen.clear()
        screen.text_pixels(
            'CURVES {}/{}'.format(completed_curves, TOTAL_CURVES),
            x=25,
            y=42,
            font='luBS14'
        )
        screen.update()
    except Exception:
        pass


def beep_for_curve():
    # play_tone is non-blocking when play_type is PLAY_NO_WAIT_FOR_COMPLETE.
    try:
        sound.set_volume(CURVE_BEEP_VOLUME)
    except Exception:
        pass

    try:
        sound.play_tone(
            frequency=CURVE_BEEP_FREQUENCY,
            duration=CURVE_BEEP_DURATION_MS,
            volume=CURVE_BEEP_VOLUME,
            play_type=Sound.PLAY_NO_WAIT_FOR_COMPLETE
        )
    except Exception:
        # Fallback for ev3dev2 versions where keyword support differs.
        try:
            sound.tone(
                CURVE_BEEP_FREQUENCY,
                CURVE_BEEP_DURATION_MS,
                play_type=Sound.PLAY_NO_WAIT_FOR_COMPLETE
            )
        except Exception:
            pass


# ================================================================
# FRONT ULTRASONIC
# ================================================================
def read_front_distance():
    try:
        value = float(front_sensor.distance_centimeters)
    except Exception:
        return None

    if not valid_distance(value):
        return None

    return value


def reverse_from_front_wall():
    """Reverse straight until front distance is safely >= 55 cm."""
    recovery_start_time = time()
    safe_reading_count = 0

    reset_pid()
    set_steering(0, immediate=True)
    drive.on(SpeedPercent(EMERGENCY_REVERSE_SPEED))

    # Keep the EV3 display dedicated to the curve counter while running.
    show_curve_count()
    print('FRONT EMERGENCY: reversing away from wall')

    while True:
        if buttons.backspace:
            stop_robot()
            return False

        current_front = read_front_distance()

        if current_front is not None and current_front >= FRONT_RECOVERY_DISTANCE_CM:
            safe_reading_count += 1
        else:
            safe_reading_count = 0

        if safe_reading_count >= FRONT_RECOVERY_CONFIRMATIONS:
            drive.off(brake=True)
            set_steering(0, immediate=True)
            reset_pid()
            show_curve_count()
            print('FRONT RECOVERY COMPLETE')
            return True

        if time() - recovery_start_time >= FRONT_RECOVERY_TIMEOUT:
            drive.off(brake=True)
            set_steering(0, immediate=True)
            reset_pid()
            show_curve_count()
            print('FRONT RECOVERY TIMEOUT')
            return True

        set_steering(0, immediate=True)
        drive.on(SpeedPercent(EMERGENCY_REVERSE_SPEED))
        sleep(FRONT_RECOVERY_LOOP_DELAY)


def update_front_collision_recovery(current_front):
    global front_too_close_count

    # One valid <= 5 cm reading is enough to trigger.
    if current_front is not None and current_front <= FRONT_TOO_CLOSE_CM:
        front_too_close_count += 1
    else:
        front_too_close_count = 0

    if front_too_close_count < 1:
        return False

    front_too_close_count = 0
    return reverse_from_front_wall()


# ================================================================
# COLOR / CURVE COUNTER
# ================================================================
def read_floor_color():
    """
    Only BLUE and ORANGE are relevant for curve counting.

    The EV3 color sensor may classify the orange strip as RED,
    YELLOW, or BROWN depending on lighting.
    """
    try:
        detected = color_sensor.color
    except Exception:
        return None

    if detected == ColorSensor.COLOR_BLUE:
        return 'BLUE'

    if detected in (
        ColorSensor.COLOR_RED,
        ColorSensor.COLOR_YELLOW,
        ColorSensor.COLOR_BROWN
    ):
        return 'ORANGE'

    return None


def reset_curve_sequence():
    global first_curve_color, first_curve_color_time
    global steering_seen_between_colors
    global steering_start_time, steering_direction
    global waiting_for_post_color_steering
    global pending_second_color, pending_second_color_time

    first_curve_color = None
    first_curve_color_time = None

    steering_seen_between_colors = False
    steering_start_time = None
    steering_direction = 0

    waiting_for_post_color_steering = False
    pending_second_color = None
    pending_second_color_time = None


def register_curve():
    global completed_curves, last_curve_count_time

    now = time()

    # Counter-only cooldown. Robot movement is NOT paused.
    if last_curve_count_time is not None:
        if now - last_curve_count_time < CURVE_COOLDOWN:
            return False

    completed_curves += 1
    last_curve_count_time = now

    print('CURVE COUNT: {}/{}'.format(completed_curves, TOTAL_CURVES))
    show_curve_count()

    reset_curve_sequence()
    return True


def update_curve_counter(color):
    """
    A curve can now be confirmed in either timing order:

        BLUE -> STEERING -> ORANGE
        ORANGE -> STEERING -> BLUE

    or, if steering happens slightly late:

        BLUE -> ORANGE -> STEERING within 0.9 s
        ORANGE -> BLUE -> STEERING within 0.9 s

    Requirements:
      - Only BLUE and ORANGE are used.
      - The second color must be the opposite color.
      - The two colors must be detected within 3.0 s.
      - Any non-zero steering angle qualifies.
      - Steering must last at least 0.03 s.
      - Steering may occur before the second color OR up to 0.9 s after it.
      - After a count, the counter has a 1.5 s cooldown.
      - Robot movement continues normally during cooldown.
    """
    global first_curve_color, first_curve_color_time
    global steering_seen_between_colors
    global last_curve_count_time
    global waiting_for_post_color_steering
    global pending_second_color, pending_second_color_time
    global steering_start_time, steering_direction

    now = time()

    # ------------------------------------------------------------
    # COUNTER-ONLY COOLDOWN
    # ------------------------------------------------------------
    if last_curve_count_time is not None:
        if now - last_curve_count_time < CURVE_COOLDOWN:
            return

    # ------------------------------------------------------------
    # WAITING FOR STEERING AFTER THE SECOND COLOR
    # ------------------------------------------------------------
    if waiting_for_post_color_steering:
        if now - pending_second_color_time <= POST_COLOR_STEERING_WINDOW:
            # Do not start another color sequence while this curve attempt is
            # still waiting for its post-color steering confirmation.
            return

        print('NO CURVE: no steering within 0.9s after second color')

        # Preserve the second color as the possible first color of the next
        # sequence, just like the old logic did immediately.
        first_curve_color = pending_second_color
        first_curve_color_time = pending_second_color_time
        waiting_for_post_color_steering = False
        pending_second_color = None
        pending_second_color_time = None
        steering_seen_between_colors = False
        steering_start_time = None
        steering_direction = 0

    # ------------------------------------------------------------
    # EXPIRE AN UNFINISHED FIRST-COLOR SEQUENCE AFTER 3 SECONDS
    # ------------------------------------------------------------
    if first_curve_color is not None:
        if now - first_curve_color_time > COLOR_CHANGE_WINDOW:
            print('CURVE SEQUENCE EXPIRED')
            reset_curve_sequence()

    if color is None:
        return

    # ------------------------------------------------------------
    # FIRST COLOR
    # ------------------------------------------------------------
    if first_curve_color is None:
        first_curve_color = color
        first_curve_color_time = now
        steering_seen_between_colors = False

        print('CURVE START COLOR: {}'.format(color))
        return

    # Repeated detection of the same color does not count.
    if color == first_curve_color:
        return

    elapsed = now - first_curve_color_time

    valid_transition = (
        (first_curve_color == 'BLUE' and color == 'ORANGE') or
        (first_curve_color == 'ORANGE' and color == 'BLUE')
    )

    # ------------------------------------------------------------
    # SECOND COLOR
    # ------------------------------------------------------------
    if valid_transition and elapsed <= COLOR_CHANGE_WINDOW:
        if steering_seen_between_colors:
            print(
                'CURVE CONFIRMED: {} -> STEERING -> {} in {:.2f}s'.format(
                    first_curve_color,
                    color,
                    elapsed
                )
            )
            register_curve()
            return

        # No steering yet: keep THIS SAME curve attempt alive for another
        # 0.9 seconds. set_steering() will count it if steering is confirmed.
        waiting_for_post_color_steering = True
        pending_second_color = color
        pending_second_color_time = now
        steering_start_time = None
        steering_direction = 0

        print(
            'SECOND COLOR: {} -> {}; waiting up to {:.1f}s for steering'.format(
                first_curve_color,
                color,
                POST_COLOR_STEERING_WINDOW
            )
        )
        return

    # Invalid/late transition: start a fresh sequence from the newest color.
    first_curve_color = color
    first_curve_color_time = now
    steering_seen_between_colors = False
    steering_start_time = None
    steering_direction = 0


# ================================================================
# SENSOR-FUSION PID STEERING
# ================================================================
def read_side_walls():
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


def filter_sensor_value(value, previous):
    if value is None:
        return previous

    if previous is None:
        return value

    # Reject a one-loop ultrasonic jump without freezing legitimate corner
    # changes. At the 0.01 s loop rate, real openings can still grow quickly.
    value = clamp(
        value,
        previous - MAX_CONTROL_STEP_CM,
        previous + MAX_CONTROL_STEP_CM
    )

    return (
        SENSOR_FILTER_ALPHA * value
        + (1.0 - SENSOR_FILTER_ALPHA) * previous
    )


def choose_drive_speed(left, right, front):
    # ------------------------------------------------------------
    # SIDE-SENSOR SPEED LIMIT (unchanged behavior)
    # ------------------------------------------------------------
    severe = (
        (left is not None and left <= WALL_SEVERE_DISTANCE) or
        (right is not None and right <= WALL_SEVERE_DISTANCE)
    )

    if severe:
        side_speed = SEVERE_WALL_SPEED
    else:
        gentle = (
            (left is not None and left <= WALL_GENTLE_DISTANCE) or
            (right is not None and right <= WALL_GENTLE_DISTANCE)
        )

        if gentle:
            side_speed = GENTLE_WALL_SPEED
        else:
            side_speed = NORMAL_SPEED

    # ------------------------------------------------------------
    # FRONT-SENSOR SPEED LIMIT
    # ------------------------------------------------------------
    # The front ultrasonic now also affects DRIVE SPEED.
    #
    # At >= 55 cm: keep normal speed.
    # From 55 cm down to 20 cm: slow progressively from NORMAL_SPEED
    # to GENTLE_WALL_SPEED.
    # From 20 cm down to 18 cm: slow progressively toward
    # SEVERE_WALL_SPEED.
    # At <= 18 cm: use severe wall speed.
    #
    # These use distances that already exist in the code; no steering
    # distances, PID gains, or steering behavior are changed.
    if front is None or front >= CURVE_FRONT_TRIGGER_CM:
        front_speed = NORMAL_SPEED

    elif front <= WALL_SEVERE_DISTANCE:
        front_speed = SEVERE_WALL_SPEED

    elif front <= WALL_GENTLE_DISTANCE:
        span = WALL_GENTLE_DISTANCE - WALL_SEVERE_DISTANCE
        amount = (WALL_GENTLE_DISTANCE - front) / span
        amount = clamp(amount, 0.0, 1.0)

        front_speed = (
            GENTLE_WALL_SPEED
            + (SEVERE_WALL_SPEED - GENTLE_WALL_SPEED) * amount
        )

    else:
        span = CURVE_FRONT_TRIGGER_CM - WALL_GENTLE_DISTANCE
        amount = (CURVE_FRONT_TRIGGER_CM - front) / span
        amount = clamp(amount, 0.0, 1.0)

        front_speed = (
            NORMAL_SPEED
            + (GENTLE_WALL_SPEED - NORMAL_SPEED) * amount
        )

    # Forward speeds are negative. The numerically larger value is slower:
    # max(-62, -46) -> -46.
    return max(side_speed, front_speed)


def build_fused_error(left, right, front):
    """
    Build ONE PID error from every available ultrasonic sensor.

    Sign convention:
      positive error -> steer LEFT / away from the left wall
      negative error -> steer RIGHT / away from the right wall
    """
    global filtered_left, filtered_right, filtered_front

    filtered_left = filter_sensor_value(left, filtered_left)
    filtered_right = filter_sensor_value(right, filtered_right)
    filtered_front = filter_sensor_value(front, filtered_front)

    left_used = filtered_left if left is not None else None
    right_used = filtered_right if right is not None else None
    front_used = filtered_front if front is not None else None

    # Very large diagonal readings usually mean the sensor is looking beyond a
    # corner. They remain useful as "open", but cannot dominate the PID.
    if left_used is not None:
        left_used = min(left_used, MAX_CONTROL_DISTANCE_CM)
    if right_used is not None:
        right_used = min(right_used, MAX_CONTROL_DISTANCE_CM)

    # Side difference is the basic centering error. A larger right reading
    # requests a right turn; a larger left reading requests a left turn.
    if left_used is not None and right_used is not None:
        side_error = right_used - left_used

        # Do not chase tiny left/right differences while both walls are safe.
        # This keeps the wheels quiet on straights without slowing real turns.
        if (
            abs(side_error) < PID_CENTER_ERROR_DEADBAND
            and left_used > WALL_GENTLE_DISTANCE
            and right_used > WALL_GENTLE_DISTANCE
        ):
            side_error = 0.0

    elif left_used is not None:
        side_error = max(0.0, WALL_GENTLE_DISTANCE - left_used)

    elif right_used is not None:
        side_error = -max(0.0, WALL_GENTLE_DISTANCE - right_used)

    else:
        side_error = 0.0

    # Diagonal sensors can create a very large difference after looking beyond
    # a corner. Centering must remain corrective, not become another full-turn
    # command. Strong corner demand belongs only to curve_error below.
    side_error = clamp(side_error, -SIDE_ERROR_MAX, SIDE_ERROR_MAX)

    # Continuous wall repulsion. It grows only when a side is inside 20 cm.
    left_close = 0.0
    right_close = 0.0
    if left_used is not None:
        left_close = max(0.0, WALL_GENTLE_DISTANCE - left_used)
    if right_used is not None:
        right_close = max(0.0, WALL_GENTLE_DISTANCE - right_used)

    wall_error = WALL_ERROR_GAIN * (left_close - right_close)

    # Curve demand is part of the PID error. The front sensor only controls
    # how strongly the PID follows the side opening; it never chooses a side.
    curve_error = 0.0
    if (
        left_used is not None
        and right_used is not None
        and front_used is not None
        and front_used < CURVE_FRONT_TRIGGER_CM
        and min(left_used, right_used) <= CURVE_NEAR_WALL_MAX_CM
    ):
        opening = right_used - left_used
        open_side = max(left_used, right_used)

        if (
            open_side >= CURVE_OPEN_SIDE_MIN_CM
            and abs(opening) >= CURVE_OPENING_DIFFERENCE_CM
        ):
            front_pressure = (
                CURVE_FRONT_TRIGGER_CM - front_used
            ) / (CURVE_FRONT_TRIGGER_CM - FRONT_TOO_CLOSE_CM)
            front_pressure = clamp(front_pressure, 0.0, 1.0)
            curve_error = opening * CURVE_ERROR_GAIN * (0.45 + front_pressure)
            curve_error = clamp(curve_error, -CURVE_ERROR_MAX, CURVE_ERROR_MAX)

            # Never let curve assistance request a turn toward a wall that is
            # already inside the existing 20 cm protection distance.
            if curve_error < 0.0 and left_used <= WALL_GENTLE_DISTANCE:
                curve_error = 0.0
            elif curve_error > 0.0 and right_used <= WALL_GENTLE_DISTANCE:
                curve_error = 0.0

    return side_error + wall_error + curve_error


def drive_sensor_fusion_pid(left, right, front):
    global integral, last_error, filtered_derivative

    error = build_fused_error(left, right, front)

    # Remove stored steering quickly when the required direction changes. This
    # helps the wheels straighten instead of carrying curve error toward the
    # inner wall.
    if error * last_error < 0.0:
        integral *= 0.35

    if abs(error) < INTEGRAL_DECAY_ERROR:
        integral *= INTEGRAL_DECAY_FACTOR
    elif abs(error) < CURVE_ERROR_MAX:
        integral += error
        integral = clamp(integral, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)

    if abs(integral) < 0.05:
        integral = 0.0

    raw_derivative = error - last_error
    filtered_derivative = (
        DERIVATIVE_FILTER_ALPHA * raw_derivative
        + (1.0 - DERIVATIVE_FILTER_ALPHA) * filtered_derivative
    )
    last_error = error

    correction = (
        KP * error
        + KI * integral
        + KD * filtered_derivative
    )

    steering_angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive_speed = choose_drive_speed(left, right, front)

    if abs(steering_angle) >= HIGH_STEERING_ANGLE:
        drive_speed = max(drive_speed, HIGH_STEERING_SPEED)

    drive.on(SpeedPercent(drive_speed))
    set_steering(steering_angle)


# ================================================================
# MINIMUM-CORRECTION CONTROLLER
# ================================================================
# These final definitions replace the earlier continuous-centering controller.
# The curve counter above is intentionally unchanged.
def required_pid_error(left, right, front):
    """Return a PID error only when steering is genuinely necessary."""
    global filtered_left, filtered_right, filtered_front

    filtered_left = filter_sensor_value(left, filtered_left)
    filtered_right = filter_sensor_value(right, filtered_right)
    filtered_front = filter_sensor_value(front, filtered_front)

    # ------------------------------------------------------------
    # 1. EXTREMELY CLOSE SIDE WALL: highest normal-steering priority
    # ------------------------------------------------------------
    left_danger = (
        left is not None and left <= CORRECTION_WALL_DISTANCE_CM
    )
    right_danger = (
        right is not None and right <= CORRECTION_WALL_DISTANCE_CM
    )

    if left_danger or right_danger:
        left_depth = 0.0
        right_depth = 0.0

        if left_danger:
            left_depth = CORRECTION_WALL_DISTANCE_CM - left
        if right_danger:
            right_depth = CORRECTION_WALL_DISTANCE_CM - right

        wall_error = WALL_ERROR_GAIN * (left_depth - right_depth)

        # Even the first dangerous reading must create a useful correction.
        if wall_error > 0.0:
            wall_error = max(wall_error, WALL_ERROR_MIN)
        elif wall_error < 0.0:
            wall_error = min(wall_error, -WALL_ERROR_MIN)
        elif left_danger and not right_danger:
            wall_error = WALL_ERROR_MIN
        elif right_danger and not left_danger:
            wall_error = -WALL_ERROR_MIN

        # Wall avoidance must remain preventive and gentle. Curves retain the
        # larger steering range, but proximity corrections cannot escalate into
        # a sudden maximum-angle command.
        wall_error = clamp(
            wall_error,
            -WALL_ERROR_MAX,
            WALL_ERROR_MAX
        )

        return wall_error, True

    # ------------------------------------------------------------
    # 2. CONFIRMED CURVE: front wall plus one clearly open side
    # ------------------------------------------------------------
    if (
        filtered_left is not None
        and filtered_right is not None
        and filtered_front is not None
        and filtered_front <= CURVE_FRONT_TRIGGER_CM
    ):
        left_used = min(filtered_left, MAX_CONTROL_DISTANCE_CM)
        right_used = min(filtered_right, MAX_CONTROL_DISTANCE_CM)
        opening = right_used - left_used

        if (
            max(left_used, right_used) >= CURVE_OPEN_SIDE_MIN_CM
            and abs(opening) >= CURVE_OPENING_DIFFERENCE_CM
        ):
            curve_error = abs(opening) * CURVE_ERROR_GAIN
            curve_error = clamp(
                curve_error,
                CURVE_ERROR_MIN,
                CURVE_ERROR_MAX
            )

            if opening < 0.0:
                curve_error = -curve_error

            return curve_error, True

    # Safe/open path: do not continuously center between the walls.
    return 0.0, False


def drive_sensor_fusion_pid(left, right, front):
    """Drive straight unless a close wall or confirmed curve needs PID."""
    global integral, last_error, filtered_derivative

    error, correction_needed = required_pid_error(left, right, front)

    if not correction_needed:
        reset_pid()
        drive_speed = NORMAL_SPEED

        drive.on(SpeedPercent(drive_speed))
        set_steering(0.0)
        return

    # P + filtered D. Integral is deliberately zero so one curve cannot leave
    # stored steering that affects a later lap.
    raw_derivative = error - last_error
    filtered_derivative = (
        DERIVATIVE_FILTER_ALPHA * raw_derivative
        + (1.0 - DERIVATIVE_FILTER_ALPHA) * filtered_derivative
    )
    last_error = error

    correction = KP * error + KD * filtered_derivative
    steering_angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)

    drive_speed = CORRECTION_SPEED
    drive.on(SpeedPercent(drive_speed))
    set_steering(steering_angle)


# ================================================================
# START
# ================================================================
def wait_for_start_button():
    show_message('PRESS ENTER', x=20, font='luBS18')

    while buttons.enter:
        sleep(0.02)

    while not buttons.enter:
        sleep(0.02)

    while buttons.enter:
        sleep(0.02)


# ================================================================
# MAIN PROGRAM
# ================================================================
try:
    wait_for_start_button()

    drive.position = 0
    reset_pid()
    show_curve_count()

    print('RUN STARTED')
    print('Curve rule: opposite colors within 3s; steering before or <=0.9s after second color')

    while True:
        if buttons.backspace:
            break

        # ----------------------------------------------------------
        # 1. FRONT COLLISION SAFETY HAS HIGHEST PRIORITY
        # ----------------------------------------------------------
        current_front = read_front_distance()

        if update_front_collision_recovery(current_front):
            if buttons.backspace:
                break

            sleep(LOOP_DELAY)
            continue

        # ----------------------------------------------------------
        # 2. CURVE COUNTING
        # ----------------------------------------------------------
        update_curve_counter(read_floor_color())

        # ----------------------------------------------------------
        # 3. READ SIDE WALLS
        # ----------------------------------------------------------
        left, right = read_side_walls()

        # ----------------------------------------------------------
        # 4. MINIMUM-CORRECTION PID
        # ----------------------------------------------------------
        drive_sensor_fusion_pid(
            left,
            right,
            current_front
        )

        sleep(LOOP_DELAY)

finally:
    stop_robot()
    show_message('STOPPED', x=50, font='luBS18')
 
