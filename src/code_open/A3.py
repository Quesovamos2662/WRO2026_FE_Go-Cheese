#!/usr/bin/env python3
# WRO Future Engineers - Open Challenge
# Python 3.5.3 compatible - ev3dev2
# New version based on locking8_pid065_value_faster (9).py.
# POST-SECOND-COLOR SHARP-TURN VERSION:
#   - The first color disables ultrasonic corrections and PID.
#   - The opposite/second color starts a short sharp turn in the SAME direction
#     and with the SAME angle/speed used during the main color curve.
#   - Ultrasonic corrections and PID remain blocked during that sharp-turn pulse.
#   - As soon as the pulse ends, ultrasonic control and PID resume immediately.
# ULTRASONIC-LOCKOUT CURVE VERSION:
#   - From the instant the FIRST color is detected until the SECOND/opposite
#     color is detected, ultrasonic readings and PID are completely ignored.
#   - During that interval, only the color-selected fixed curve command controls
#     steering: BLUE first = LEFT, ORANGE first = RIGHT.
#   - The second/opposite color ends curve mode immediately. On that same loop,
#     the ultrasonic sensors and PID resume with no 0.30 s exit hold.
#   - Side emergency, wall guard, and every other ultrasonic correction are
#     intentionally blocked while curve_mode is active.
# NEW COLOR-DIRECTION VERSION:
#   - BLUE first always starts a subtle LEFT steer.
#   - ORANGE first always starts a subtle RIGHT steer.
#   - The opposite color starts a 0.50 s exit-hold; the robot keeps the SAME
#     subtle steer during that half-second, then hands control to PID.
#   - Automatic open-side curve direction and adaptive curve angles were removed
#     because they could contradict the required color-direction behavior.
#   - Side hit-risk and emergency protection remain able to override the curve
#     only when a real collision risk is detected.
# Main change in this version:
#   - Curve angle and speed now adapt to the robot's lateral position when the
#     first color is detected. A centered or badly placed start uses a tighter,
#     slower curve; a favorable start near the outside uses the normal curve.
#   - Added a post-color exit-alignment arc. After the second color, the robot
#     keeps a short, slower turn in the same curve direction before lateral PID.
#   - If both side sensors temporarily see open space, the robot no longer
#     centers its steering; it continues a small controlled arc until a wall is
#     visible again. This targets wide third-curve exits toward the outer wall.
#   - Post-curve validation now requires 2 strict safe readings.
#   - Normal PID is blocked while the exterior wall is still approaching.
#   - A limited post-curve PID is used before normal full-speed PID resumes.
#   - PID steering is more filtered, changes direction more slowly, and ignores
#     slightly larger sensor differences to reduce left-right zigzag.
# DIRECT PID HANDOFF VERSION:
#   - After the second color, steering goes to CENTER.
#   - No fixed post-curve angle or alignment arc is commanded.
#   - The robot waits for both lateral sensors to be valid, then PID takes over directly.
#   - Emergency side-wall protection remains active as the final safety layer.
#
# NEW MODERATE-PID VERSION:
#   - Keeps the INPUT_2 color detection and curve start/end logic unchanged.
#   - Replaces aggressive straight corrections with a moderate, filtered PID.
#   - Very distant side readings are capped/ignored so they cannot dominate steering.
#   - After each color curve, the nearest trustworthy wall gets priority.
#   - Normal PID resumes only after both side readings are reasonable and stable.
#   - Front ultrasonic sensor on INPUT_2 was replaced by the EV3 color sensor.
#   - INPUT_2 now runs in RGB-RAW mode so the sensor built-in light is on.
#   - Curves are detected by the first blue/orange line, and ended by the
#     opposite color line. The photo RGB bases are BLUE=(36,74,165) and
#     ORANGE=(245,113,20).
#   - Normal straight driving has been simplified. The old file had too many
#     correction layers fighting each other: PID + wall guard + blind side +
#     post-corner + front fix + emergency. That made the robot keep correcting
#     even when it was already close to centered.
#   - Corner handling is kept almost intact: check_corner(), FRONT_GENTLE /
#     FRONT_MEDIUM / FRONT_STRONG, lap count, finish timing, and parking logic
#     were not redesigned.
#   - On safe straights, PID now gets priority before wall guard.
#   - Wall guard is now only for real close-wall risk, not normal centering.
#   - Blind-side correction is only allowed when the readable side is also
#     actually close. It no longer steals control on normal straights.
#   - Front-fix is no longer the first layer in navigate(); the normal front
#     corner logic handles front distance first.
#   - PID is softer and more persistent, so it ignores tiny 2-3 cm differences
#     instead of changing direction constantly.
#   - Post-corner recovery is reinforced again because the softer version
#     could cut into the wall right after the first corner.
#   - The robot still has reduced correction layers on straight sections, but
#     corner exit now has one clear guard instead of many competing fixes.
#   - No print() inside navigate(), to avoid MicroSD latency.

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import UltrasonicSensor, ColorSensor
from ev3dev2.button import Button
from ev3dev2.power import PowerSupply
from time import sleep, time

# =========================
# HARDWARE SETUP
# =========================

drive    = LargeMotor(OUTPUT_B)
steering = MediumMotor(OUTPUT_A)

btn = Button()
battery = PowerSupply()

# Tiny log: one entry per completed corner (12 entries for a 3-lap run).
# Lets us check whether battery voltage sags noticeably by the time we
# reach the corners near the end of lap 3, which is when crashes have been
# happening. Printed once at the very end, after the robot has stopped.
CORNER_VOLTAGE_LOG = []

# Sensors:
# INPUT_1 = left ultrasonic
# INPUT_2 = front color sensor
# INPUT_3 = right ultrasonic
us_left     = UltrasonicSensor(INPUT_1)
color_front = ColorSensor(INPUT_2)
us_right    = UltrasonicSensor(INPUT_3)

# =========================
# STARTUP / SENSOR WARMUP
# =========================

sleep(1.0)

for _i in range(3):
    try:
        us_left.distance_centimeters
        color_front.rgb
        us_right.distance_centimeters
    except Exception:
        pass
    sleep(0.05)

for _s in (us_left, us_right):
    try:
        _s.mode = 'US-DIST-CM'
    except Exception:
        pass

# RGB-RAW uses the EV3 color sensor reflected-light RGB mode, which keeps
# the sensor built-in illumination active for more stable color readings.
try:
    color_front.mode = 'RGB-RAW'
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

SPEED_FAST          = -100
SPEED_PID           = -100
SPEED_PID_CAUTION   = -100  # faster caution speed; PID gains untouched
SPEED_WALL_GUARD    = -93   # faster wall-guard speed; corner speeds untouched
SPEED_CORNER_GENTLE = -100
SPEED_CORNER_MEDIUM = -96
SPEED_CORNER_STRONG = -84
SPEED_DANGER        = -50   # faster emergency; still much slower than normal driving
SPEED_POST_CORNER   = -82   # slower right after corners so steering has time to bite
SPEED_POST_CORNER_CLOSE = -62  # slower only when the inner wall is close after a corner
                                # this protects the first corner exit from cutting into the wall

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

# Anti-wobble: avoid sending tiny steering-position updates every loop.
# Large commands, including corner commands, still update normally.
STEER_COMMAND_MIN_CHANGE = 3

# =========================
# DISTANCE SETTINGS
# =========================
# These are intentionally a little earlier than the original successful tests.
# PID handles smooth centering, but close walls and corners still need hard logic.

HIT_RISK_CM = 18

# Emergency is still the last line of defense, but it starts earlier
# than the previous 35cm value so the robot has time to turn away.
SIDE_EMERGENCY_CM  = 38
FRONT_EMERGENCY_CM = 58

# Wall guard is NOT emergency. It is a strong normal correction layer
# that should handle most wall approaches before emergency is needed.
WALL_GUARD_CM        = 68   # was 82. Wall guard now waits for real close-wall risk.
WALL_GUARD_STRONG_CM = 50   # still above emergency, but no longer active all the time.
WALL_GUARD_CLOSE_ANGLE  = 16
WALL_GUARD_STRONG_ANGLE = 30

