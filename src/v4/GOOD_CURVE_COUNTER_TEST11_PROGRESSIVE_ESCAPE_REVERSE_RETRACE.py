#!/usr/bin/env python3
# WRO Future Engineers 2026 - Open Challenge
# Test 11: Earlier progressive avoidance + calibrated sensor fusion.
# Python 3.5.3 / ev3dev2

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3, INPUT_4
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.button import Button
from ev3dev2.display import Display
from time import sleep, time


# Hardware
steering = MediumMotor(OUTPUT_A)
drive = LargeMotor(OUTPUT_B)
left_sensor = UltrasonicSensor(INPUT_1)
right_sensor = UltrasonicSensor(INPUT_2)
front_sensor = UltrasonicSensor(INPUT_3)
color_sensor = ColorSensor(INPUT_4)
buttons = Button()
screen = Display()

left_sensor.mode = 'US-DIST-CM'
right_sensor.mode = 'US-DIST-CM'
front_sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'COL-COLOR'

steering.reset()
sleep(0.5)


# Movement and PID
NORMAL_SPEED = -62
GENTLE_WALL_SPEED = -44
SEVERE_WALL_SPEED = -24
PARKING_SPEED = -28
PARKING_MEDIUM_SPEED = -18
PARKING_CREEP_SPEED = -10
EMERGENCY_REVERSE_SPEED = 28

STEERING_SPEED = 60
STEERING_DEADBAND = 0.8
STEERING_TURN_STEP = 3.0
STEERING_RETURN_STEP = 5.0
PID_CENTER_ERROR_DEADBAND = 1.5
STEER_DIRECTION = 1

MAX_PID_ANGLE = 32
GENTLE_WALL_ANGLE = 14
SEVERE_WALL_ANGLE = 18
SOFT_STEER_START_ANGLE = 10.0
SOFT_STEER_SLOPE = 0.78
FULL_AUTHORITY_START_ANGLE = 24.0

WALL_GENTLE_DISTANCE = 28.0
WALL_SEVERE_DISTANCE = 22.0
FULL_WALL_AVOIDANCE_CM = 15.0

# Calibrate this only if the two diagonal sensors give different readings
# while the robot is physically centered and parallel to the walls:
# SIDE_SENSOR_OFFSET = centered_right_reading - centered_left_reading
SIDE_SENSOR_OFFSET = 0.0

KP = 0.28
KI = 0.001
KD = 0.08
INTEGRAL_LIMIT = 20.0
INTEGRAL_DECAY_ERROR = 2.0
INTEGRAL_DECAY_FACTOR = 0.8
SENSOR_FILTER_ALPHA = 0.65
DERIVATIVE_FILTER_ALPHA = 0.45
FRONT_PID_START_CM = 70.0
FRONT_PID_MAX_ERROR_ASSIST = 10.0
LOOP_DELAY = 0.01


# Front collision recovery
FRONT_TOO_CLOSE_CM = 10.0
FRONT_RECOVERY_DISTANCE_CM = 30.0
FRONT_RECOVERY_CONFIRMATIONS = 3
FRONT_RECOVERY_TIMEOUT = 1.8
FRONT_RECOVERY_LOOP_DELAY = 0.02
REVERSE_MAX_STEER = 10.0
WALL_OVERRIDE_MIN_ANGLE = 8.0


# Curve counter
TOTAL_CURVES = 12
COLOR_CHANGE_WINDOW = 3.0
CURVE_COOLDOWN = 1.5
CORNER_TURN_MIN_ANGLE = 0.1
CORNER_TURN_MIN_TIME = 0.03
POST_COLOR_STEERING_WINDOW = 0.9


# Starting-position memory and finish detection
START_DISTANCE_SAMPLES = 9
START_DISTANCE_SAMPLE_DELAY = 0.03
START_DISTANCE_MAX_ATTEMPTS = 30
FINISH_FRONT_TOLERANCE_CM = 2.0
FINISH_CONFIRMATIONS = 2
FINISH_CROSSING_MAX_STEP_CM = 5.0

