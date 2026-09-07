#!/usr/bin/env python3
# ================================================================
# WRO Future Engineers 2026 - Obstacle Challenge
# Go!Cheese Team - Cheese v4
# Python 3.5.3 / ev3dev2
# ================================================================
#
# Obstacle Challenge testing version.
#
# This file is based on the current Cheese v4 navigation structure,
# but includes the HuskyLens + Arduino Nano obstacle system.
#
# The robot uses:
#   - EV3 for drive, steering, ultrasonic sensors, and color sensor.
#   - Arduino Nano as the communication bridge for the HuskyLens.
#   - HuskyLens Color Recognition for red and green pillar detection.
#
# Current obstacle rule:
#   - Red pillar   = ID 1 -> pass on the right
#   - Green pillar = ID 2 -> pass on the left
#
# The Nano sends one serial packet at a time to the EV3:
#   - R,xCenter,width  -> red pillar detected
#   - G,xCenter,width  -> green pillar detected
#   - N,0,0            -> no valid pillar detected
#
# Current status:
#   - The obstacle logic is already connected to movement.
#   - The system is still being calibrated for camera angle,
#     late detection, obstacle recovery, and obstacle parking.
#
# Main idea:
#   Normal navigation keeps the robot moving through the track.
#   When a fresh pillar detection is received, the camera adds a
#   steering bias so the robot passes the pillar on the correct side.
#   If the pillar is lost, camera steering is cleared and normal
#   steering resumes.
#
# Hardware:
#   Ultrasonic left:    INPUT_1
#   Ultrasonic right:   INPUT_2
#   Ultrasonic front:   INPUT_3
#   Color sensor:       INPUT_4
#   Medium steering:    OUTPUT_A
#   Large drive motor:  OUTPUT_B
#   Arduino Nano:       EV3 USB port
#   HuskyLens:          Connected to Arduino Nano
#
# ================================================================

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
import threading
import serial


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
NORMAL_SPEED = -38
GENTLE_WALL_SPEED = -32
SEVERE_WALL_SPEED = -28

# Positive speed is backward.
EMERGENCY_REVERSE_SPEED = 28

# The motor moves quickly, but requested angles still ramp smoothly.
STEERING_SPEED = 70
STEERING_DEADBAND = 0.4
STEERING_TURN_STEP = 4.65
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
# HUSKYLENS PILLAR AVOIDANCE (Nano over USB serial)
# ================================================================
# The Nano sends one line at a time as: R,xCenter,width / G,xCenter,width /
# N,0,0. HuskyLens Color Recognition must be trained as ID1=RED, ID2=GREEN.
HUSKY_PORT = '/dev/ttyUSB0'
HUSKY_BAUD = 115200

# Ignore distant/noisy blocks below this width. Width is still used to slow the
# robot and to reject tiny detections, but steering is now driven mainly by the
# pillar's horizontal image position, as in ShahroodRC's controller.
PILLAR_MIN_WIDTH = 6
PILLAR_FULL_WIDTH = 30
PILLAR_INITIAL_RAMP = 0.60
PILLAR_BIAS_ANGLE = 30.0
PILLAR_BIAS_SMOOTHING = 0.70
PILLAR_STALE_S = 0.15
PILLAR_APPROACH_SPEED = -18

# HuskyLens uses an approximately 0..320 horizontal coordinate. Instead of a
# fixed color angle, make each pillar move toward a color-specific image point:
# RED at the left of the image -> robot passes on its right.
# GREEN at the right of the image -> robot passes on its left.
CAMERA_CENTER_X = 160.0
PILLAR_TARGET_X = {'RED': 70.0, 'GREEN': 250.0}
PILLAR_X_GAIN = 0.55
PILLAR_MIN_DIRECTION_ANGLE = 12.0

# Cheese's physical steering motor uses the opposite sign from the logical
# camera convention: negative motor angle turns right, positive turns left.
# Apply this only to pillar steering so curve and wall steering stay unchanged.
PILLAR_STEERING_SIGN = -1.0

# Camera movement toward a wall fades out as that wall approaches the existing
# 24 cm correction threshold. It is unrestricted at/above 40 cm.
PILLAR_WALL_SAFE_CM = 24.0
PILLAR_WALL_FREE_CM = 40.0


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
WALL_ERROR_GAIN = 1.8
WALL_ERROR_MIN = 8.0
WALL_ERROR_MAX = 24.0

CORRECTION_SPEED = -35


