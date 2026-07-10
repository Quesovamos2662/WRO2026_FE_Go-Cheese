#!/usr/bin/env python3
# WRO Future Engineers - Open Challenge
# Python 3.5.3 compatible - ev3dev2
# New version based on successful test11.py / test14.py structure.
# Main idea:
#   - PID/PD does most of the normal side-wall centering.
#   - Wall guard corrects strongly before the robot reaches emergency distance.
#   - Steering-speed tuning: faster while PID/corner/guard steering, emergency still slow.
#   - Emergency steering is the last line of defense, but it triggers earlier than before.
#   - Front wall / corner logic overrides PID.
#   - Small sensor delay is kept so ultrasonic sensors do not freeze.
#   - No print() inside navigate(), to avoid MicroSD latency.

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor
from ev3dev2.button import Button
from time import sleep, time

# =========================
# HARDWARE SETUP
# =========================

drive    = LargeMotor(OUTPUT_B)
steering = MediumMotor(OUTPUT_A)

btn = Button()

# Sensors:
# INPUT_1 = left ultrasonic
# INPUT_2 = front ultrasonic
# INPUT_3 = right ultrasonic
us_left  = UltrasonicSensor(INPUT_1)
us_front = UltrasonicSensor(INPUT_2)
us_right = UltrasonicSensor(INPUT_3)

# =========================
# STARTUP / SENSOR WARMUP
# =========================

sleep(1.0)

for _i in range(3):
    try:
        us_left.distance_centimeters
        us_front.distance_centimeters
        us_right.distance_centimeters
    except Exception:
        pass
    sleep(0.05)

for _s in (us_left, us_front, us_right):
    try:
        _s.mode = 'US-DIST-CM'
    except Exception:
        pass

sleep(0.2)
steering.reset()
sleep(0.2)

# =========================
# SPEED SETTINGS
# =========================
# More negative = faster forward on your robot.
# Faster-steering version. Sensor delay is unchanged; emergency stays slow.

SPEED_FAST          = 200
SPEED_PID           = -100
SPEED_PID_CAUTION   = -88
SPEED_WALL_GUARD    = -74
SPEED_CORNER_GENTLE = -98
SPEED_CORNER_MEDIUM = -88
SPEED_CORNER_STRONG = -76
SPEED_DANGER        = -38
SPEED_POST_CORNER   = -80

STEER_DIRECTION_FIX = 1
DEFAULT_TURN        = "LEFT"

# =========================
# STEERING ANGLES
# =========================

ANGLE_CENTER = 0
ANGLE_GENTLE = 25
ANGLE_MEDIUM = 45
ANGLE_STRONG = 70
ANGLE_DANGER = 90

STEER_MOTOR_SPEED = 100

# =========================
# DISTANCE SETTINGS
# =========================
# These are intentionally a little earlier than the original successful tests.
# PID handles smooth centering, but close walls and corners still need hard logic.

HIT_RISK_CM = 18

# Emergency is still the last line of defense, but it starts earlier
# than the previous 35cm value so the robot has time to turn away.
SIDE_EMERGENCY_CM  = 48
FRONT_EMERGENCY_CM = 58

# Wall guard is NOT emergency. It is a strong normal correction layer
# that should handle most wall approaches before emergency is needed.
WALL_GUARD_CM        = 88
WALL_GUARD_STRONG_CM = 96

SIDE_GENTLE_CM = 14
SIDE_MEDIUM_CM = 108
SIDE_STRONG_CM = 76

FRONT_GENTLE_CM = 235
FRONT_MEDIUM_CM = 178
FRONT_STRONG_CM = 128

SIDE_DEADBAND = 8

# If a side sensor reads very far, it may be missing the wall due to angle.
BLIND_SIDE_THRESHOLD = 180

# =========================
# SENSOR SETTINGS
# =========================
# DO NOT set this to 0.
# Ultrasonic sensors can freeze / repeat bad values if read too fast.
# 0.015 was stable in your successful tests.

SENSOR_GAP_MS = 0.010

# Early warning prediction:
# If a sensor value drops fast between loops, use a slightly smaller
# distance for decisions. This keeps the sensor delay stable but makes
# reactions happen sooner.
SENSOR_DROP_MEDIUM_CM = 7.0
SENSOR_DROP_FAST_CM   = 14.0
ANTICIPATE_MEDIUM_CM  = 6.0
ANTICIPATE_FAST_CM    = 14.0

_last_l = 250.0
_last_f = 250.0
_last_r = 250.0