# Test 9 parking approach:
# - >12 cm from the remembered front distance: normal parking PID at -28
# - 6-12 cm away: slow to -18
# - <=6 cm away: creep at -10 and cap steering at +/-8 degrees
# This gives PID room to straighten after curve 12 without allowing alignment
# corrections to carry the robot past the actual stopping position.
PARKING_ALIGNMENT_RANGE_CM = 12.0
PARKING_ALIGNMENT_CUTOFF_CM = 6.0
PARKING_CLOSE_MAX_STEER = 8.0


# Runtime state
integral = 0.0
last_error = 0.0
filtered_derivative = 0.0
last_steering_target = 0.0
last_drive_speed = None

filtered_left = None
filtered_right = None
filtered_front = None

first_curve_color = None
first_curve_color_time = None
steering_seen_between_colors = False
steering_start_time = None
steering_direction = 0
waiting_for_post_color_steering = False
pending_second_color = None
pending_second_color_time = None
last_curve_count_time = None
completed_curves = 0

front_too_close_count = 0
start_left_distance = None
start_right_distance = None
start_front_distance = None
finish_match_count = 0
previous_finish_front = None
parking_mode_announced = False


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def valid_distance(value):
    return value is not None and 1.0 <= value <= 255.0


def read_distance(sensor):
    try:
        value = float(sensor.distance_centimeters)
    except Exception:
        return None
    return value if valid_distance(value) else None


def read_distances():
    """Read each ultrasonic sensor exactly once for this loop."""
    return (
        read_distance(left_sensor),
        read_distance(right_sensor),
        read_distance(front_sensor)
    )


def reset_pid():
    global integral, last_error, filtered_derivative
    integral = 0.0
    last_error = 0.0
    filtered_derivative = 0.0


def set_drive_speed(speed, force=False):
    """Avoid resending an unchanged drive command every 0.01 seconds."""
    global last_drive_speed
    speed = round(speed, 2)
    if force or speed != last_drive_speed:
        drive.on(SpeedPercent(speed))
        last_drive_speed = speed


def stop_robot():
    global last_drive_speed
    drive.off(brake=True)
    steering.off(brake=True)
    last_drive_speed = None


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


def reset_curve_sequence():
    global first_curve_color, first_curve_color_time
    global steering_seen_between_colors, steering_start_time, steering_direction
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

    if (
        last_curve_count_time is not None
        and now - last_curve_count_time < CURVE_COOLDOWN
    ):
        return False

    completed_curves += 1
    last_curve_count_time = now
    print('CURVE COUNT: {}/{}'.format(completed_curves, TOTAL_CURVES))
    show_curve_count()
    reset_curve_sequence()
    return True


def update_steering_confirmation(commanded_angle):
    """Confirm steering before or shortly after the second curve color."""
    global steering_seen_between_colors, steering_start_time, steering_direction

    if first_curve_color is None or steering_seen_between_colors:
        return

    if abs(commanded_angle) < CORNER_TURN_MIN_ANGLE:
        steering_start_time = None
        steering_direction = 0
        return

    now = time()
    direction = 1 if commanded_angle > 0 else -1

    if steering_start_time is None or direction != steering_direction:
        steering_start_time = now
        steering_direction = direction
        return

    if now - steering_start_time < CORNER_TURN_MIN_TIME:
        return

    steering_seen_between_colors = True

    if waiting_for_post_color_steering:
        elapsed = now - pending_second_color_time
        if elapsed <= POST_COLOR_STEERING_WINDOW:
            print(
                'CURVE CONFIRMED: {} -> {} -> STEERING {:.2f}s after color'.format(
                    first_curve_color,
                    pending_second_color,
                    elapsed
                )
            )
            register_curve()
            return

    print('STEERING CONFIRMED between colors: {:.1f} deg'.format(commanded_angle))