# ================================================================
# STRAIGHT-PATH ALIGNMENT AFTER CURVES
# ================================================================
# Curve steering remains strong. Once the new corridor is clearly open, the
# wheels are centered immediately and this small controller makes the robot's
# body parallel to the two walls. Pillar steering always overrides it.
STRAIGHT_ALIGNMENT_GAIN = 0.20
STRAIGHT_ALIGNMENT_MAX_ANGLE = 7.0
STRAIGHT_ALIGNMENT_DEADBAND_CM = 3.0

# Require several consecutive open readings before declaring that the corner
# has ended. At a 0.01 s loop this is deliberately fast but rejects one spike.
CURVE_EXIT_FRONT_CLEAR_CM = 70.0
CURVE_EXIT_SIDE_CLEAR_CM = 20.0
CURVE_EXIT_CONFIRMATIONS = 4


# ================================================================
# FRONT COLLISION RECOVERY
# ================================================================
FRONT_TOO_CLOSE_CM = 10.0
FRONT_RECOVERY_DISTANCE_CM = 70.0
FRONT_RECOVERY_CONFIRMATIONS = 3
FRONT_RECOVERY_TIMEOUT = 4.0
FRONT_RECOVERY_LOOP_DELAY = 0.02


# ================================================================
# CURVE COUNTER SETTINGS
# ================================================================
TOTAL_CURVES = 12

# Maximum time allowed between two different detected colors.
COLOR_CHANGE_WINDOW = 3.0

# After a curve is counted, ignore new curve counts for 2.5 seconds.
CURVE_COOLDOWN = 2.5

# Loud beep when one curve is counted.
CURVE_BEEP_FREQUENCY = 1200
CURVE_BEEP_DURATION_MS = 350
CURVE_BEEP_VOLUME = 100


# ================================================================
# FINISH / STARTING-POSITION MEMORY
# ================================================================
# After ENTER is pressed, the robot samples all three ultrasonic sensors while
# stationary and remembers the starting position.
START_DISTANCE_SAMPLES = 9
START_DISTANCE_SAMPLE_DELAY = 0.03
START_DISTANCE_MAX_ATTEMPTS = 30

# The front wall is the actual stopping reference. Ultrasonic readings are not
# perfectly noise-free, so Test 8 uses a +/- 2.0 cm front window.
# Side sensors no longer gate the normal parking stop. They are only used as a
# very loose sanity check for the backup target-crossing stop.
FINISH_FRONT_TOLERANCE_CM = 2.0
FINISH_SIDE_TOLERANCE_CM = 25.0
FINISH_CONFIRMATIONS = 2

# Test 8 parking behavior. Once 12/12 (or higher) is reached, the robot keeps
# the SAME sensor-fusion PID steering but moves much more slowly. This gives the
# ultrasonic sensors enough time to recognize the saved starting position.
PARKING_SPEED = -28

# Backup stop condition: if the robot passes from one side of the saved FRONT
# distance to the other while at least ONE side still resembles the start, stop
# rather than continuing for another lap. A maximum sample-to-sample change rejects
# unrealistic ultrasonic jumps at corners.
FINISH_CROSSING_MAX_STEP_CM = 5.0


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

# Used for color-entry detection. Holding the sensor over the same strip does
# not create another event after the counter cooldown ends.
previous_floor_color = None

completed_curves = 0

front_too_close_count = 0

start_left_distance = None
start_right_distance = None
start_front_distance = None
finish_match_count = 0
previous_finish_front = None
parking_mode_announced = False

# Latest camera packet. The serial thread is the only writer; the navigation
# loop reads a consistent snapshot while holding husky_lock.
husky_color = None
husky_x_center = 0
husky_width = 0
husky_last_update = 0.0
husky_lock = threading.Lock()

pillar_bias = 0.0
pillar_speed_ramp = 0.0
pillar_debug_last_color = 'UNSET'
pillar_just_lost = False

# Navigation phase prevents straight alignment from fighting a corner.
navigation_phase = 'STRAIGHT'
curve_exit_clear_count = 0

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


def median_distance(values):
    """Return the median of a non-empty list of distance samples."""
    ordered = sorted(values)
    middle = len(ordered) // 2

    if len(ordered) % 2 == 1:
        return ordered[middle]

    return (ordered[middle - 1] + ordered[middle]) / 2.0