# =========================
# PID SETTINGS
# =========================
# This is technically PID, but KI starts at 0.00 because ultrasonic sensors are noisy.
# Start with PD. Only increase KI later if the robot keeps drifting to one side.
# If it zigzags: lower KP or KD.
# If it reacts too weakly: raise KP a little.

PID_KP = 0.56
PID_KI = 0.00
PID_KD = 1.22

PID_MAX_ANGLE       = 70
PID_DEADBAND_CM     = 4
PID_INTEGRAL_LIMIT  = 120
PID_VALID_MAX_CM    = 175
PID_VALID_MIN_CM    = 20

pid_last_error = 0.0
pid_integral   = 0.0

# =========================
# LOOP / DEBUG SETTINGS
# =========================

LOOP_DELAY = 0.000
DEBUG_PRINT = False
PRINT_INTERVAL = 0.30

# Stop automatically after 1 minute 54 seconds.
# Timer starts after warmup, when the robot begins driving.
RUN_TIME_LIMIT_SECONDS = 99.0

# =========================
# LAP / CORNER TRACKING
# =========================

TOTAL_LAPS        = 3
CORNERS_PER_LAP   = 4
CORNER_ENTRY_DIST = 135
CORNER_EXIT_DIST  = 170
CORNER_COOLDOWN   = 0.55

corners_counted   = 0
laps_completed    = 0
in_corner         = False
last_corner_time  = 0.0
lap_split_time    = 0.0

last_steer_target = 999
last_drive_speed  = 999
last_print_time   = 0.0

post_corner_until  = 0.0
POST_CORNER_CENTER = 0.65
POST_CORNER_SENSOR_CAP = 75

# =========================
# SMALL HELPERS
# =========================

def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def reset_pid():
    global pid_last_error, pid_integral
    pid_last_error = 0.0
    pid_integral = 0.0

# =========================
# SENSOR FUNCTIONS
# =========================

def _read_one(sensor, last_val):
    try:
        v = sensor.distance_centimeters

        if v is None:
            return last_val

        if v <= 0:
            return HIT_RISK_CM

        if v > 250:
            return last_val

        return float(v)

    except Exception:
        return last_val


def _anticipate_distance(current, previous):
    # If distance suddenly gets smaller, the robot is approaching a wall.
    # Return a slightly smaller value so wall guard / emergency reacts sooner.
    drop = previous - current

    if drop >= SENSOR_DROP_FAST_CM:
        return max(HIT_RISK_CM, current - ANTICIPATE_FAST_CM)

    if drop >= SENSOR_DROP_MEDIUM_CM:
        return max(HIT_RISK_CM, current - ANTICIPATE_MEDIUM_CM)

    return current


def read_all_fast():
    global _last_l, _last_f, _last_r

    prev_l = _last_l
    prev_f = _last_f
    prev_r = _last_r

    raw_l = _read_one(us_left, _last_l)
    sleep(SENSOR_GAP_MS)

    raw_f = _read_one(us_front, _last_f)
    sleep(SENSOR_GAP_MS)

    raw_r = _read_one(us_right, _last_r)
    sleep(SENSOR_GAP_MS)

    _last_l = raw_l
    _last_f = raw_f
    _last_r = raw_r

    left  = _anticipate_distance(raw_l, prev_l)
    front = _anticipate_distance(raw_f, prev_f)
    right = _anticipate_distance(raw_r, prev_r)

    return left, front, right


def open_side(left, right):
    # Choose the side with more space.
    if left - right > SIDE_DEADBAND:
        return "LEFT"

    if right - left > SIDE_DEADBAND:
        return "RIGHT"

    return DEFAULT_TURN

# =========================
# MOVEMENT FUNCTIONS
# =========================

def set_drive(speed):
    global last_drive_speed

    if abs(speed - last_drive_speed) >= 2:
        drive.on(SpeedPercent(speed))
        last_drive_speed = speed


def set_steering_signed(target):
    # Positive target = LEFT, negative target = RIGHT.
    global last_steer_target

    target = int(clamp(target, -ANGLE_DANGER, ANGLE_DANGER))

    if abs(target - last_steer_target) >= 3:
        steering.on_to_position(
            SpeedPercent(STEER_MOTOR_SPEED),
            target,
            brake=True,
            block=False
        )
        last_steer_target = target


def set_steering(direction, angle):
    if direction == "CENTER":
        target = ANGLE_CENTER

    elif direction == "LEFT":
        target = angle * STEER_DIRECTION_FIX

    else:
        target = -angle * STEER_DIRECTION_FIX

    set_steering_signed(target)