# Softer one-side fallback angles. These prevent the robot from starting
# near a side wall, overcorrecting, and immediately crossing into the
# opposite wall.
SINGLE_SIDE_GENTLE_ANGLE = 16
SINGLE_SIDE_MEDIUM_ANGLE = 28
SINGLE_SIDE_STRONG_ANGLE = 42

SIDE_GENTLE_CM = 138
SIDE_MEDIUM_CM = 100
SIDE_STRONG_CM = 68

FRONT_GENTLE_CM = 235
FRONT_MEDIUM_CM = 178
FRONT_STRONG_CM = 128

SIDE_DEADBAND = 8

# If a side sensor reads very far, it may be missing the wall due to angle.
BLIND_SIDE_THRESHOLD = 205

# =========================
# FRONT COLOR SENSOR / CURVE LINE SETTINGS
# =========================
# The front ultrasonic was replaced with the EV3 color sensor on INPUT_2.
# The RGB values below come from the track photo. Keep them as the starting
# values, then tune COLOR_THRESHOLD if the real sensor readings vary with
# lighting or sensor height.
COLOR_SENSOR_MODE = 'RGB-RAW'
AZUL_RGB          = (36, 74, 165)
NARANJA_RGB       = (245, 113, 20)
COLOR_THRESHOLD   = 45.0

# Prevents the same colored line from being read multiple times while the
# robot is still physically passing over it.
COLOR_EVENT_COOLDOWN = 0.55
COLOR_CURVE_MIN_TIME = 0.35

# Color-defined curve with a short exterior displacement before the main turn:
#   BLUE   -> briefly open RIGHT, then turn LEFT
#   ORANGE -> briefly open LEFT, then turn RIGHT
# The exterior movement is skipped when the outside wall is too close.
# After the opposite color, the main turn progressively tightens for 0.30 s,
# then PID takes control immediately.
CURVE_OUTWARD_ANGLE = 0
CURVE_OUTWARD_TIME = 0.0
CURVE_OUTWARD_MIN_SPACE_CM = 999
CURVE_OUTWARD_SPEED = -68

# The robot now turns inward immediately on the FIRST color.
# It no longer waits until the second color to become aggressive.
COLOR_CURVE_STEER_ANGLE = 48
COLOR_CURVE_PRE_EXIT_TIGHT_ANGLE = 60
COLOR_CURVE_PRE_EXIT_TIGHTEN_SECONDS = 0.18
COLOR_CURVE_EXIT_TIGHT_ANGLE = 68
COLOR_CURVE_SPEED       = -68

# After the opposite/second color, keep the exact same sharp curve command
# for this short time before ultrasonic sensors and PID resume.
POST_SECOND_COLOR_SHARP_TURN_SECONDS = 0.18
COLOR_CURVE_EXIT_HOLD_SECONDS = 0.30
# Reach the tighter angle quickly, then hold it for the rest of the 0.30 s.
# Previously, the angle only reached its tightest value at the exact moment PID
# took over, so the robot barely used the tighter angle in practice.
COLOR_CURVE_EXIT_TIGHTEN_SECONDS = 0.08

# PID starts from part of the final curve angle instead of snapping toward 0.
# This still hands control to PID after 0.30 s, but prevents a straight-line
# command immediately after the curve.
PID_HANDOFF_KEEP_RATIO = 0.85

# =========================
# SENSOR SETTINGS
# =========================
# DO NOT set this to 0.
# Ultrasonic sensors can freeze / repeat bad values if read too fast.
# 0.015 was stable in your successful tests.

SENSOR_GAP_MS = 0.015

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
# PID SETTINGS - MODERATE / PREVENTIVE
# =========================
# Both side sensors participate in normal steering. A distant reading is capped
# before calculating error, so a wall that is far away (or briefly missed) does
# not pull the robot violently across the lane.
PID_KP = 0.22
PID_KI = 0.002
PID_KD = 0.07

PID_MAX_ANGLE = 22

# Hysteresis avoids reacting to tiny left/right differences.
PID_DEADBAND_CM      = 6
PID_DEADBAND_EXIT_CM = 12

PID_INTEGRAL_LIMIT = 55
PID_VALID_MAX_CM   = 205
PID_VALID_MIN_CM   = 20

# Readings above this value are still considered "open space", but are capped
# for PID math. This is the key protection against random far-away readings.
PID_FAR_CAP_CM = 165

# Gentle preventive bias starts before the robot is actually in danger.
PID_PREVENTIVE_CM       = 105
PID_PREVENTIVE_MAX_BIAS = 7.0

# Stronger filtering, a wider dead zone, and a smaller per-loop step reduce zigzag at SPEED_PID.
PID_STEER_SMOOTHING = 0.87
PID_MAX_STEP        = 1.8
PID_CENTER_SNAP     = 3.5

pid_last_error     = 0.0
pid_integral       = 0.0
pid_filtered_angle = 0.0
pid_in_deadband    = True  # start assuming centered

# =========================
# LOOP / DEBUG SETTINGS
# =========================

LOOP_DELAY = 0.000
DEBUG_PRINT = False
PRINT_INTERVAL = 0.30

# Maximum safety time.
# This is NOT the parking trigger anymore.
# The robot now parks/stops after it counts 3 laps.
# Timer starts after warmup, when the robot begins driving.
RUN_TIME_LIMIT_SECONDS = 114.0

# =========================
# LAP / CORNER TRACKING
# =========================

TOTAL_LAPS        = 3
CORNERS_PER_LAP   = 4
TARGET_CORNERS    = TOTAL_LAPS * CORNERS_PER_LAP

# Corner counting is now the real finish/parking trigger.
# The timer above is only a maximum safety cutoff.
# The extra validation below helps avoid counting a moved middle square
# as if it were one of the 4 real track corners.
CORNER_ENTRY_DIST = 130
CORNER_EXIT_DIST  = 175

# False corner fix:
# The middle square can briefly look like a front wall.
# A real track corner should not happen immediately after the last real corner.
# If the robot starts missing real corners, lower this slowly to 2.4 or 2.2.
CORNER_COOLDOWN   = 3.0

# Do not allow the robot to stop from corner count too early.
# This is NOT the parking timer. It is only a sanity check against false counts.
# If your real 3-lap finish is faster than this, lower it.
MINIMUM_FINISH_TIME_SECONDS = 86.0

# The front sensor must see the corner for a tiny moment before we accept it.
# This filters quick false reads from the middle square or ultrasonic noise.
CORNER_ENTRY_HOLD_TIME = 0.14

# A valid corner should last long enough and include strong steering.
# This rejects quick obstacle/square avoidance that is not a 90-degree corner.
CORNER_MIN_INSIDE_TIME = 0.35
CORNER_MIN_STEER_ANGLE = 45
CORNER_REAL_FRONT_CM   = 112

# Extra drive time after the finish trigger.
# User requested 3.5 seconds so the robot can fully reach the parking zone.
PARKING_EXTRA_SECONDS = 3.5

corners_counted   = 0
laps_completed    = 0
in_corner         = False
last_corner_time  = 0.0
lap_split_time    = 0.0

corner_entry_candidate_time = 0.0
corner_enter_time = 0.0
corner_min_front = 250.0
corner_max_steer = 0

finish_requested = False
finish_request_time = 0.0

# =========================
# COLOR CURVE STATE
# =========================
# Straight mode: wait for first color.
# Curve mode: first color has started the curve; wait only for the opposite
# color to end it and count one completed curve/corner.
curve_mode = False
curve_first_color = None
curve_exit_color = None
curve_started_time = 0.0
curve_turn_direction = DEFAULT_TURN
curve_turn_angle = COLOR_CURVE_STEER_ANGLE
curve_drive_speed = COLOR_CURVE_SPEED
curve_entry_position = "COLOR_FIXED"
curve_exit_hold_until = 0.0
curve_exit_hold_start_time = 0.0
curve_exit_hold_started = False
curve_outward_active = False
curve_outward_until = 0.0