# ================================================================
# HUSKYLENS SERIAL + PILLAR CONTROL
# ================================================================
def husky_reader_thread():
    """Continuously receive the Nano's latest confirmed pillar packet."""
    global husky_color, husky_x_center, husky_width, husky_last_update

    try:
        ser = serial.Serial(HUSKY_PORT, HUSKY_BAUD, timeout=0.5)
    except Exception as exc:
        print('HUSKYLENS SERIAL OPEN FAILED on {}: {}'.format(HUSKY_PORT, exc))
        return

    print('HUSKYLENS SERIAL OPENED on {}'.format(HUSKY_PORT))

    while True:
        try:
            line = ser.readline().decode('ascii', errors='ignore').strip()
        except Exception:
            continue

        if not line:
            continue

        parts = line.split(',')
        if len(parts) != 3:
            continue

        color_code, x_text, width_text = parts
        try:
            x_center = int(x_text)
            width = int(width_text)
        except ValueError:
            continue

        with husky_lock:
            if color_code == 'R':
                husky_color, husky_x_center, husky_width = 'RED', x_center, width
            elif color_code == 'G':
                husky_color, husky_x_center, husky_width = 'GREEN', x_center, width
            else:
                husky_color, husky_x_center, husky_width = None, 0, 0
            husky_last_update = time()


def read_pillar(now):
    """Return fresh (color, x, width), otherwise (None, 0, 0)."""
    with husky_lock:
        color = husky_color
        x_center = husky_x_center
        width = husky_width
        updated = husky_last_update

    if color is None or width < PILLAR_MIN_WIDTH:
        return None, 0, 0
    if now - updated > PILLAR_STALE_S:
        return None, 0, 0
    return color, x_center, width


def pillar_proximity_ramp(width):
    """Give every confirmed pillar an immediate demand, then grow to 1."""
    distance_ramp = clamp(
        (width - PILLAR_MIN_WIDTH) /
        float(PILLAR_FULL_WIDTH - PILLAR_MIN_WIDTH),
        0.0,
        1.0
    )
    return PILLAR_INITIAL_RAMP + (1.0 - PILLAR_INITIAL_RAMP) * distance_ramp


def pillar_wall_clearance(distance):
    """Reduce camera movement as its requested side approaches a wall."""
    if distance is None:
        return 1.0
    return clamp(
        (distance - PILLAR_WALL_SAFE_CM) /
        float(PILLAR_WALL_FREE_CM - PILLAR_WALL_SAFE_CM),
        0.0,
        1.0
    )


def pillar_desired_x(color, width):
    """Return the color-specific passing target in the camera image."""
    return PILLAR_TARGET_X[color]


def pillar_bias_target(color, x_center, width, left, right):
    if color is None:
        return 0.0

    desired_x = pillar_desired_x(color, width)
    raw_bias = clamp(
        (x_center - desired_x) * PILLAR_X_GAIN,
        -PILLAR_BIAS_ANGLE,
        PILLAR_BIAS_ANGLE
    )

    # Restore the strong minimum response so small/early detections cannot be
    # reduced to zero by the image-position formula.
    if color == 'RED':
        raw_bias = max(PILLAR_MIN_DIRECTION_ANGLE, abs(raw_bias))
    elif color == 'GREEN':
        raw_bias = -max(PILLAR_MIN_DIRECTION_ANGLE, abs(raw_bias))
    else:
        raw_bias = 0.0

    # Give the first small-but-valid sighting an immediate response, then let
    # the command reach full strength as confidence/size grows.
    raw_bias *= pillar_proximity_ramp(width)

    # Convert the logical RED-right / GREEN-left command to Cheese's actual
    # steering-motor sign without changing PID or curve steering signs.
    raw_bias *= PILLAR_STEERING_SIGN

    # Limit using the WRO passing direction, not the motor sign: RED moves the
    # robot right and GREEN moves it left.
    limiting_wall = right if color == 'RED' else left
    return raw_bias * pillar_wall_clearance(limiting_wall)