def drive_and_steer(drive_speed, direction, angle):
    set_drive(drive_speed)
    set_steering(direction, angle)


def drive_and_steer_signed(drive_speed, signed_angle):
    set_drive(drive_speed)
    set_steering_signed(signed_angle)


def stop():
    drive.off()
    steering.off()

# =========================
# PID SIDE CENTERING
# =========================

def pid_center(left, right, speed):
    global pid_last_error, pid_integral

    # error > 0 means left wall is closer, so steer RIGHT.
    # error < 0 means right wall is closer, so steer LEFT.
    error = right - left

    if abs(error) <= PID_DEADBAND_CM:
        error = 0.0

    pid_integral += error
    pid_integral = clamp(pid_integral, -PID_INTEGRAL_LIMIT, PID_INTEGRAL_LIMIT)

    derivative = error - pid_last_error
    pid_last_error = error

    correction = (PID_KP * error) + (PID_KI * pid_integral) + (PID_KD * derivative)

    # Convert correction to steering angle.
    # correction positive = left wall closer = steer right = negative angle.
    signed_angle = -correction
    signed_angle = clamp(signed_angle, -PID_MAX_ANGLE, PID_MAX_ANGLE)

    drive_and_steer_signed(speed, signed_angle)


def pid_side_valid(value):
    return value >= PID_VALID_MIN_CM and value <= PID_VALID_MAX_CM

# =========================
# CORNER TRACKING
# =========================

def check_corner(front_dist):
    global corners_counted, laps_completed, in_corner
    global last_corner_time, lap_split_time, post_corner_until

    now = time()

    if not in_corner and front_dist < CORNER_ENTRY_DIST:
        in_corner = True

    elif in_corner and front_dist > CORNER_EXIT_DIST:
        in_corner = False

        if (now - last_corner_time) >= CORNER_COOLDOWN:
            corners_counted += 1
            last_corner_time = now
            post_corner_until = now + POST_CORNER_CENTER
            reset_pid()

            new_laps = corners_counted // CORNERS_PER_LAP

            if new_laps > laps_completed:
                laps_completed = new_laps
                lap_time = now - lap_split_time
                lap_split_time = now

                print("=" * 40)
                print("LAP {} DONE | split: {:.1f}s".format(laps_completed, lap_time))
                print("=" * 40)

            else:
                laps_completed = new_laps
                print("[CORNER] {} of {} | lap {}".format(
                    corners_counted % CORNERS_PER_LAP or CORNERS_PER_LAP,
                    CORNERS_PER_LAP,
                    laps_completed + 1
                ))

# =========================
# NAVIGATION LOGIC
# =========================

def wall_guard(left, right):
    # Strong normal steering before emergency distance.
    # This should do most of the work when a side wall gets close.
    # Returns True if it took control.

    left_close = left <= WALL_GUARD_CM
    right_close = right <= WALL_GUARD_CM

    if not left_close and not right_close:
        return False

    reset_pid()

    # If both sides are close, steer toward the side with more space.
    if left_close and right_close:
        if left <= WALL_GUARD_STRONG_CM or right <= WALL_GUARD_STRONG_CM:
            drive_and_steer(SPEED_WALL_GUARD, open_side(left, right), ANGLE_DANGER)
        else:
            drive_and_steer(SPEED_PID_CAUTION, open_side(left, right), ANGLE_STRONG)
        return True

    if left <= WALL_GUARD_STRONG_CM:
        drive_and_steer(SPEED_WALL_GUARD, "RIGHT", ANGLE_DANGER)
        return True

    if right <= WALL_GUARD_STRONG_CM:
        drive_and_steer(SPEED_WALL_GUARD, "LEFT", ANGLE_DANGER)
        return True

    if left_close:
        drive_and_steer(SPEED_PID_CAUTION, "RIGHT", ANGLE_STRONG)
        return True

    if right_close:
        drive_and_steer(SPEED_PID_CAUTION, "LEFT", ANGLE_STRONG)
        return True

    return False