def set_steering(angle, immediate=False):
    global last_steering_target

    requested = clamp(angle, -90, 90)

    if immediate:
        commanded = requested
    else:
        returning_or_reversing = (
            last_steering_target != 0.0
            and (
                requested * last_steering_target <= 0.0
                or abs(requested) < abs(last_steering_target)
            )
        )
        max_step = (
            STEERING_RETURN_STEP
            if returning_or_reversing
            else STEERING_TURN_STEP
        )
        change = clamp(
            requested - last_steering_target,
            -max_step,
            max_step
        )
        commanded = last_steering_target + change

    commanded = round(clamp(commanded, -90, 90), 1)
    update_steering_confirmation(commanded)

    if abs(commanded - last_steering_target) < STEERING_DEADBAND:
        return

    last_steering_target = commanded
    steering.on_to_position(
        SpeedPercent(STEERING_SPEED),
        int(round(commanded * STEER_DIRECTION)),
        brake=True,
        block=False
    )


def read_floor_color():
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


def update_curve_counter(color):
    global first_curve_color, first_curve_color_time
    global steering_seen_between_colors, steering_start_time, steering_direction
    global waiting_for_post_color_steering
    global pending_second_color, pending_second_color_time

    now = time()

    if (
        last_curve_count_time is not None
        and now - last_curve_count_time < CURVE_COOLDOWN
    ):
        return

    if waiting_for_post_color_steering:
        if now - pending_second_color_time <= POST_COLOR_STEERING_WINDOW:
            return

        print('NO CURVE: no steering within 0.9s after second color')
        first_curve_color = pending_second_color
        first_curve_color_time = pending_second_color_time
        waiting_for_post_color_steering = False
        pending_second_color = None
        pending_second_color_time = None
        steering_seen_between_colors = False
        steering_start_time = None
        steering_direction = 0

    if (
        first_curve_color is not None
        and now - first_curve_color_time > COLOR_CHANGE_WINDOW
    ):
        print('CURVE SEQUENCE EXPIRED')
        reset_curve_sequence()

    if color is None:
        return

    if first_curve_color is None:
        first_curve_color = color
        first_curve_color_time = now
        steering_seen_between_colors = False
        print('CURVE START COLOR: {}'.format(color))
        return

    if color == first_curve_color:
        return

    elapsed = now - first_curve_color_time
    valid_transition = (
        (first_curve_color == 'BLUE' and color == 'ORANGE')
        or (first_curve_color == 'ORANGE' and color == 'BLUE')
    )

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

    first_curve_color = color
    first_curve_color_time = now
    steering_seen_between_colors = False
    steering_start_time = None
    steering_direction = 0


def filter_sensor_value(value, previous):
    if value is None:
        return previous
    if previous is None:
        return value
    return (
        SENSOR_FILTER_ALPHA * value
        + (1.0 - SENSOR_FILTER_ALPHA) * previous
    )


def wall_pid_bias(distance):
    if distance is None or distance >= WALL_GENTLE_DISTANCE:
        return 0.0

    gentle_error = GENTLE_WALL_ANGLE / KP
    severe_error = SEVERE_WALL_ANGLE / KP

    if distance > WALL_SEVERE_DISTANCE:
        amount = (
            (WALL_GENTLE_DISTANCE - distance)
            / (WALL_GENTLE_DISTANCE - WALL_SEVERE_DISTANCE)
        )
        return gentle_error * clamp(amount, 0.0, 1.0)

    amount = (
        (WALL_SEVERE_DISTANCE - distance)
        / (WALL_SEVERE_DISTANCE - FULL_WALL_AVOIDANCE_CM)
    )
    amount = clamp(amount, 0.0, 1.0)
    return gentle_error + (severe_error - gentle_error) * amount


def progressive_wall_override(distance):
    """Increase escape steering smoothly from 22 cm down to 15 cm."""
    if distance is None or distance > WALL_SEVERE_DISTANCE:
        return 0.0

    amount = (
        (WALL_SEVERE_DISTANCE - distance)
        / (WALL_SEVERE_DISTANCE - FULL_WALL_AVOIDANCE_CM)
    )
    return (
        WALL_OVERRIDE_MIN_ANGLE
        + (SEVERE_WALL_ANGLE - WALL_OVERRIDE_MIN_ANGLE)
        * clamp(amount, 0.0, 1.0)
    )