# Timed pulse after the second color. While active, ultrasonic corrections and
# PID are still locked out and the robot keeps the same curve direction/angle.
post_second_color_sharp_active = False
post_second_color_sharp_until = 0.0

last_color_event_time = -999.0
color_line_locked = False
last_color_rgb = (0, 0, 0)
last_color_seen = None

last_steer_target = 999
last_steer_sign    = 0     # tracks which way steering last actually moved:
                           # 1 = LEFT, -1 = RIGHT, 0 = no direction yet
last_drive_speed  = 999
last_print_time   = 0.0

# =========================
# STEERING BACKLASH COMPENSATION
# =========================
# Estimated mechanical backlash in the steering linkage: ~6-7 degrees of
# "dead" travel before the linkage engages and the wheel actually starts
# turning, whenever direction reverses. Not measured with a protractor yet -
# this is a starting estimate to tune on the track. If the robot still
# feels like it's slow to bite on direction changes, raise it a little
# (try 7-8). If it feels like it overshoots/twitches right when reversing,
# lower it (try 4-5).
STEER_BACKLASH_DEG = 5

post_corner_until = 0.0

# Conditional post-color-curve recovery. After the opposite color is detected,
# the robot first completes a short alignment arc in the SAME direction as the
# curve. This prevents the chassis from leaving the curve aimed at the exterior
# wall while both side sensors are temporarily looking into open space.
post_curve_recovery_active = False
post_curve_alignment_active = False
post_curve_alignment_until = 0.0
post_curve_stable_count = 0
post_curve_previous_outer = None

# After the second color, keep the wheels centered until both side sensors
# are valid. Then hand control directly to PID. No fixed post-curve steering
# angle, alignment arc, or wall-trend steering is allowed before PID.
post_curve_pid_handoff_pending = False
POST_CURVE_HANDOFF_SPEED = -72

POST_CORNER_CENTER = 2.20  # maximum fallback window; stable readings can end it earlier
POST_CORNER_RELEASE_TIME = 0.35
POST_CORNER_SOFT_STEER_LIMIT = 30

POST_CURVE_CLOSE_CM       = 92
POST_CURVE_VERY_CLOSE_CM  = 62
POST_CURVE_SAFE_MIN_CM    = 76
POST_CURVE_RELIABLE_MIN   = 55
POST_CURVE_REASONABLE_MAX = 175
POST_CURVE_FAR_IGNORE_CM  = 185
POST_CURVE_STABLE_DIFF_CM = 55
POST_CURVE_STABLE_SAMPLES = 2

# Exterior-wall trend protection. A decreasing exterior distance means the
# chassis is still aimed outward even if both ultrasonic readings look valid.
POST_CURVE_OUTER_SAFE_CM = 75
POST_CURVE_OUTER_DROP_CM = 2.0
POST_CURVE_OUTER_TREND_ANGLE = 17

# First stage immediately after the second color. It is deliberately short:
# finish rotating the chassis without extending the curve too far outward.
POST_CURVE_ALIGN_TIME = 0.22
POST_CURVE_ALIGN_SPEED = -70
POST_CURVE_ALIGN_ANGLE = 17
POST_CURVE_ALIGN_BLIND_ANGLE = 12
POST_CURVE_ALIGN_DANGER_CM = 58

POST_CURVE_GENTLE_ANGLE = 13
POST_CURVE_MEDIUM_ANGLE = 21
POST_CURVE_CLOSE_ANGLE  = 30
POST_CURVE_PID_MAX_ANGLE = 14
POST_CURVE_PID_MAX_STEP  = 1.5

# =========================
# COLOR-BASED CURVE TRACKING
# =========================

def register_completed_color_curve(elapsed_time):
    global corners_counted, laps_completed, last_corner_time, lap_split_time
    global post_corner_until, finish_requested, finish_request_time
    global post_curve_recovery_active, post_curve_alignment_active
    global post_curve_alignment_until, post_curve_stable_count
    global post_curve_previous_outer, post_curve_pid_handoff_pending
    global pid_filtered_angle, pid_last_error, pid_integral, pid_in_deadband

    now = time()

    corners_counted += 1
    last_corner_time = now
    # Direct PID handoff: once the second color is detected, do not command
    # any fixed steering angle. Center the wheels while waiting for two valid
    # side readings, then let PID choose the first correction itself.
    post_corner_until = 0.0
    post_curve_recovery_active = False
    post_curve_alignment_active = False
    post_curve_alignment_until = 0.0
    post_curve_stable_count = 0
    post_curve_previous_outer = None
    # PID is armed only after the post-second-color sharp pulse finishes.
    post_curve_pid_handoff_pending = False

    # Prepare a clean PID calculation for the instant the sharp pulse ends.
    pid_filtered_angle = 0.0
    pid_last_error = 0.0
    pid_integral = 0.0
    pid_in_deadband = True

    try:
        volts = round(battery.measured_volts, 2)
    except Exception:
        volts = -1.0
    CORNER_VOLTAGE_LOG.append((corners_counted, round(now - run_start, 1), volts))

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
        print("[COLOR CURVE] {} of {} | lap {}".format(
            corners_counted % CORNERS_PER_LAP or CORNERS_PER_LAP,
            CORNERS_PER_LAP,
            laps_completed + 1
        ))

    if corners_counted >= TARGET_CORNERS:
        if elapsed_time >= MINIMUM_FINISH_TIME_SECONDS:
            finish_requested = True
            finish_request_time = now
            print("Target reached: {} color curves / {} laps. Parking stop armed.".format(
                corners_counted, TOTAL_LAPS
            ))
        else:
            print("[EARLY TARGET IGNORED] {} color curves at {:.1f}s. Need at least {:.1f}s.".format(
                corners_counted, elapsed_time, MINIMUM_FINISH_TIME_SECONDS
            ))


def direction_for_first_color(color_name):
    # Required behavior: the first color alone defines the curve direction.
    if color_name == "AZUL":
        return "LEFT"

    if color_name == "NARANJA":
        return "RIGHT"

    return DEFAULT_TURN


def finish_color_curve(elapsed_time):
    global curve_mode, curve_first_color, curve_exit_color, curve_started_time
    global curve_exit_hold_until, curve_exit_hold_start_time, curve_exit_hold_started
    global curve_outward_active, curve_outward_until
    global post_second_color_sharp_active, post_second_color_sharp_until

    # The opposite color ends the waiting-for-color stage, but it does NOT
    # release PID yet. Keep the same direction, angle, and speed for one short
    # sharp-turn pulse so the chassis finishes rotating into the curve.
    curve_mode = False
    curve_first_color = None
    curve_exit_color = None
    curve_started_time = 0.0
    curve_exit_hold_until = 0.0
    curve_exit_hold_start_time = 0.0
    curve_exit_hold_started = False
    curve_outward_active = False
    curve_outward_until = 0.0

    post_second_color_sharp_active = True
    post_second_color_sharp_until = time() + POST_SECOND_COLOR_SHARP_TURN_SECONDS

    register_completed_color_curve(elapsed_time)