def navigate(left, front, right):

    # =========================
    # 1) ABSOLUTE HIT RISK
    # =========================
    # This is the panic layer. It uses max steering and very low speed.

    if front <= HIT_RISK_CM or left <= HIT_RISK_CM or right <= HIT_RISK_CM:
        reset_pid()

        if front <= HIT_RISK_CM:
            drive_and_steer(SPEED_DANGER, open_side(left, right), ANGLE_DANGER)
            return

        if left <= HIT_RISK_CM and right <= HIT_RISK_CM:
            drive_and_steer(SPEED_DANGER, open_side(left, right), ANGLE_DANGER)
            return

        if left <= HIT_RISK_CM:
            drive_and_steer(SPEED_DANGER, "RIGHT", ANGLE_DANGER)
            return

        drive_and_steer(SPEED_DANGER, "LEFT", ANGLE_DANGER)
        return

    # =========================
    # 2) EMERGENCY WALL AVOIDANCE
    # =========================
    # Last line of defense before a bump.
    # It starts earlier than before, but wall_guard should usually prevent
    # the robot from ever needing this layer.

    if (front <= FRONT_EMERGENCY_CM or
        left  <= SIDE_EMERGENCY_CM or
        right <= SIDE_EMERGENCY_CM):

        reset_pid()

        if front <= FRONT_EMERGENCY_CM:
            drive_and_steer(SPEED_DANGER, open_side(left, right), ANGLE_DANGER)
            return

        if left <= SIDE_EMERGENCY_CM and right <= SIDE_EMERGENCY_CM:
            drive_and_steer(SPEED_DANGER, open_side(left, right), ANGLE_DANGER)
            return

        if left <= SIDE_EMERGENCY_CM:
            drive_and_steer(SPEED_DANGER, "RIGHT", ANGLE_DANGER)
            return

        drive_and_steer(SPEED_DANGER, "LEFT", ANGLE_DANGER)
        return

    # =========================
    # 3) POST-CORNER CENTERING
    # =========================
    # After a corner, side sensors can miss the new wall and read 250.
    # We cap big readings so the robot does not think the wall disappeared.

    if time() < post_corner_until:
        l_capped = min(left, POST_CORNER_SENSOR_CAP)
        r_capped = min(right, POST_CORNER_SENSOR_CAP)

        if wall_guard(l_capped, r_capped):
            return

        pid_center(l_capped, r_capped, SPEED_POST_CORNER)
        return

    # =========================
    # 4) FRONT WALL / CORNER LOGIC
    # =========================
    # PID does NOT control corners. The front sensor decides the turn.

    if front <= FRONT_STRONG_CM:
        reset_pid()
        drive_and_steer(SPEED_CORNER_STRONG, open_side(left, right), ANGLE_STRONG)
        return

    if front <= FRONT_MEDIUM_CM:
        reset_pid()
        drive_and_steer(SPEED_CORNER_MEDIUM, open_side(left, right), ANGLE_MEDIUM)
        return

    if front <= FRONT_GENTLE_CM:
        reset_pid()
        drive_and_steer(SPEED_CORNER_GENTLE, open_side(left, right), ANGLE_GENTLE)
        return

    # =========================
    # 5) BLIND SIDE DETECTION ON STRAIGHTS
    # =========================
    # If one ultrasonic beam misses a wall while the other side is close,
    # steer away from the close side.

    if front > FRONT_GENTLE_CM:
        left_blind = left > BLIND_SIDE_THRESHOLD
        right_blind = right > BLIND_SIDE_THRESHOLD

        if left_blind and right <= SIDE_GENTLE_CM:
            reset_pid()
            drive_and_steer(SPEED_PID_CAUTION, "LEFT", ANGLE_MEDIUM)
            return

        if right_blind and left <= SIDE_GENTLE_CM:
            reset_pid()
            drive_and_steer(SPEED_PID_CAUTION, "RIGHT", ANGLE_MEDIUM)
            return

    # =========================
    # 6) WALL GUARD
    # =========================
    # This is the strong normal correction layer.
    # It should do most of the wall avoidance before emergency is needed.

    if wall_guard(left, right):
        return

    # =========================
    # 7) PID SIDE-WALL CENTERING
    # =========================
    # Smooth normal driving. It continuously corrects instead of waiting
    # for gentle / medium / strong thresholds.

    left_valid = pid_side_valid(left)
    right_valid = pid_side_valid(right)

    if left_valid and right_valid:
        if left <= SIDE_MEDIUM_CM or right <= SIDE_MEDIUM_CM:
            pid_center(left, right, SPEED_PID_CAUTION)
        else:
            pid_center(left, right, SPEED_PID)
        return

    # =========================
    # 8) SINGLE-SIDE FALLBACK
    # =========================
    # If only one side is readable, use conservative wall avoidance.

    reset_pid()

    if left_valid and not right_valid:
        if left <= SIDE_STRONG_CM:
            drive_and_steer(SPEED_PID_CAUTION, "RIGHT", ANGLE_STRONG)
            return
        if left <= SIDE_MEDIUM_CM:
            drive_and_steer(SPEED_PID_CAUTION, "RIGHT", ANGLE_MEDIUM)
            return
        if left <= SIDE_GENTLE_CM:
            drive_and_steer(SPEED_PID, "RIGHT", ANGLE_GENTLE)
            return

    if right_valid and not left_valid:
        if right <= SIDE_STRONG_CM:
            drive_and_steer(SPEED_PID_CAUTION, "LEFT", ANGLE_STRONG)
            return
        if right <= SIDE_MEDIUM_CM:
            drive_and_steer(SPEED_PID_CAUTION, "LEFT", ANGLE_MEDIUM)
            return
        if right <= SIDE_GENTLE_CM:
            drive_and_steer(SPEED_PID, "LEFT", ANGLE_GENTLE)
            return

    # =========================
    # 9) SAFE / NO CLEAR SIDE READING
    # =========================

    drive_and_steer(SPEED_FAST, "CENTER", ANGLE_CENTER)