def update_pillar_control(color, x_center, width, left, right):
    """Return smoothed (steering bias, speed) for the latest camera reading."""
    global pillar_bias, pillar_speed_ramp, pillar_debug_last_color
    global pillar_just_lost

    pillar_just_lost = False

    # The moment the block leaves the camera view, discard all stored camera
    # steering and slowdown. Normal wall/curve/straight control takes over in
    # this same navigation loop, so no old pillar turn can remain active.
    if color is None:
        pillar_just_lost = pillar_debug_last_color in ('RED', 'GREEN')
        pillar_bias = 0.0
        pillar_speed_ramp = 0.0

        if pillar_debug_last_color != 'LOST':
            print('PILLAR LOST | NORMAL STEERING RESUMED')
            pillar_debug_last_color = 'LOST'

        return 0.0, NORMAL_SPEED

    target_bias = pillar_bias_target(
        color, x_center, width, left, right
    )
    target_speed_ramp = (
        pillar_proximity_ramp(width) if color is not None else 0.0
    )

    pillar_bias += (
        target_bias - pillar_bias
    ) * PILLAR_BIAS_SMOOTHING
    pillar_speed_ramp += (
        target_speed_ramp - pillar_speed_ramp
    ) * PILLAR_BIAS_SMOOTHING

    if color != pillar_debug_last_color:
        print('PILLAR {} | x={} width={} target={:.1f} deg'.format(
            color if color else 'LOST', x_center, width, target_bias
        ))
        pillar_debug_last_color = color

    speed = (
        NORMAL_SPEED
        + (PILLAR_APPROACH_SPEED - NORMAL_SPEED) * pillar_speed_ramp
    )
    return pillar_bias, speed


def memorize_starting_distances():
    """
    Sample LEFT, RIGHT, and FRONT while the robot is stationary immediately
    after ENTER is pressed. Median sampling rejects occasional ultrasonic spikes.
    """
    global start_left_distance, start_right_distance, start_front_distance

    left_samples = []
    right_samples = []
    front_samples = []

    attempts = 0
    while attempts < START_DISTANCE_MAX_ATTEMPTS:
        attempts += 1

        left, right = read_side_walls()
        front = read_front_distance()

        if left is not None and len(left_samples) < START_DISTANCE_SAMPLES:
            left_samples.append(left)

        if right is not None and len(right_samples) < START_DISTANCE_SAMPLES:
            right_samples.append(right)

        if front is not None and len(front_samples) < START_DISTANCE_SAMPLES:
            front_samples.append(front)

        if (
            len(left_samples) >= START_DISTANCE_SAMPLES
            and len(right_samples) >= START_DISTANCE_SAMPLES
            and len(front_samples) >= START_DISTANCE_SAMPLES
        ):
            break

        sleep(START_DISTANCE_SAMPLE_DELAY)

    if not left_samples or not right_samples or not front_samples:
        print('START MEMORY ERROR: could not read all three ultrasonic sensors')
        return False

    start_left_distance = median_distance(left_samples)
    start_right_distance = median_distance(right_samples)
    start_front_distance = median_distance(front_samples)

    print(
        'START DISTANCES SAVED: LEFT={:.1f} cm RIGHT={:.1f} cm FRONT={:.1f} cm'.format(
            start_left_distance,
            start_right_distance,
            start_front_distance
        )
    )
    return True


def finish_position_reached(left, right, front):
    """
    After 12/12 (or 13/12, etc.), detect the original starting position.

    Normal finish:
      - FRONT is the dominant parking reference and must be within +/- 2.0 cm.
      - LEFT/RIGHT do NOT gate this normal stop.
      - Two consecutive FRONT matches reject isolated sensor noise while stopping fast.

    Backup finish:
      - If FRONT crosses the saved FRONT distance between two consecutive
        readings, at least ONE side must only be loosely near the start (+/- 25 cm).
      - Large front-sensor jumps are rejected so a corner cannot fake a crossing.
    """
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
        # FRONT is essential. If it disappears, discard the previous sample so
        # we never infer a target crossing across a gap in front-sensor data.
        if front is None:
            previous_finish_front = None
        return False

    front_error = front - start_front_distance

    # Test 8: side sensors are support-only for parking. They do NOT decide the
    # normal stop. This broad sanity check is used only by the backup crossing
    # condition, reducing their influence substantially.
    left_matches = (
        left is not None
        and abs(left - start_left_distance) <= FINISH_SIDE_TOLERANCE_CM
    )
    right_matches = (
        right is not None
        and abs(right - start_right_distance) <= FINISH_SIDE_TOLERANCE_CM
    )
    side_sanity_match = left_matches or right_matches

    front_matches = abs(front_error) <= FINISH_FRONT_TOLERANCE_CM

    # ------------------------------------------------------------
    # 1. NORMAL REPEATED-MATCH STOP
    # ------------------------------------------------------------
    if front_matches:
        finish_match_count += 1
    else:
        finish_match_count = 0

    if finish_match_count >= FINISH_CONFIRMATIONS:
        print(
            'FINISH FRONT-DOMINANT MATCH: LEFT={}/{} RIGHT={}/{} FRONT={:.1f}/{:.1f}'.format(
                'NA' if left is None else '{:.1f}'.format(left),
                '{:.1f}'.format(start_left_distance),
                'NA' if right is None else '{:.1f}'.format(right),
                '{:.1f}'.format(start_right_distance),
                front,
                start_front_distance
            )
        )
        return True

    # ------------------------------------------------------------
    # 2. BACKUP TARGET-CROSSING STOP
    # ------------------------------------------------------------
    crossed_front_target = False

    if previous_finish_front is not None and side_sanity_match:
        previous_error = previous_finish_front - start_front_distance
        front_step = abs(front - previous_finish_front)

        # Sign changed (or one sample landed exactly on the target), therefore
        # the robot physically passed the remembered front-distance plane.
        crossed_front_target = (
            previous_error * front_error <= 0.0
            and front_step <= FINISH_CROSSING_MAX_STEP_CM
        )

    previous_finish_front = front

    if crossed_front_target:
        print(
            'FINISH FRONT TARGET CROSSED: LEFT={}/{} RIGHT={}/{} FRONT={:.1f}/{:.1f}'.format(
                'NA' if left is None else '{:.1f}'.format(left),
                '{:.1f}'.format(start_left_distance),
                'NA' if right is None else '{:.1f}'.format(right),
                '{:.1f}'.format(start_right_distance),
                front,
                start_front_distance
            )
        )
        return True

    return False


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

    if detected == ColorSensor.COLOR_RED:
        return 'ORANGE'

    return None