def check_color_curve(color_detected, left, right, elapsed_time):
    global curve_mode, curve_first_color, curve_exit_color, curve_started_time
    global curve_turn_direction, curve_turn_angle, curve_drive_speed
    global curve_entry_position, last_color_event_time, color_line_locked
    global curve_exit_hold_until, curve_exit_hold_start_time, curve_exit_hold_started
    global curve_outward_active, curve_outward_until
    global post_second_color_sharp_active

    now = time()

    # Unlock only after the sensor leaves the colored line. This prevents one
    # physical line from becoming multiple color events.
    if color_detected is None:
        color_line_locked = False
        return

    # Do not allow another color event to start a new curve while the timed
    # post-second-color sharp turn is still being completed.
    if post_second_color_sharp_active:
        return

    if color_line_locked:
        return

    if (now - last_color_event_time) < COLOR_EVENT_COOLDOWN:
        return

    color_line_locked = True
    last_color_event_time = now

    if not curve_mode:
        curve_mode = True
        curve_first_color = color_detected
        curve_exit_color = opposite_color(color_detected)
        curve_started_time = now

        # Direction comes ONLY from the first color. Ultrasonic values are not
        # consulted for direction, angle, speed, protection, or PID.
        curve_turn_direction = direction_for_first_color(color_detected)
        curve_turn_angle = COLOR_CURVE_STEER_ANGLE
        curve_drive_speed = COLOR_CURVE_SPEED
        curve_entry_position = "COLOR_ONLY_ULTRASONIC_LOCKOUT"

        curve_exit_hold_until = 0.0
        curve_exit_hold_start_time = 0.0
        curve_exit_hold_started = False
        curve_outward_active = False
        curve_outward_until = 0.0

        remember_corner_turn(curve_turn_direction)
        reset_pid()

        print("[CURVE START - ULTRASONIC OFF] first:{} waiting:{} turn:{} angle:{} speed:{} rgb:{}".format(
            curve_first_color, curve_exit_color, curve_turn_direction,
            curve_turn_angle, curve_drive_speed, last_color_rgb
        ))
        return

    # While curve mode is active, only the opposite color can release control.
    if color_detected != curve_exit_color:
        print("[COLOR IGNORED] saw:{} expected:{} rgb:{}".format(
            color_detected, curve_exit_color, last_color_rgb
        ))
        return

    if (now - curve_started_time) < COLOR_CURVE_MIN_TIME:
        print("[COLOR EXIT TOO EARLY] saw:{} time:{:.2f}s".format(
            color_detected, now - curve_started_time
        ))
        return

    print("[SECOND COLOR - SHARP TURN START] first:{} exit:{} time:{:.2f}s hold:{:.2f}s rgb:{}".format(
        curve_first_color, color_detected, now - curve_started_time,
        POST_SECOND_COLOR_SHARP_TURN_SECONDS, last_color_rgb
    ))

    # Start the timed sharp-turn pulse. PID and ultrasonic corrections remain
    # blocked until that pulse has fully finished.
    finish_color_curve(elapsed_time)


def color_curve_drive(left, right):
    # ULTRASONIC LOCKOUT:
    # From the first color until the opposite color, left/right values are
    # deliberately ignored. No PID, emergency avoidance, wall guard, or
    # sensor-based angle change is allowed to modify the curve.
    #
    # The function keeps left/right parameters only so the surrounding program
    # structure stays compatible with Python 3.5.3 and the existing calls.
    reset_pid()
    drive_and_steer(
        curve_drive_speed,
        curve_turn_direction,
        curve_turn_angle
    )
    return True


def post_second_color_sharp_drive():
    # Same exact direction, angle, and speed as the main color curve. No
    # ultrasonic correction or PID may interrupt this short completion pulse.
    reset_pid()
    drive_and_steer(
        curve_drive_speed,
        curve_turn_direction,
        curve_turn_angle
    )


# =========================
# STRAIGHT FRONT-SENSOR FIX
# =========================
# This is NOT corner logic. It only activates when the robot is already
# aimed into a wall during normal running. It uses the front sensor first,
# then left/right sensors and the current steering direction to choose the
# safest correction. Once active, it keeps correcting until the front
# distance is safe again, so the behavior can repeat during all 3 laps.

FRONT_FIX_ENTER_CM = 84
FRONT_FIX_EXIT_CM  = 138

FRONT_FIX_SIDE_CLOSE_CM  = 104
FRONT_FIX_SIDE_DANGER_CM = 74
FRONT_FIX_MIN_STEER_ANGLE = 20

FRONT_FIX_SPEED       = -85  # faster front-fix speed; no reverse, still controlled
FRONT_FIX_PANIC_CM    = 38
FRONT_FIX_ANGLE       = 40
FRONT_FIX_PANIC_ANGLE = ANGLE_STRONG

front_fix_active = False
front_fix_direction = DEFAULT_TURN

last_corner_turn_direction = DEFAULT_TURN
front_corner_active = False

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
    global pid_last_error, pid_integral, pid_filtered_angle
    pid_last_error = 0.0
    pid_integral = 0.0
    pid_filtered_angle = 0.0
    # NOTE: pid_in_deadband is intentionally NOT reset here. It reflects
    # whether the robot is actually near center right now, not whether some
    # other layer (wall_guard, corner logic, front fix...) briefly took
    # control. Resetting it to True every time PID hands off control made
    # it "forget" it was actively correcting and go quiet right when it got
    # control back near a wall - exactly when it needed to react fastest.

# =========================
# SENSOR FUNCTIONS
# =========================