# =========================
# WARMUP
# =========================

def warmup():
    print("Warming up sensors...")

    for i in range(15):
        read_all_fast()
        print("  {}/15".format(i + 1), end="\r")

    left, front, right = read_all_fast()

    print("\nSensors ready | L:{:.1f} F:{:.1f} R:{:.1f}".format(
        left, front, right
    ))

    # Only block on front sensor. Side sensors being close is normal
    # when the robot starts inside a WRO corridor.
    while front <= HIT_RISK_CM:
        print("Front too close to wall. Move robot away.")
        print("L:{:.1f} F:{:.1f} R:{:.1f}".format(left, front, right))
        stop()
        sleep(0.3)
        left, front, right = read_all_fast()

# =========================
# MAIN
# =========================

warmup()

print("=" * 40)
print("PID + corner + guard emergency STEER-FASTER started")
print("Speeds FAST/PID/CAUTION/GUARD/CORNER G-M-S/DANGER: {}/{}/{}/{}/{}/{}/{}/{}".format(
    SPEED_FAST,
    SPEED_PID,
    SPEED_PID_CAUTION,
    SPEED_WALL_GUARD,
    SPEED_CORNER_GENTLE,
    SPEED_CORNER_MEDIUM,
    SPEED_CORNER_STRONG,
    SPEED_DANGER
))
print("PID KP/KI/KD: {}/{}/{} | max angle:{}".format(
    PID_KP, PID_KI, PID_KD, PID_MAX_ANGLE
))
print("Front G/M/S: {}/{}/{} cm".format(
    FRONT_GENTLE_CM, FRONT_MEDIUM_CM, FRONT_STRONG_CM
))
print("Side G/M/S: {}/{}/{} cm".format(
    SIDE_GENTLE_CM, SIDE_MEDIUM_CM, SIDE_STRONG_CM
))
print("Wall guard:{}cm strong:{}cm".format(
    WALL_GUARD_CM, WALL_GUARD_STRONG_CM
))
print("Emergency side/front:{}/{}cm Hit risk:{}cm Sensor gap:{}s".format(
    SIDE_EMERGENCY_CM, FRONT_EMERGENCY_CM, HIT_RISK_CM, SENSOR_GAP_MS
))
print("Press BACK to stop.")
print("=" * 40)

run_start = time()
lap_split_time = run_start
last_print_time = run_start

drive_and_steer(SPEED_FAST, "CENTER", ANGLE_CENTER)

try:
    while True:

        if time() - run_start >= RUN_TIME_LIMIT_SECONDS:
            print("Time limit reached - stopping.")
            break

        if btn.backspace:
            print("Back button pressed - stopping.")
            break

        left, front, right = read_all_fast()

        check_corner(front)
        navigate(left, front, right)

        if DEBUG_PRINT:
            now = time()

            if now - last_print_time >= PRINT_INTERVAL:
                print("L:{:.0f} F:{:.0f} R:{:.0f} | c:{} laps:{} | pid_e:{:.1f}".format(
                    left, front, right, corners_counted, laps_completed, pid_last_error
                ))
                last_print_time = now

        if LOOP_DELAY > 0:
            sleep(LOOP_DELAY)

except KeyboardInterrupt:
    print("Keyboard interrupt")

finally:
    stop()
    total_time = time() - run_start

    print("Stopped | corners:{} laps:{} time:{:.1f}s".format(
        corners_counted, laps_completed, total_time
    ))