def reset_curve_sequence():
    global first_curve_color, first_curve_color_time

    first_curve_color = None
    first_curve_color_time = None


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
    A curve is confirmed by a fresh opposite-color transition:

        BLUE -> ORANGE
        ORANGE -> BLUE

    Requirements:
      - Only BLUE and ORANGE are used.
      - The second color must be the opposite color.
      - The two colors must be detected within 3.0 s.
      - After a count, the counter has a 2.5 s cooldown.
      - A color is processed only when the sensor newly enters that color.
      - Robot movement continues normally during cooldown.
    """
    global first_curve_color, first_curve_color_time
    global last_curve_count_time
    global previous_floor_color

    now = time()

    # Record color changes even during cooldown. This prevents a color that is
    # already beneath the sensor when cooldown ends from starting a new curve.
    new_color_entry = color is not None and color != previous_floor_color
    previous_floor_color = color

    # ------------------------------------------------------------
    # COUNTER-ONLY COOLDOWN
    # ------------------------------------------------------------
    if last_curve_count_time is not None:
        if now - last_curve_count_time < CURVE_COOLDOWN:
            return

    # ------------------------------------------------------------
    # EXPIRE AN UNFINISHED FIRST-COLOR SEQUENCE AFTER 3 SECONDS
    # ------------------------------------------------------------
    if first_curve_color is not None:
        if now - first_curve_color_time > COLOR_CHANGE_WINDOW:
            print('CURVE SEQUENCE EXPIRED')
            reset_curve_sequence()

    if color is None:
        return

    # Process only the first loop after entering a blue/orange region.
    if not new_color_entry:
        return

    # ------------------------------------------------------------
    # FIRST COLOR
    # ------------------------------------------------------------
    if first_curve_color is None:
        first_curve_color = color
        first_curve_color_time = now

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
        print(
            'CURVE CONFIRMED: {} -> {} in {:.2f}s'.format(
                first_curve_color,
                color,
                elapsed
            )
        )
        register_curve()
        return

    # Invalid/late transition: start a fresh sequence from the newest color.
    first_curve_color = color
    first_curve_color_time = now


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
    global navigation_phase, curve_exit_clear_count

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
            navigation_phase = 'CURVE'
            curve_exit_clear_count = 0

            curve_error = abs(opening) * CURVE_ERROR_GAIN
            curve_error = clamp(
                curve_error,
                CURVE_ERROR_MIN,
                CURVE_ERROR_MAX
            )

            if opening < 0.0:
                curve_error = -curve_error

            return curve_error, True

    # The curve demand has disappeared. Do not immediately enable centering,
    # because the robot can still be rotating inside the corner.
    if navigation_phase == 'CURVE':
        navigation_phase = 'CURVE_EXIT'
        curve_exit_clear_count = 0

    if navigation_phase == 'CURVE_EXIT':
        exit_is_clear = (
            front is not None
            and left is not None
            and right is not None
            and front >= CURVE_EXIT_FRONT_CLEAR_CM
            and left >= CURVE_EXIT_SIDE_CLEAR_CM
            and right >= CURVE_EXIT_SIDE_CLEAR_CM
        )

        if exit_is_clear:
            curve_exit_clear_count += 1
        else:
            curve_exit_clear_count = 0

        if curve_exit_clear_count >= CURVE_EXIT_CONFIRMATIONS:
            navigation_phase = 'STRAIGHT'
            curve_exit_clear_count = 0

    # Safe/open path: do not continuously center between the walls.
    return 0.0, False


def straight_alignment_target(left, right):
    """Return a small direct steering angle that aligns the straight path."""
    if navigation_phase != 'STRAIGHT':
        return 0.0

    if left is None or right is None:
        return 0.0

    # Cheese's physical steering convention is negative=right and
    # positive=left. Therefore:
    #   left wall closer  -> negative angle -> move right
    #   right wall closer -> positive angle -> move left
    difference = left - right
    if abs(difference) <= STRAIGHT_ALIGNMENT_DEADBAND_CM:
        return 0.0

    return clamp(
        difference * STRAIGHT_ALIGNMENT_GAIN,
        -STRAIGHT_ALIGNMENT_MAX_ANGLE,
        STRAIGHT_ALIGNMENT_MAX_ANGLE
    )


def drive_sensor_fusion_pid(left, right, front):
    """Combine minimum-correction PID with smooth camera pillar avoidance."""
    global integral, last_error, filtered_derivative

    parking_mode = completed_curves >= TOTAL_CURVES
    error, correction_needed = required_pid_error(left, right, front)

    # The rules only require obeying pillars during the three official laps.
    # Once parking begins, camera influence is suppressed and smoothly cleared.
    if parking_mode:
        pillar_color, pillar_x, pillar_width = None, 0, 0
    else:
        pillar_color, pillar_x, pillar_width = read_pillar(time())

    camera_bias, camera_speed = update_pillar_control(
        pillar_color, pillar_x, pillar_width, left, right
    )

    # A side already inside the existing 24 cm correction threshold has safety
    # priority. Camera steering is still useful while it agrees with the escape;
    # only a camera request in the opposite direction will be vetoed below.
    close_wall_active = (
        (left is not None and left <= CORRECTION_WALL_DISTANCE_CM)
        or (right is not None and right <= CORRECTION_WALL_DISTANCE_CM)
    )

    if parking_mode:
        applied_camera_bias = 0.0
    else:
        applied_camera_bias = camera_bias

    if not correction_needed:
        reset_pid()
        drive_speed = max(NORMAL_SPEED, camera_speed)

        if parking_mode:
            drive_speed = max(drive_speed, PARKING_SPEED)

        drive.on(SpeedPercent(drive_speed))

        # A fresh or fading camera command has priority over alignment. During
        # CURVE_EXIT, center the wheels immediately so the car stops carrying
        # corner steering into the next straight.
        if pillar_just_lost:
            set_steering(0.0, immediate=True)
        elif abs(applied_camera_bias) >= 1.0:
            set_steering(applied_camera_bias)
        elif navigation_phase == 'CURVE_EXIT':
            set_steering(0.0, immediate=True)
        else:
            set_steering(straight_alignment_target(left, right))
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
    pid_steering_angle = -correction

    if close_wall_active:
        # Wall escape is non-negotiable. Never add camera steering while either
        # side is already inside the emergency correction distance.
        applied_camera_bias = 0.0

    steering_angle = clamp(
        pid_steering_angle + applied_camera_bias,
        -(MAX_PID_ANGLE + PILLAR_BIAS_ANGLE),
        MAX_PID_ANGLE + PILLAR_BIAS_ANGLE
    )

    drive_speed = max(CORRECTION_SPEED, camera_speed)

    if parking_mode:
        drive_speed = max(drive_speed, PARKING_SPEED)

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
    threading.Thread(target=husky_reader_thread, daemon=True).start()

    wait_for_start_button()

    if not memorize_starting_distances():
        stop_robot()
        show_message('SENSOR ERROR', x=20, font='luBS14')
        raise RuntimeError('Could not memorize starting distances')

    drive.position = 0
    reset_pid()
    show_curve_count()

    print('RUN STARTED')
    print('Curve rule: fresh opposite-color entries within 3s')

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

        parking_mode = completed_curves >= TOTAL_CURVES

        if finish_position_reached(left, right, current_front):
            stop_robot()
            break

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
 
 