def rgb_distance(rgb1, rgb2):
    return ((rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2) ** 0.5


def set_color_light_on():
    # Keep RGB-RAW active. On the EV3 color sensor this is the mode used for
    # reflected RGB readings with the built-in sensor light on.
    try:
        if color_front.mode != COLOR_SENSOR_MODE:
            color_front.mode = COLOR_SENSOR_MODE
    except Exception:
        try:
            color_front.mode = COLOR_SENSOR_MODE
        except Exception:
            pass


def _read_color_rgb():
    # Python 3.5.3 compatible: no f-strings, no type annotations.
    set_color_light_on()

    try:
        rgb = color_front.rgb
    except Exception:
        try:
            # Fallback for ev3dev2 versions where rgb is unavailable.
            rgb = color_front.raw
        except Exception:
            return None

    try:
        r = int(rgb[0])
        g = int(rgb[1])
        b = int(rgb[2])
    except Exception:
        return None

    # If a fallback returns raw values above 255, compress them roughly into
    # the same 0-255 scale as the photo RGB references.
    max_val = max(r, g, b)
    if max_val > 255:
        scale = 255.0 / float(max_val)
        r = int(r * scale)
        g = int(g * scale)
        b = int(b * scale)

    return (r, g, b)


def detect_track_color():
    global last_color_rgb, last_color_seen

    rgb = _read_color_rgb()

    if rgb is None:
        last_color_seen = None
        return None

    last_color_rgb = rgb

    dist_azul = rgb_distance(rgb, AZUL_RGB)
    dist_naranja = rgb_distance(rgb, NARANJA_RGB)

    if dist_azul <= COLOR_THRESHOLD and dist_azul < dist_naranja:
        last_color_seen = "AZUL"
        return "AZUL"

    if dist_naranja <= COLOR_THRESHOLD and dist_naranja < dist_azul:
        last_color_seen = "NARANJA"
        return "NARANJA"

    last_color_seen = None
    return None


def opposite_color(color_name):
    if color_name == "AZUL":
        return "NARANJA"

    if color_name == "NARANJA":
        return "AZUL"

    return None


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
    global _last_l, _last_r

    prev_l = _last_l
    prev_r = _last_r

    raw_l = _read_one(us_left, _last_l)
    sleep(SENSOR_GAP_MS)

    color_name = detect_track_color()
    sleep(SENSOR_GAP_MS)

    raw_r = _read_one(us_right, _last_r)
    sleep(SENSOR_GAP_MS)

    _last_l = raw_l
    _last_r = raw_r

    left  = _anticipate_distance(raw_l, prev_l)
    right = _anticipate_distance(raw_r, prev_r)

    return left, color_name, right


def open_side(left, right):
    # Choose the side with more space.
    if left - right > SIDE_DEADBAND:
        return "LEFT"

    if right - left > SIDE_DEADBAND:
        return "RIGHT"

    return DEFAULT_TURN


def opposite_side(direction):
    if direction == "LEFT":
        return "RIGHT"
    return "LEFT"

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
    global last_steer_target, last_steer_sign

    target = int(clamp(target, -ANGLE_DANGER, ANGLE_DANGER))

    # Tiny steering corrections create visible wobble but do not help much.
    # Snap very small commands to true center.
    if abs(target) <= PID_CENTER_SNAP:
        target = ANGLE_CENTER

    if abs(target - last_steer_target) >= STEER_COMMAND_MIN_CHANGE:

        if target > 0:
            new_sign = 1
        elif target < 0:
            new_sign = -1
        else:
            new_sign = 0

        commanded_target = target

        # Backlash compensation: only add the extra push when the steering
        # direction actually reverses (LEFT -> RIGHT or RIGHT -> LEFT), not
        # on every command. If it's still turning the same way it was
        # already turning, the linkage slack is already taken up.
        if new_sign != 0 and last_steer_sign != 0 and new_sign != last_steer_sign:
            commanded_target = target + (new_sign * STEER_BACKLASH_DEG)
            commanded_target = int(clamp(commanded_target, -ANGLE_DANGER, ANGLE_DANGER))

        steering.on_to_position(
            SpeedPercent(STEER_MOTOR_SPEED),
            commanded_target,
            brake=True,
            block=False
        )

        # Keep last_steer_target as the TRUE logical angle (not the
        # backlash-inflated motor command), since other code (corner
        # detection, _safe_abs_steer, etc.) reads this expecting the real
        # requested steering angle.
        last_steer_target = target
        if new_sign != 0:
            last_steer_sign = new_sign


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

def wait_for_right_arrow_start():
    # The program will not begin driving until RIGHT is pressed.
    # BACK can still cancel safely before the run starts.
    stop()
    print("=" * 40)
    print("Ready. Press RIGHT arrow to start.")
    print("Press BACK to cancel.")
    print("=" * 40)

    while not btn.right:
        if btn.backspace:
            print("Back button pressed before start - exiting.")
            return False
        sleep(0.05)

    # Wait for release so holding RIGHT does not affect the run.
    while btn.right:
        sleep(0.05)

    print("Right arrow pressed - starting.")
    return True


# =========================
# PID SIDE CENTERING
# =========================

def pid_center(left, right, speed, max_angle=None, max_step=None):
    global pid_last_error, pid_integral, pid_filtered_angle, pid_in_deadband

    if max_angle is None:
        max_angle = PID_MAX_ANGLE
    if max_step is None:
        max_step = PID_MAX_STEP

    # A far wall must not dominate. Cap both readings only for control math;
    # emergency and wall-guard logic still receive the real distances.
    left_control = min(left, PID_FAR_CAP_CM)
    right_control = min(right, PID_FAR_CAP_CM)

    # Positive error: left wall is closer -> steer right (negative angle).
    raw_error = right_control - left_control

    # Small preventive bias begins before a wall becomes dangerous. It is
    # intentionally limited so it cannot create a violent correction.
    preventive_bias = 0.0
    if left < PID_PREVENTIVE_CM:
        ratio = (PID_PREVENTIVE_CM - left) / float(PID_PREVENTIVE_CM - WALL_GUARD_STRONG_CM)
        preventive_bias += clamp(ratio, 0.0, 1.0) * PID_PREVENTIVE_MAX_BIAS
    if right < PID_PREVENTIVE_CM:
        ratio = (PID_PREVENTIVE_CM - right) / float(PID_PREVENTIVE_CM - WALL_GUARD_STRONG_CM)
        preventive_bias -= clamp(ratio, 0.0, 1.0) * PID_PREVENTIVE_MAX_BIAS

    raw_error += preventive_bias
    abs_error = abs(raw_error)
    was_in_deadband = pid_in_deadband

    if pid_in_deadband:
        if abs_error > PID_DEADBAND_EXIT_CM:
            pid_in_deadband = False
    else:
        if abs_error <= PID_DEADBAND_CM:
            pid_in_deadband = True

    if pid_in_deadband:
        error = 0.0
        pid_integral *= 0.65
    else:
        error = raw_error

    pid_integral += error
    pid_integral = clamp(pid_integral, -PID_INTEGRAL_LIMIT, PID_INTEGRAL_LIMIT)

    if error == 0.0 or was_in_deadband:
        derivative = 0.0
    else:
        derivative = error - pid_last_error

    pid_last_error = error
    correction = (PID_KP * error) + (PID_KI * pid_integral) + (PID_KD * derivative)

    target_angle = clamp(-correction, -max_angle, max_angle)
    if abs(target_angle) <= PID_CENTER_SNAP:
        target_angle = 0.0

    desired = (PID_STEER_SMOOTHING * pid_filtered_angle) + ((1.0 - PID_STEER_SMOOTHING) * target_angle)
    step = clamp(desired - pid_filtered_angle, -max_step, max_step)
    pid_filtered_angle += step

    if abs(pid_filtered_angle) <= PID_CENTER_SNAP:
        pid_filtered_angle = 0.0

    drive_and_steer_signed(speed, pid_filtered_angle)


def pid_side_valid(value):
    return value >= PID_VALID_MIN_CM and value <= PID_VALID_MAX_CM

# =========================
# CORNER TRACKING
# =========================

def _safe_abs_steer():
    # last_steer_target starts at 999 before the first steering command.
    # Ignore that startup value so it does not create a false valid corner.
    if last_steer_target > ANGLE_DANGER or last_steer_target < -ANGLE_DANGER:
        return 0
    return abs(last_steer_target)


def check_corner(front_dist, elapsed_time):
    global corners_counted, laps_completed, in_corner
    global last_corner_time, lap_split_time, post_corner_until
    global corner_entry_candidate_time, corner_enter_time
    global corner_min_front, corner_max_steer
    global finish_requested, finish_request_time

    if finish_requested:
        return

    now = time()

    # Step 1: require the front distance to stay close briefly before
    # entering corner mode. This avoids counting one-frame sensor spikes.
    if not in_corner:
        if front_dist < CORNER_ENTRY_DIST:
            if corner_entry_candidate_time == 0.0:
                corner_entry_candidate_time = now

            elif (now - corner_entry_candidate_time) >= CORNER_ENTRY_HOLD_TIME:
                in_corner = True
                corner_enter_time = now
                corner_min_front = front_dist
                corner_max_steer = _safe_abs_steer()

        else:
            corner_entry_candidate_time = 0.0

        return

    # Step 2: while inside a possible corner, remember how close the front
    # got and whether the robot actually steered like a real turn.
    if front_dist < corner_min_front:
        corner_min_front = front_dist

    steer_now = _safe_abs_steer()
    if steer_now > corner_max_steer:
        corner_max_steer = steer_now

    # Step 3: count the corner only after the robot has exited the turn zone.
    if front_dist > CORNER_EXIT_DIST:
        in_corner = False
        corner_entry_candidate_time = 0.0

        time_inside = now - corner_enter_time

        valid_corner = (
            time_inside >= CORNER_MIN_INSIDE_TIME and
            corner_min_front <= CORNER_REAL_FRONT_CM and
            corner_max_steer >= CORNER_MIN_STEER_ANGLE and
            (now - last_corner_time) >= CORNER_COOLDOWN
        )

        if not valid_corner:
            print("[IGNORED] possible false corner | front_min:{:.0f} steer:{} time:{:.2f}s gap:{:.2f}s".format(
                corner_min_front, corner_max_steer, time_inside, now - last_corner_time
            ))
            return

        corners_counted += 1
        last_corner_time = now
        post_corner_until = max(post_corner_until, now + POST_CORNER_CENTER)
        reset_pid()

        try:
            volts = round(battery.measured_volts, 2)
        except Exception:
            volts = -1.0
        CORNER_VOLTAGE_LOG.append((corners_counted, round(now - run_start, 1), volts))

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

        if corners_counted >= TARGET_CORNERS:
            if elapsed_time >= MINIMUM_FINISH_TIME_SECONDS:
                finish_requested = True
                finish_request_time = now
                print("Target reached: {} corners / {} laps. Parking stop armed.".format(
                    corners_counted, TOTAL_LAPS
                ))
            else:
                # This usually means the middle square caused an extra count.
                # Keep driving and require another valid corner after the minimum time.
                print("[EARLY TARGET IGNORED] {} corners at {:.1f}s. Need at least {:.1f}s.".format(
                    corners_counted, elapsed_time, MINIMUM_FINISH_TIME_SECONDS
                ))

# =========================
# STRAIGHT FRONT-SENSOR FIX
# =========================

def _last_steer_direction():
    # Positive steering target = LEFT, negative = RIGHT.
    # This helps detect when the robot is still steering into a wall.
    if last_steer_target > PID_CENTER_SNAP:
        return "LEFT"

    if last_steer_target < -PID_CENTER_SNAP:
        return "RIGHT"

    return "CENTER"


def choose_front_fix_direction(left, front, right):
    # Use all sensors:
    # - front says there is a wall ahead
    # - side sensors say which wall is being approached
    # - current steering tells us if the robot is oversteering into that wall

    left_very_close = left <= FRONT_FIX_SIDE_DANGER_CM
    right_very_close = right <= FRONT_FIX_SIDE_DANGER_CM

    if left_very_close and right_very_close:
        return open_side(left, right)

    if left_very_close:
        return "RIGHT"

    if right_very_close:
        return "LEFT"

    left_close = left <= FRONT_FIX_SIDE_CLOSE_CM
    right_close = right <= FRONT_FIX_SIDE_CLOSE_CM

    if left_close and not right_close:
        return "RIGHT"

    if right_close and not left_close:
        return "LEFT"

    # If side readings are not decisive, cancel the current steering direction.
    # Example: if the robot is steering LEFT and the front wall is getting too
    # close, steering RIGHT is the fastest way to stop the oversteer.
    steer_dir = _last_steer_direction()

    if steer_dir == "LEFT":
        return "RIGHT"

    if steer_dir == "RIGHT":
        return "LEFT"

    return open_side(left, right)


def should_start_front_fix(left, front, right):
    # Keep real corner behavior untouched. During real corner behavior,
    # front_corner_active is set by the existing front-wall/corner block.
    if in_corner or front_corner_active:
        return False

    if front > FRONT_FIX_ENTER_CM:
        return False

    # If the front is extremely close during normal running, correct even if
    # the side sensors are not perfect.
    if front <= FRONT_FIX_PANIC_CM:
        return True

    side_danger = (left <= FRONT_FIX_SIDE_DANGER_CM or
                   right <= FRONT_FIX_SIDE_DANGER_CM)

    if side_danger:
        return True

    side_close = (left <= FRONT_FIX_SIDE_CLOSE_CM or
                  right <= FRONT_FIX_SIDE_CLOSE_CM)

    steering_hard = _safe_abs_steer() >= FRONT_FIX_MIN_STEER_ANGLE

    # This is the oversteer case: the front is close, at least one side sensor
    # confirms wall risk, and the steering is not close to centered.
    return side_close and steering_hard


def front_sensor_fix(left, front, right):
    global front_fix_active, front_fix_direction

    if front_fix_active:
        if front >= FRONT_FIX_EXIT_CM:
            front_fix_active = False
            reset_pid()
            return False
    else:
        if not should_start_front_fix(left, front, right):
            return False

        front_fix_active = True

    front_fix_direction = choose_front_fix_direction(left, front, right)
    reset_pid()

    if front <= FRONT_FIX_PANIC_CM:
        drive_and_steer(SPEED_DANGER, front_fix_direction, FRONT_FIX_PANIC_ANGLE)
    else:
        drive_and_steer(FRONT_FIX_SPEED, front_fix_direction, FRONT_FIX_ANGLE)

    return True


# =========================
# POST-CORNER STABILITY
# =========================

def remember_corner_turn(direction):
    global last_corner_turn_direction, front_corner_active

    last_corner_turn_direction = direction
    front_corner_active = True


def update_front_corner_exit(front):
    global front_corner_active, post_corner_until

    # Front corner logic has just finished. Start anti-cut protection right now,
    # not only after the lap counter validates the corner.
    if front_corner_active and front > FRONT_GENTLE_CM:
        post_corner_until = max(post_corner_until, time() + POST_CORNER_CENTER)
        front_corner_active = False
        reset_pid()


def post_corner_drive_and_steer(drive_speed, direction, angle):
    # During the last part of the post-corner window, fade the steering
    # back toward center. This keeps the robot from leaving a corner with a
    # large steering angle that continues cutting toward the inner wall.
    remaining = post_corner_until - time()

    if remaining < POST_CORNER_RELEASE_TIME:
        scale = clamp(remaining / POST_CORNER_RELEASE_TIME, 0.0, 1.0)
        angle = angle * scale

    angle = clamp(angle, 0, POST_CORNER_SOFT_STEER_LIMIT)
    drive_and_steer(drive_speed, direction, angle)


def post_corner_protect(left, right):
    global post_curve_recovery_active, post_curve_alignment_active
    global post_curve_alignment_until, post_curve_stable_count, post_corner_until
    global post_curve_previous_outer

    now = time()

    # The exterior wall is opposite the turn direction. During a LEFT curve,
    # the right wall is exterior; during a RIGHT curve, the left wall is exterior.
    outer_side = opposite_side(curve_turn_direction)
    if outer_side == "LEFT":
        outer_dist = left
    else:
        outer_dist = right

    outer_approaching = False
    if post_curve_previous_outer is not None:
        outer_approaching = (
            outer_dist < POST_CURVE_FAR_IGNORE_CM and
            post_curve_previous_outer < POST_CURVE_FAR_IGNORE_CM and
            outer_dist < (post_curve_previous_outer - POST_CURVE_OUTER_DROP_CM)
        )

    if outer_dist < POST_CURVE_FAR_IGNORE_CM:
        post_curve_previous_outer = outer_dist

    # ---------------------------------------------------------
    # STAGE 1: COMPLETE AND ALIGN THE CURVE EXIT
    # ---------------------------------------------------------
    # The second color is under the front sensor before the entire chassis has
    # finished rotating. Keep a short arc in the same direction as the curve so
    # the robot does not straighten while still facing the exterior wall.
    if post_curve_alignment_active:
        nearest_side = None
        nearest_dist = 999.0

        if left < POST_CURVE_FAR_IGNORE_CM:
            nearest_side = "LEFT"
            nearest_dist = left

        if right < POST_CURVE_FAR_IGNORE_CM and right < nearest_dist:
            nearest_side = "RIGHT"
            nearest_dist = right

        # A genuinely close wall always overrides the alignment arc.
        if nearest_side is not None and nearest_dist <= POST_CURVE_ALIGN_DANGER_CM:
            post_curve_stable_count = 0
            reset_pid()
            drive_and_steer(
                SPEED_POST_CORNER_CLOSE,
                opposite_side(nearest_side),
                POST_CURVE_CLOSE_ANGLE
            )
            return True

        # During the fixed alignment interval, continue in the original curve
        # direction. If both sensors are blind, use a smaller angle, because the
        # robot only needs to finish rotating—not begin another full corner.
        if now < post_curve_alignment_until:
            reset_pid()

            both_blind = (
                left >= POST_CURVE_REASONABLE_MAX and
                right >= POST_CURVE_REASONABLE_MAX
            )

            if both_blind:
                align_angle = POST_CURVE_ALIGN_BLIND_ANGLE
            else:
                align_angle = POST_CURVE_ALIGN_ANGLE

            drive_and_steer(
                POST_CURVE_ALIGN_SPEED,
                curve_turn_direction,
                align_angle
            )
            return True

        post_curve_alignment_active = False
        post_curve_stable_count = 0
        reset_pid()

    # ---------------------------------------------------------
    # STAGE 2: SENSOR-BASED RECOVERY
    # ---------------------------------------------------------
    # If the exterior wall is getting closer, the robot is still pointing
    # outward. Keep steering toward the inside (same direction as the curve)
    # before trusting normal PID. This has priority over apparently valid pairs.
    if outer_dist < POST_CURVE_FAR_IGNORE_CM and (
            outer_dist <= POST_CURVE_OUTER_SAFE_CM or outer_approaching):
        post_curve_stable_count = 0
        reset_pid()

        if outer_dist <= POST_CURVE_VERY_CLOSE_CM:
            trend_angle = POST_CURVE_CLOSE_ANGLE
            trend_speed = SPEED_POST_CORNER_CLOSE
        elif outer_dist <= POST_CURVE_OUTER_SAFE_CM:
            trend_angle = POST_CURVE_MEDIUM_ANGLE
            trend_speed = SPEED_POST_CORNER
        else:
            trend_angle = POST_CURVE_OUTER_TREND_ANGLE
            trend_speed = SPEED_POST_CORNER

        drive_and_steer(
            trend_speed,
            curve_turn_direction,
            trend_angle
        )
        return True

    # Ignore a side that is extremely far away. It may be seeing through the
    # curve opening or producing a random long reading.
    left_reasonable = left <= POST_CURVE_REASONABLE_MAX
    right_reasonable = right <= POST_CURVE_REASONABLE_MAX

    nearest_side = None
    nearest_dist = 999.0

    if left < POST_CURVE_FAR_IGNORE_CM:
        nearest_side = "LEFT"
        nearest_dist = left

    if right < POST_CURVE_FAR_IGNORE_CM and right < nearest_dist:
        nearest_side = "RIGHT"
        nearest_dist = right

    # Obey the nearest trustworthy wall until it is safely separated.
    if nearest_side is not None and nearest_dist <= POST_CURVE_SAFE_MIN_CM:
        post_curve_stable_count = 0
        reset_pid()

        if nearest_dist <= POST_CURVE_VERY_CLOSE_CM:
            angle = POST_CURVE_CLOSE_ANGLE
            speed = SPEED_POST_CORNER_CLOSE
        else:
            angle = POST_CURVE_MEDIUM_ANGLE
            speed = SPEED_POST_CORNER

        drive_and_steer(speed, opposite_side(nearest_side), angle)
        return True

    both_safe = (
        left_reasonable and right_reasonable and
        left >= POST_CURVE_RELIABLE_MIN and
        right >= POST_CURVE_RELIABLE_MIN and
        left <= POST_CURVE_REASONABLE_MAX and
        right <= POST_CURVE_REASONABLE_MAX and
        outer_dist > POST_CURVE_OUTER_SAFE_CM and
        not outer_approaching and
        abs(left - right) <= POST_CURVE_STABLE_DIFF_CM
    )

    if both_safe:
        post_curve_stable_count += 1
    else:
        post_curve_stable_count = 0

    if post_curve_stable_count >= POST_CURVE_STABLE_SAMPLES:
        post_curve_recovery_active = False
        post_curve_alignment_active = False
        post_curve_stable_count = 0
        post_curve_previous_outer = None
        post_corner_until = 0.0
        reset_pid()
        return False

    # One reliable sensor: use only that wall and ignore the far-away reading.
    if left_reasonable and not right_reasonable:
        if left < PID_PREVENTIVE_CM:
            reset_pid()
            drive_and_steer(SPEED_POST_CORNER, "RIGHT", POST_CURVE_GENTLE_ANGLE)
        else:
            # Keep a tiny continuation of the curve instead of snapping straight.
            drive_and_steer(SPEED_POST_CORNER, curve_turn_direction, 8)
        return True

    if right_reasonable and not left_reasonable:
        if right < PID_PREVENTIVE_CM:
            reset_pid()
            drive_and_steer(SPEED_POST_CORNER, "LEFT", POST_CURVE_GENTLE_ANGLE)
        else:
            drive_and_steer(SPEED_POST_CORNER, curve_turn_direction, 8)
        return True

    if left_reasonable and right_reasonable:
        pid_center(
            left,
            right,
            SPEED_POST_CORNER,
            POST_CURVE_PID_MAX_ANGLE,
            POST_CURVE_PID_MAX_STEP
        )
        return True

    # Neither sensor sees a believable wall. Never center here: that was the
    # behavior that let the robot continue directly toward the exterior wall.
    # Continue a small arc in the curve direction until a wall becomes visible.
    reset_pid()
    drive_and_steer(
        POST_CURVE_ALIGN_SPEED,
        curve_turn_direction,
        POST_CURVE_ALIGN_BLIND_ANGLE
    )
    return True


# =========================
# NAVIGATION LOGIC
# =========================

def wall_guard(left, right):
    # Close-wall protection only.
    # In the previous version, this layer was active too early and fought the
    # PID on normal straights. Now it only takes over when a side is truly
    # close enough that smooth PID centering is no longer enough.
    # Returns True if it took control.

    left_close = left <= WALL_GUARD_CM
    right_close = right <= WALL_GUARD_CM

    if not left_close and not right_close:
        return False

    reset_pid()

    # If both sides are close, steer toward the side with more space.
    if left_close and right_close:
        if left <= WALL_GUARD_STRONG_CM or right <= WALL_GUARD_STRONG_CM:
            drive_and_steer(SPEED_WALL_GUARD, open_side(left, right), WALL_GUARD_STRONG_ANGLE)
        else:
            drive_and_steer(SPEED_PID_CAUTION, open_side(left, right), WALL_GUARD_CLOSE_ANGLE)
        return True

    if left <= WALL_GUARD_STRONG_CM:
        drive_and_steer(SPEED_WALL_GUARD, "RIGHT", WALL_GUARD_STRONG_ANGLE)
        return True

    if right <= WALL_GUARD_STRONG_CM:
        drive_and_steer(SPEED_WALL_GUARD, "LEFT", WALL_GUARD_STRONG_ANGLE)
        return True

    if left_close:
        drive_and_steer(SPEED_PID_CAUTION, "RIGHT", WALL_GUARD_CLOSE_ANGLE)
        return True

    if right_close:
        drive_and_steer(SPEED_PID_CAUTION, "LEFT", WALL_GUARD_CLOSE_ANGLE)
        return True

    return False

def navigate(left, color_detected, right):
    global post_curve_pid_handoff_pending
    global post_second_color_sharp_active, post_second_color_sharp_until

    # =========================
    # 0) COLOR CURVE MODE - TOTAL ULTRASONIC/PID LOCKOUT
    # =========================
    # This check MUST be first. While curve_mode is active, no ultrasonic
    # emergency, wall guard, fallback, or PID layer is allowed to run.
    if curve_mode:
        color_curve_drive(left, right)
        return

    # =========================
    # 0.5) SHARP TURN AFTER SECOND COLOR - STILL NO ULTRASONIC/PID
    # =========================
    # This stage intentionally precedes every sensor-based safety/controller
    # layer. It keeps the same curve command for a short fixed pulse.
    if post_second_color_sharp_active:
        if time() < post_second_color_sharp_until:
            post_second_color_sharp_drive()
            return

        # Pulse finished: re-enable ultrasonic data and PID immediately.
        post_second_color_sharp_active = False
        post_second_color_sharp_until = 0.0
        post_curve_pid_handoff_pending = False
        pid_center(left, right, SPEED_POST_CORNER)
        return

    # =========================
    # 0) ABSOLUTE SIDE HIT RISK
    # =========================
    # The front ultrasonic is now a color sensor, so this panic layer only
    # uses the left and right ultrasonic sensors.

    if left <= HIT_RISK_CM or right <= HIT_RISK_CM:
        reset_pid()

        if left <= HIT_RISK_CM and right <= HIT_RISK_CM:
            drive_and_steer(SPEED_DANGER, open_side(left, right), ANGLE_DANGER)
            return

        if left <= HIT_RISK_CM:
            drive_and_steer(SPEED_DANGER, "RIGHT", ANGLE_DANGER)
            return

        drive_and_steer(SPEED_DANGER, "LEFT", ANGLE_DANGER)
        return

    # =========================
    # 1) EMERGENCY SIDE WALL AVOIDANCE
    # =========================
    # Last line of defense before a side bump.

    if left <= SIDE_EMERGENCY_CM or right <= SIDE_EMERGENCY_CM:
        reset_pid()

        if left <= SIDE_EMERGENCY_CM and right <= SIDE_EMERGENCY_CM:
            drive_and_steer(SPEED_DANGER, open_side(left, right), ANGLE_DANGER)
            return

        if left <= SIDE_EMERGENCY_CM:
            drive_and_steer(SPEED_DANGER, "RIGHT", ANGLE_DANGER)
            return

        drive_and_steer(SPEED_DANGER, "LEFT", ANGLE_DANGER)
        return

    # =========================
    # 3) DIRECT POST-CURVE PID HANDOFF
    # =========================
    # Fallback handoff state. Normally the timed sharp-turn block above hands
    # control directly to PID as soon as its pulse finishes.

    if post_curve_pid_handoff_pending:
        # No exit hold and no centered waiting stage.
        post_curve_pid_handoff_pending = False
        pid_center(left, right, SPEED_POST_CORNER)
        return

    # =========================
    # 4) NORMAL STRAIGHT DRIVING - PID FIRST
    # =========================
    # If both sides are readable and not truly close, PID is the normal
    # straight controller. Color markers are only used to enter/exit curves.

    left_valid = pid_side_valid(left)
    right_valid = pid_side_valid(right)

    if left_valid and right_valid:
        # If a wall is truly close, let wall_guard take over.
        # Otherwise keep PID in charge, even if one side is a little closer.
        if left <= WALL_GUARD_CM or right <= WALL_GUARD_CM:
            if wall_guard(left, right):
                return

        # Smooth, persistent straight-line control.
        pid_center(left, right, SPEED_PID)
        return

    # =========================
    # 5) BLIND / SINGLE-SIDE FALLBACK ONLY WHEN CLOSE
    # =========================
    # Same side-sensor fallback as before, but without front ultrasonic input.

    left_blind = left > BLIND_SIDE_THRESHOLD
    right_blind = right > BLIND_SIDE_THRESHOLD

    if left_blind and right <= WALL_GUARD_CM:
        reset_pid()
        drive_and_steer(SPEED_PID_CAUTION, "LEFT", WALL_GUARD_CLOSE_ANGLE)
        return

    if right_blind and left <= WALL_GUARD_CM:
        reset_pid()
        drive_and_steer(SPEED_PID_CAUTION, "RIGHT", WALL_GUARD_CLOSE_ANGLE)
        return

    if left_valid and not right_valid:
        if left <= WALL_GUARD_STRONG_CM:
            reset_pid()
            drive_and_steer(SPEED_PID_CAUTION, "RIGHT", SINGLE_SIDE_STRONG_ANGLE)
            return
        if left <= WALL_GUARD_CM:
            reset_pid()
            drive_and_steer(SPEED_PID_CAUTION, "RIGHT", SINGLE_SIDE_GENTLE_ANGLE)
            return

    if right_valid and not left_valid:
        if right <= WALL_GUARD_STRONG_CM:
            reset_pid()
            drive_and_steer(SPEED_PID_CAUTION, "LEFT", SINGLE_SIDE_STRONG_ANGLE)
            return
        if right <= WALL_GUARD_CM:
            reset_pid()
            drive_and_steer(SPEED_PID_CAUTION, "LEFT", SINGLE_SIDE_GENTLE_ANGLE)
            return

    # =========================
    # 6) SAFE / NO CLEAR SIDE READING
    # =========================
    # Do not invent corrections if the readings are not useful and nothing is
    # close. Go straight instead of adding another steering layer.

    reset_pid()
    drive_and_steer(SPEED_FAST, "CENTER", ANGLE_CENTER)

# =========================
# WARMUP
# =========================

def warmup():
    print("Warming up sensors...")

    set_color_light_on()

    for i in range(15):
        read_all_fast()
        print("  {}/15".format(i + 1), end="\r")

    left, color_name, right = read_all_fast()

    print("\nSensors ready | L:{:.1f} Color:{} RGB:{} R:{:.1f}".format(
        left, color_name, last_color_rgb, right
    ))

    # The front ultrasonic was replaced by the color sensor, so there is no
    # front-distance startup block anymore. Side sensors being close is normal
    # when the robot starts inside a WRO corridor.

# =========================
# MAIN
# =========================

if not wait_for_right_arrow_start():
    stop()
    raise SystemExit

warmup()

print("=" * 40)
print("PID-first straights + color-line curve mode started")
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
print("Soft PID KP/KI/KD: {}/{}/{} | max angle:{} | smooth:{} step:{}".format(
    PID_KP, PID_KI, PID_KD, PID_MAX_ANGLE, PID_STEER_SMOOTHING, PID_MAX_STEP
))
print("PID deadband enter/exit: {}/{}cm (hysteresis)".format(
    PID_DEADBAND_CM, PID_DEADBAND_EXIT_CM
))
print("Color sensor INPUT_2 mode:{} | AZUL:{} NARANJA:{} threshold:{}".format(
    COLOR_SENSOR_MODE, AZUL_RGB, NARANJA_RGB, COLOR_THRESHOLD
))
print("Color curve: BLUE->LEFT | ORANGE->RIGHT | angle:{} speed:{}".format(
    COLOR_CURVE_STEER_ANGLE, COLOR_CURVE_SPEED
))
print("Curve control: ultrasonic sensors and PID ignored after first color")
print("Second/opposite color: curve ends immediately; ultrasonic PID resumes")
print("Color event cooldown:{}s | no exit hold".format(
    COLOR_EVENT_COOLDOWN
))
print("Side G/M/S: {}/{}/{} cm".format(
    SIDE_GENTLE_CM, SIDE_MEDIUM_CM, SIDE_STRONG_CM
))
print("Wall guard:{}cm strong:{}cm".format(
    WALL_GUARD_CM, WALL_GUARD_STRONG_CM
))
print("Straight priority: PID first; color curve mode overrides straight PID")
print("Emergency side:{}cm Hit risk:{}cm Sensor gap:{}s".format(
    SIDE_EMERGENCY_CM, HIT_RISK_CM, SENSOR_GAP_MS
))
print("Post-color recovery | close:{} safe:{} far-ignore:{} stable:{}".format(
    POST_CURVE_CLOSE_CM, POST_CURVE_SAFE_MIN_CM,
    POST_CURVE_FAR_IGNORE_CM, POST_CURVE_STABLE_SAMPLES
))
print("Finish trigger: {} color curves = {} laps".format(
    TARGET_CORNERS, TOTAL_LAPS
))
print("Maximum safety time: {:.1f}s".format(RUN_TIME_LIMIT_SECONDS))
print("Minimum finish time: {:.1f}s | Parking extra: {:.1f}s".format(
    MINIMUM_FINISH_TIME_SECONDS, PARKING_EXTRA_SECONDS
))
print("Press BACK to stop.")
print("=" * 40)

run_start = time()
lap_split_time = run_start
last_print_time = run_start

drive_and_steer(SPEED_FAST, "CENTER", ANGLE_CENTER)

try:
    while True:

        now_loop = time()

        # Maximum-time safety cutoff only.
        # Parking/finish is handled by the corner/lap counter below.
        if now_loop - run_start >= RUN_TIME_LIMIT_SECONDS:
            print("Maximum time reached - stopping for safety.")
            break

        if btn.backspace:
            print("Back button pressed - stopping.")
            break

        left, color_name, right = read_all_fast()

        check_color_curve(color_name, left, right, now_loop - run_start)

        if finish_requested:
            if PARKING_EXTRA_SECONDS <= 0.0:
                print("3 laps detected - stopping/parking now.")
                break

            if time() - finish_request_time >= PARKING_EXTRA_SECONDS:
                print("3 laps detected + extra parking time done - stopping.")
                break

        navigate(left, color_name, right)

        if DEBUG_PRINT:
            now = time()

            if now - last_print_time >= PRINT_INTERVAL:
                print("L:{:.0f} C:{} RGB:{} R:{:.0f} | c:{} laps:{} | pid_e:{:.1f}".format(
                    left, color_name, last_color_rgb, right, corners_counted, laps_completed, pid_last_error
                ))
                last_print_time = now

        if LOOP_DELAY > 0:
            sleep(LOOP_DELAY)

except KeyboardInterrupt:
    print("Keyboard interrupt")

finally:
    stop()
    total_time = time() - run_start

    print("Stopped | color curves:{} laps:{} time:{:.1f}s".format(
        corners_counted, laps_completed, total_time
    ))

    if CORNER_VOLTAGE_LOG:
        print("=" * 40)
        print("BATTERY VOLTAGE PER COLOR CURVE")
        print("corner  t(s)   volts")
        for corner_n, t, volts in CORNER_VOLTAGE_LOG:
            print("{:<7} {:<6} {}".format(corner_n, t, volts))
        print("=" * 40)