def front_pid_assist(front, steering_error):
    if (
        front is None
        or front >= FRONT_PID_START_CM
        or abs(steering_error) < 0.1
    ):
        return 0.0

    pressure = (
        (FRONT_PID_START_CM - front)
        / (FRONT_PID_START_CM - FRONT_TOO_CLOSE_CM)
    )
    assist = FRONT_PID_MAX_ERROR_ASSIST * clamp(pressure, 0.0, 1.0)
    return assist if steering_error > 0 else -assist


def build_fused_error(left, right, front):
    global filtered_left, filtered_right, filtered_front

    filtered_left = filter_sensor_value(left, filtered_left)
    filtered_right = filter_sensor_value(right, filtered_right)
    filtered_front = filter_sensor_value(front, filtered_front)

    left_used = filtered_left if left is not None else None
    right_used = filtered_right if right is not None else None
    front_used = filtered_front if front is not None else None

    if left_used is not None and right_used is not None:
        # Remove the normal difference caused by diagonally-mounted sensors.
        side_error = (right_used - left_used) - SIDE_SENSOR_OFFSET
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

    error = (
        side_error
        + wall_pid_bias(left_used)
        - wall_pid_bias(right_used)
    )
    return error + front_pid_assist(front_used, error)


def soften_pid_steering(angle, left, right, front):
    magnitude = abs(angle)
    if magnitude <= SOFT_STEER_START_ANGLE:
        return angle

    severe_proximity = (
        (left is not None and left <= WALL_SEVERE_DISTANCE)
        or (right is not None and right <= WALL_SEVERE_DISTANCE)
        or (front is not None and front <= WALL_SEVERE_DISTANCE)
    )

    if severe_proximity and magnitude >= FULL_AUTHORITY_START_ANGLE:
        return angle

    softened = (
        SOFT_STEER_START_ANGLE
        + (magnitude - SOFT_STEER_START_ANGLE) * SOFT_STEER_SLOPE
    )
    softened = clamp(softened, 0.0, MAX_PID_ANGLE)
    return -softened if angle < 0 else softened


def choose_drive_speed(left, right, front):
    severe_side = (
        (left is not None and left <= WALL_SEVERE_DISTANCE)
        or (right is not None and right <= WALL_SEVERE_DISTANCE)
    )
    gentle_side = (
        (left is not None and left <= WALL_GENTLE_DISTANCE)
        or (right is not None and right <= WALL_GENTLE_DISTANCE)
    )

    if severe_side:
        side_speed = SEVERE_WALL_SPEED
    elif gentle_side:
        side_speed = GENTLE_WALL_SPEED
    else:
        side_speed = NORMAL_SPEED

    if front is None or front >= FRONT_PID_START_CM:
        front_speed = NORMAL_SPEED
    elif front <= WALL_SEVERE_DISTANCE:
        front_speed = SEVERE_WALL_SPEED
    elif front <= WALL_GENTLE_DISTANCE:
        amount = (
            (WALL_GENTLE_DISTANCE - front)
            / (WALL_GENTLE_DISTANCE - WALL_SEVERE_DISTANCE)
        )
        front_speed = (
            GENTLE_WALL_SPEED
            + (SEVERE_WALL_SPEED - GENTLE_WALL_SPEED)
            * clamp(amount, 0.0, 1.0)
        )
    else:
        amount = (
            (FRONT_PID_START_CM - front)
            / (FRONT_PID_START_CM - WALL_GENTLE_DISTANCE)
        )
        front_speed = (
            NORMAL_SPEED
            + (GENTLE_WALL_SPEED - NORMAL_SPEED)
            * clamp(amount, 0.0, 1.0)
        )

    return max(side_speed, front_speed)


def drive_sensor_fusion_pid(left, right, front, parking_mode=False):
    global integral, last_error, filtered_derivative

    error = build_fused_error(left, right, front)

    if abs(error) < INTEGRAL_DECAY_ERROR:
        integral *= INTEGRAL_DECAY_FACTOR
    else:
        integral = clamp(integral + error, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)

    if abs(integral) < 0.05:
        integral = 0.0

    raw_derivative = error - last_error
    filtered_derivative = (
        DERIVATIVE_FILTER_ALPHA * raw_derivative
        + (1.0 - DERIVATIVE_FILTER_ALPHA) * filtered_derivative
    )
    last_error = error

    correction = KP * error + KI * integral + KD * filtered_derivative
    angle = clamp(-correction, -MAX_PID_ANGLE, MAX_PID_ANGLE)
    angle = soften_pid_steering(angle, left, right, front)

    # Immediate protection uses the newest unfiltered side readings. Normal
    # centering remains filtered, but a genuinely close wall cannot be hidden
    # by filtering delay. If both sides are close, escape from the closer one.
    left_danger = left is not None and left <= WALL_SEVERE_DISTANCE
    right_danger = right is not None and right <= WALL_SEVERE_DISTANCE

    if left_danger and right_danger:
        angle = (
            -progressive_wall_override(left)
            if left <= right
            else progressive_wall_override(right)
        )
    elif left_danger:
        angle = -progressive_wall_override(left)
    elif right_danger:
        angle = progressive_wall_override(right)

    if left_danger or right_danger:
        # The raw-distance override owns steering here. Clear stored PID force
        # so it cannot continue the turn after the robot leaves the wall.
        integral = 0.0
        filtered_derivative = 0.0
        last_error = error

    speed = choose_drive_speed(left, right, front)

    if parking_mode:
        # Front distance has priority over perfect alignment near the finish.
        # Far away, PID keeps full steering authority so it can recover from a
        # diagonal curve exit. As the saved distance approaches, the robot
        # progressively slows. Inside the final 6 cm, steering is limited so a
        # large late PID correction cannot rotate/push the robot past the target.
        if front is not None and start_front_distance is not None:
            parking_error = abs(front - start_front_distance)

            if parking_error <= PARKING_ALIGNMENT_CUTOFF_CM:
                speed = max(speed, PARKING_CREEP_SPEED)
                angle = clamp(
                    angle,
                    -PARKING_CLOSE_MAX_STEER,
                    PARKING_CLOSE_MAX_STEER
                )

            elif parking_error <= PARKING_ALIGNMENT_RANGE_CM:
                speed = max(speed, PARKING_MEDIUM_SPEED)

            else:
                speed = max(speed, PARKING_SPEED)
        else:
            # If the front reading temporarily disappears, remain slow rather
            # than accidentally returning to normal lap speed.
            speed = max(speed, PARKING_SPEED)

    set_drive_speed(speed)
    set_steering(angle)


def reverse_from_front_wall():
    recovery_start = time()
    safe_count = 0
    recovery_angle = clamp(
        last_steering_target,
        -REVERSE_MAX_STEER,
        REVERSE_MAX_STEER
    )

    reset_pid()
    # Keep a small amount of the previous steering so reverse approximately
    # retraces the approach. Side ultrasonics do not choose reverse direction.
    set_steering(recovery_angle, immediate=True)
    set_drive_speed(EMERGENCY_REVERSE_SPEED, force=True)
    show_curve_count()
    print('FRONT EMERGENCY: reversing away from wall')

    while True:
        if buttons.backspace:
            stop_robot()
            return False

        front = read_distance(front_sensor)
        if front is not None and front >= FRONT_RECOVERY_DISTANCE_CM:
            safe_count += 1
        else:
            safe_count = 0

        if safe_count >= FRONT_RECOVERY_CONFIRMATIONS:
            break
        if time() - recovery_start >= FRONT_RECOVERY_TIMEOUT:
            print('FRONT RECOVERY TIMEOUT')
            break

        sleep(FRONT_RECOVERY_LOOP_DELAY)

    drive.off(brake=True)
    global last_drive_speed
    last_drive_speed = None
    set_steering(0, immediate=True)
    reset_pid()
    show_curve_count()
    print('FRONT RECOVERY COMPLETE')
    return True


def update_front_collision_recovery(front):
    global front_too_close_count

    if front is not None and front <= FRONT_TOO_CLOSE_CM:
        front_too_close_count += 1
    else:
        front_too_close_count = 0

    if front_too_close_count < 1:
        return False

    front_too_close_count = 0
    return reverse_from_front_wall()


def median_distance(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0


def memorize_starting_distances():
    global start_left_distance, start_right_distance, start_front_distance

    samples = [[], [], []]

    for unused_attempt in range(START_DISTANCE_MAX_ATTEMPTS):
        distances = read_distances()

        for index, value in enumerate(distances):
            if value is not None and len(samples[index]) < START_DISTANCE_SAMPLES:
                samples[index].append(value)

        if all(len(group) >= START_DISTANCE_SAMPLES for group in samples):
            break

        sleep(START_DISTANCE_SAMPLE_DELAY)

    if any(not group for group in samples):
        print('START MEMORY ERROR: could not read all ultrasonic sensors')
        return False

    start_left_distance = median_distance(samples[0])
    start_right_distance = median_distance(samples[1])
    start_front_distance = median_distance(samples[2])
    print(
        'START DISTANCES SAVED: LEFT={:.1f} RIGHT={:.1f} FRONT={:.1f}'.format(
            start_left_distance,
            start_right_distance,
            start_front_distance
        )
    )
    return True


def finish_position_reached(left, right, front):
    global finish_match_count, previous_finish_front

    if completed_curves < TOTAL_CURVES:
        finish_match_count = 0
        previous_finish_front = None
        return False

    if (
        start_left_distance is None
        or start_right_distance is None
        or start_front_distance is None
        or front is None
    ):
        finish_match_count = 0
        if front is None:
            previous_finish_front = None
        return False

    front_error = front - start_front_distance
    front_matches = abs(front_error) <= FINISH_FRONT_TOLERANCE_CM
    finish_match_count = finish_match_count + 1 if front_matches else 0

    if finish_match_count >= FINISH_CONFIRMATIONS:
        print('FINISH FRONT-DOMINANT MATCH: {:.1f}/{:.1f}'.format(
            front,
            start_front_distance
        ))
        return True

    crossed = False

    if previous_finish_front is not None:
        previous_error = previous_finish_front - start_front_distance
        crossed = (
            previous_error * front_error <= 0.0
            and abs(front - previous_finish_front) <= FINISH_CROSSING_MAX_STEP_CM
        )

    previous_finish_front = front

    if crossed:
        print('FINISH FRONT TARGET CROSSED: {:.1f}/{:.1f}'.format(
            front,
            start_front_distance
        ))
    return crossed


def wait_for_start_button():
    show_message('PRESS ENTER', x=20, font='luBS18')
    while buttons.enter:
        sleep(0.02)
    while not buttons.enter:
        sleep(0.02)
    while buttons.enter:
        sleep(0.02)


try:
    wait_for_start_button()

    if not memorize_starting_distances():
        stop_robot()
        show_message('SENSOR ERROR', x=20, font='luBS14')
        raise RuntimeError('Could not memorize starting distances')

    drive.position = 0
    reset_pid()
    show_curve_count()
    print('RUN STARTED - TEST 9 PROGRESSIVE PARKING')

    while True:
        if buttons.backspace:
            break

        left, right, front = read_distances()

        if update_front_collision_recovery(front):
            if buttons.backspace:
                break
            sleep(LOOP_DELAY)
            continue

        update_curve_counter(read_floor_color())
        parking_mode = completed_curves >= TOTAL_CURVES

        if parking_mode and not parking_mode_announced:
            parking_mode_announced = True
            print('PARKING MODE ACTIVE - PROGRESSIVE SPEED / CLOSE STEERING LIMIT')

        if finish_position_reached(left, right, front):
            stop_robot()
            print('RUN COMPLETE - ROBOT STOPPED AT SAVED START POSITION')
            break

        drive_sensor_fusion_pid(left, right, front, parking_mode)
        sleep(LOOP_DELAY)

finally:
    stop_robot()
    show_message('STOPPED', x=50, font='luBS18')
