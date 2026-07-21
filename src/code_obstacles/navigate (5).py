#!/usr/bin/env python3
# WRO Future Engineers 2026 - Go!Cheese
# Simplified rewrite of the color-sensor corner navigation system.
# Same core behavior as the original 15.py: PID wall-following on the
# straights, an early/strong wall-protection override near the walls,
# a color-triggered steering hold through each corner (blue = left,
# orange = right, confirmed by seeing the opposite color then neutral
# floor), and a rear-ultrasonic parking search after the 12th curve.
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
from collections import deque
from time import sleep, time
import threading
import serial


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

for sensor in (left_sensor, right_sensor, rear_sensor):
    sensor.mode = 'US-DIST-CM'
color_sensor.mode = 'COL-COLOR'

steering.reset()
sleep(1.0)


# ================================================================
# TUNABLE CONSTANTS
# ================================================================
STEER_DIRECTION = -1
STEERING_SPEED = 23
MAX_PID_ANGLE = 24
KP, KI, KD = 0.28, 0.001, 0.08
INTEGRAL_LIMIT = 70.0

STRAIGHT_SPEED = -62
CORNER_SPEED = -43
LOOP_DELAY = 0.01

# Ultrasonic readings at or above this are treated as "no wall visible"
# rather than a real distance.
NO_WALL_CM = 180.0

# Wall protection, as (gentle_dist, severe_dist, gentle_angle, severe_angle,
# gentle_speed, severe_speed). POST_CURVE trips earlier and steers harder so
# the robot resettles into the corridor right after a turn.
WALL_NORMAL = (21.5, 19.0, 18, 32, -46, -40)
WALL_POST_CURVE = (30.0, 25.5, 24, 38, -39, -32)
POST_CURVE_GUARD_TIME = 0.60

# Both side sensors blind (open corner, missed wall): slow down and lean
# toward whichever wall was last seen instead of driving straight blind.
BLIND_SPEED = -30
BLIND_STEER_ANGLE = 16
BLIND_HOLD_ANGLE = 8
BLIND_STRONG_TIME = 0.55

# Floor color -> corner direction. First color seen decides the turn; the
# opposite color then neutral floor confirms the corner is finished.
ORANGE_GROUP = (ColorSensor.COLOR_RED, ColorSensor.COLOR_YELLOW, ColorSensor.COLOR_BROWN)
CORNER_ANGLE = {'BLUE': -34, 'ORANGE': 34}
CORNER_EXIT_FACTOR = 0.72  # soften the angle once the exit color is seen
CORNER_EMERGENCY_DIST = 15.5  # only a wall this close can override the turn
CORNER_EMERGENCY_ANGLE = 42
CORNER_EMERGENCY_SPEED = -30

# Reject a duplicate curve count if it follows the last one too closely, and
# give up on a stuck detector instead of missing curves for the rest of the lap.
MIN_CURVE_GAP_DEG = 140.0
MIN_CURVE_GAP_TIME = 0.20
CURVE_TIMEOUT_TIME = 5.0
CURVE_TIMEOUT_DEG = 2200.0
CURVES_PER_LAP = 4
TOTAL_CURVES = 12

# Rear parking: match the stationary start-of-run rear distance.
REAR_SAMPLES = 25
REAR_SAMPLE_DELAY = 0.025
REAR_TOLERANCE_CM = 2.5
REAR_FILTER_WINDOW = 5      # rolling median window while approaching, rejects single-frame spikes

# Speed drops in stages as the filtered gap to the target closes, so the
# robot is barely moving by the time it actually reaches the tolerance band
# instead of covering it at search speed. PARK_FAR_ERROR/PARK_NEAR_ERROR are
# the remaining-distance thresholds (cm) that pick which stage applies.
PARK_SEARCH_SPEED = -20
PARK_CREEP_SPEED = -12
PARK_CRAWL_SPEED = -6
PARK_FAR_ERROR = 20.0
PARK_NEAR_ERROR = 8.0

# Extra margin (cm) subtracted from the tolerance check before braking, to
# account for motor coast-to-stop distance at PARK_CRAWL_SPEED. Start at 0
# and raise it in ~0.5cm steps only if testing still shows overshoot.
STOP_MARGIN_CM = 0.0

# Once braked, the reading must hold inside tolerance this many stationary
# loops before we call it parked -- confirming while stopped instead of while
# still moving is what actually removes the overshoot risk.
REAR_HOLD_CONFIRMATIONS = 4

SEARCH_TIMEOUT_S = 20.0
SEARCH_MAX_DEG = 5000.0

# ----------------------------------------------------------------
# HUSKYLENS BRIDGE (via Nano over USB serial)
# ----------------------------------------------------------------
# Confirm the actual device name once the Nano is plugged in: run
# `ls /dev/tty*` before and after plugging it in over SSH/putty. CH340
# clone boards usually show up as /dev/ttyUSB0; boards with native USB
# show up as /dev/ttyACM0.
HUSKY_PORT = '/dev/ttyUSB0'
HUSKY_BAUD = 115200

# A block narrower than this is treated as too far away to react to yet,
# since a distant pillar's x position is noisy and reacting to it early
# just adds unnecessary weave. This also doubles as the point where the
# avoidance steer starts ramping in.
PILLAR_MIN_WIDTH = 40

# Width (proximity) at which the steer reaches full PILLAR_BIAS_ANGLE.
# Between PILLAR_MIN_WIDTH and this, the commanded angle increases in a
# straight line as the pillar gets bigger/closer -- that's what actually
# produces the "slowly steers over as it approaches" behavior, rather than
# snapping to full deflection the instant a pillar is confirmed. Lowered
# from 90 to 70: since lap time isn't the priority right now, full
# avoidance completes farther out (smaller width = farther away) instead
# of cutting it close, trading distance for margin while reliability is
# still the main problem to solve. Both values are still placeholders;
# walk the robot toward a real pillar and log husky_width to set these
# from the actual pixel widths at "just entering range" and "close enough
# that full avoidance is needed."
PILLAR_FULL_WIDTH = 70

# Steering bias (degrees) applied once fully engaged (pillar at or closer
# than PILLAR_FULL_WIDTH). This needs to be large enough that the robot's
# body actually clears the pillar sideways, not just enough to graze past
# it -- if the robot is still clipping or moving pillars at full deflection,
# raise this before touching anything else.
PILLAR_BIAS_ANGLE = 12.0

# Sign of the bias per color. Rule 9.19 requires passing red on the
# robot's right and green on the robot's left. This mapping is a starting
# guess for how that sign should combine with STEER_DIRECTION and set_steering's
# angle convention (positive angle already means a rightward corner per
# CORNER_ANGLE['ORANGE'] = 34) -- verify on the bench with the robot on a
# stand before trusting it on the actual track.
PILLAR_PASS_SIDE = {'RED': -1.0, 'GREEN': 1.0}

# Fraction of the gap between the current commanded bias and the target
# bias that gets closed each loop (~10ms, see LOOP_DELAY). This is what
# actually makes the steer smooth frame to frame instead of jumping
# straight to whatever the width-based ramp above computes -- it also
# means releasing a pillar glides the steering back to center instead of
# snapping straight, since the target simply becomes 0 once the pillar is
# out of view. Lower = smoother and slower to respond, higher = snappier.
PILLAR_BIAS_SMOOTHING = 0.12

# Drop a pillar reading this old and treat it as "nothing in view" -- a
# stalled or unplugged Nano should fail safe back to plain wall PID
# instead of steering on a frozen last-known position.
PILLAR_STALE_S = 0.30

# The old approach here was a flat cutoff: ignore the pillar entirely if
# either wall was under 20cm. That throws away legitimate avoidance room
# any time a wall happens to be nearby, which isn't what's wanted -- the
# robot should lean toward the pillar's correct side using as much of the
# lane as it safely can, and only ease off as it actually starts crowding
# whatever wall is on that side. So instead this is a proportional clamp:
# PILLAR_WALL_SAFE_CM matches WALL_NORMAL's own gentle_dist (21.5), the
# exact point wall protection itself would take over, so the handoff
# between "lean toward the pillar" and "wall protection has full control"
# is continuous instead of an abrupt jump. PILLAR_WALL_FREE_CM is the
# distance at which the wall is no longer a limiting factor at all.
PILLAR_WALL_SAFE_CM = WALL_NORMAL[0]
PILLAR_WALL_FREE_CM = 40.0

# Speed while actively easing toward a pillar (SpeedPercent, so negative
# is forward, same convention as STRAIGHT_SPEED/CORNER_SPEED). More time
# spent in the PILLAR_MIN_WIDTH-to-PILLAR_FULL_WIDTH window means more
# 10ms loops for the Nano's confirm counter and this file's bias
# smoothing to both settle before the robot is actually close -- slowing
# down specifically during that window buys real reaction margin without
# costing lap time on the open straight. Dropped below CORNER_SPEED (-43)
# on purpose: with obstacle handling still unreliable and no competitive
# pressure on time yet, this window should get more caution than a corner
# does, not less. Raise this back up once avoidance is consistently
# working and lap time starts mattering again.
PILLAR_APPROACH_SPEED = -30


# ================================================================
# STATE
# All mutated only by the functions named in the comment beside each group.
# ================================================================
integral = 0.0          # drive_straight
last_error = 0.0        # drive_straight

curve_state = 'ENTRY'   # update_curve_count: ENTRY -> EXIT -> NEUTRAL
entry_color = None
exit_color = None
entry_position = None
entry_time = None

completed_curves = 0            # register_curve
last_curve_position = None
last_curve_time = None

post_curve_guard_until = 0.0    # start_post_curve_guard / navigate

last_visible_wall = None        # drive_blind
blind_start_time = None

rear_start_distance = None      # set once at startup, read by update_parking
rear_history = deque(maxlen=REAR_FILTER_WINDOW)  # read_rear_filtered
parking_active = False          # arm_parking
parking_state = 'APPROACH'      # update_parking: APPROACH -> HOLD -> parked
hold_count = 0
parked = False

husky_color = None      # husky_reader_thread (writer) / read_pillar (reader)
husky_x_center = 0
husky_width = 0
husky_last_update = 0.0
husky_lock = threading.Lock()

pillar_debug_last_color = 'UNSET'  # navigate -- forces one log line on the very first loop

pillar_bias = 0.0       # update_pillar_bias -- smoothed steering offset, degrees
pillar_speed_ramp = 0.0 # update_pillar_speed -- smoothed 0..1 proximity used for the speed blend


# ================================================================
# HELPERS
# ================================================================
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


def valid_distance(value):
    return value is not None and 1.0 <= value < NO_WALL_CM


def set_steering(angle):
    target = int(clamp(angle, -90, 90) * STEER_DIRECTION)
    steering.on_to_position(SpeedPercent(STEERING_SPEED), target, brake=True, block=False)


def stop_robot():
    drive.off(brake=True)
    steering.off(brake=True)


def reset_pid():
    global integral, last_error
    integral = 0.0
    last_error = 0.0


def show(text, x=10, font='luBS14'):
    screen.clear()
    screen.text_pixels(text, x=x, y=45, font=font)
    screen.update()


# ================================================================
# SENSORS
# ================================================================
def read_walls():
    try:
        left = float(left_sensor.distance_centimeters)
        right = float(right_sensor.distance_centimeters)
    except Exception:
        return None, None
    return (left if valid_distance(left) else None,
            right if valid_distance(right) else None)


def read_rear():
    try:
        value = float(rear_sensor.distance_centimeters)
    except Exception:
        return None
    return value if valid_distance(value) else None


def read_rear_filtered():
    # A single bad ultrasonic frame (echo off an angled panel, a missed
    # ping) can trigger a false match or a false rejection. Taking the
    # median of the last REAR_FILTER_WINDOW readings throws out a lone
    # spike without lagging behind a real, sustained change the way an
    # average would.
    value = read_rear()
    if value is not None:
        rear_history.append(value)
    if not rear_history:
        return None
    ordered = sorted(rear_history)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def read_floor_color():
    try:
        detected = color_sensor.color
    except Exception:
        return None
    if detected == ColorSensor.COLOR_BLUE:
        return 'BLUE'
    if detected in ORANGE_GROUP:
        return 'ORANGE'
    return None


def husky_reader_thread():
    # Runs on its own thread instead of being polled inline in the main
    # loop, for the same reason the color sensor's blocking RGB-RAW read
    # was pulled off the main loop earlier in this project: a serial
    # readline() with any I/O hiccup would stall PID timing for however
    # long it blocks. This thread just keeps the latest reading current;
    # the main loop reads whatever is freshest and never waits on it.
    global husky_color, husky_x_center, husky_width, husky_last_update

    try:
        ser = serial.Serial(HUSKY_PORT, HUSKY_BAUD, timeout=0.5)
    except Exception as exc:
        print('HUSKYLENS SERIAL OPEN FAILED on {}: {}'.format(HUSKY_PORT, exc))
        return

    print('HUSKYLENS SERIAL OPENED on {}'.format(HUSKY_PORT))

    # If this thread is alive but nothing valid is ever parsed, the log
    # will show 0 received lines forever instead of just silence -- that
    # distinguishes "port opened but Nano isn't sending" from "Nano is
    # sending garbage" from "nothing is wrong here at all."
    lines_received = 0
    last_count_log = time()

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

        color_code, x_str, w_str = parts
        try:
            x_center = int(x_str)
            width = int(w_str)
        except ValueError:
            continue

        lines_received += 1
        now = time()
        if now - last_count_log >= 2.0:
            print('HUSKYLENS LINES RECEIVED: {} (last: {},{},{})'.format(
                lines_received, color_code, x_center, width
            ))
            last_count_log = now

        with husky_lock:
            if color_code == 'R':
                husky_color, husky_x_center, husky_width = 'RED', x_center, width
            elif color_code == 'G':
                husky_color, husky_x_center, husky_width = 'GREEN', x_center, width
            else:
                husky_color, husky_x_center, husky_width = None, 0, 0
            husky_last_update = time()


def read_pillar(now):
    # Returns (color, width) for a pillar worth reacting to, or (None, 0)
    # if nothing qualifies -- too small, stale, or no block at all.
    # Keeping the staleness/size filtering here means navigate() itself
    # doesn't need to know anything about the HuskyLens protocol. Shape
    # (aspect ratio) and frame-to-frame stability filtering, to reject
    # wall-shadow false positives, already happened on the Nano before
    # this value ever arrived over serial.
    with husky_lock:
        color, width, updated = (husky_color, husky_width, husky_last_update)

    if color is None or width < PILLAR_MIN_WIDTH:
        return None, 0
    if now - updated > PILLAR_STALE_S:
        return None, 0
    return color, width


def sample_rear_start_distance():
    # Averages a trimmed sample set (drops the extreme 20% on each end) to
    # damp ultrasonic spikes while the robot sits stationary at the start line.
    values = []
    for _ in range(REAR_SAMPLES):
        value = read_rear()
        if value is not None:
            values.append(value)
        sleep(REAR_SAMPLE_DELAY)

    if not values:
        return None

    values.sort()
    if len(values) >= 10:
        trim = max(1, len(values) // 5)
        values = values[trim:-trim]
    return sum(values) / len(values)


# ================================================================
# CURVE COUNTING
# entry_color/exit_color/curve_state form a 3-step latch: a real corner must
# show the entry color, then the opposite color, then neutral floor, in that
# order, before it counts. This throws away noise/partial readings for free
# since any state only advances on the exact color it is waiting for.
# ================================================================
def reset_curve_detector():
    global curve_state, entry_color, exit_color, entry_position, entry_time
    curve_state = 'ENTRY'
    entry_color = None
    exit_color = None
    entry_position = None
    entry_time = None


def corner_active():
    return curve_state in ('EXIT', 'NEUTRAL') and entry_color in CORNER_ANGLE


def corner_steering_angle():
    angle = CORNER_ANGLE[entry_color]
    if curve_state == 'NEUTRAL':
        angle *= CORNER_EXIT_FACTOR
    return angle


def register_curve(position, now):
    global completed_curves, last_curve_position, last_curve_time

    if last_curve_position is not None:
        if (position - last_curve_position < MIN_CURVE_GAP_DEG or
                now - last_curve_time < MIN_CURVE_GAP_TIME):
            print('CURVE REJECTED (too close to previous curve)')
            return

    completed_curves += 1
    last_curve_position, last_curve_time = position, now

    lap = min(3, completed_curves // CURVES_PER_LAP + 1)
    print('CURVE {}/{} | LAP {}/3'.format(completed_curves, TOTAL_CURVES, lap))
    show('LAP {}/3'.format(lap), x=42, font='luBS14')

    if completed_curves >= TOTAL_CURVES:
        arm_parking(position, now)
    else:
        start_post_curve_guard(now)


def update_curve_count(raw_color, position, now):
    global curve_state, entry_color, exit_color, entry_position, entry_time

    if parking_active:
        return

    # Give up on a stuck sequence instead of missing curves for a whole lap.
    if curve_state != 'ENTRY' and (now - entry_time > CURVE_TIMEOUT_TIME or
                                    position - entry_position > CURVE_TIMEOUT_DEG):
        print('CURVE SEQUENCE TIMED OUT, RESETTING')
        reset_curve_detector()

    if curve_state == 'ENTRY':
        if raw_color in CORNER_ANGLE:
            entry_color = raw_color
            exit_color = 'ORANGE' if raw_color == 'BLUE' else 'BLUE'
            entry_position, entry_time = position, now
            curve_state = 'EXIT'

    elif curve_state == 'EXIT':
        if raw_color == exit_color:
            curve_state = 'NEUTRAL'

    elif curve_state == 'NEUTRAL':
        if raw_color is None:
            register_curve(position, now)
            reset_curve_detector()


# ================================================================
# DRIVING MODES
# navigate() runs one strict priority chain per loop, highest first:
# parking search -> corner hold -> wall protection -> PID -> blind recovery.
# ================================================================
def steer_away_from_wall(left, right, angle):
    if left is not None and right is not None:
        set_steering(-angle if left < right else angle)
    elif left is not None:
        set_steering(-angle)
    elif right is not None:
        set_steering(angle)


def drive_corner(left, right):
    if ((left is not None and left <= CORNER_EMERGENCY_DIST) or
            (right is not None and right <= CORNER_EMERGENCY_DIST)):
        drive.on(SpeedPercent(CORNER_EMERGENCY_SPEED))
        steer_away_from_wall(left, right, CORNER_EMERGENCY_ANGLE)
    else:
        drive.on(SpeedPercent(CORNER_SPEED))
        set_steering(corner_steering_angle())
    reset_pid()


def start_post_curve_guard(now):
    global post_curve_guard_until
    post_curve_guard_until = now + POST_CURVE_GUARD_TIME
    reset_pid()


def apply_wall_protection(left, right, speed, now):
    profile = (WALL_POST_CURVE if now < post_curve_guard_until else WALL_NORMAL)
    gentle_dist, severe_dist, gentle_angle, severe_angle, gentle_speed, severe_speed = profile

    if (left is not None and left <= severe_dist) or (right is not None and right <= severe_dist):
        drive.on(SpeedPercent(severe_speed))
        steer_away_from_wall(left, right, severe_angle)
        reset_pid()
        return True

    if (left is not None and left <= gentle_dist) or (right is not None and right <= gentle_dist):
        drive.on(SpeedPercent(gentle_speed))
        steer_away_from_wall(left, right, gentle_angle)
        reset_pid()
        return True

    return False


def wall_clearance_factor(distance):
    # 0 right at the point wall protection would take over, ramping up to
    # 1 by the time the wall is no longer a meaningful constraint. A blind
    # sensor (None) means no wall detected on that side at all, so it's
    # not limiting anything -- full clearance.
    if distance is None:
        return 1.0
    return clamp(
        (distance - PILLAR_WALL_SAFE_CM) / float(PILLAR_WALL_FREE_CM - PILLAR_WALL_SAFE_CM),
        0.0, 1.0
    )


def pillar_proximity_ramp(width):
    # 0 right as the pillar enters reaction range (PILLAR_MIN_WIDTH), 1 by
    # the time it's close enough to need full avoidance (PILLAR_FULL_WIDTH).
    # Shared by the steering bias and the speed blend below so both ease
    # in together instead of the steer and the slowdown drifting out of
    # sync with each other.
    return clamp(
        (width - PILLAR_MIN_WIDTH) / float(PILLAR_FULL_WIDTH - PILLAR_MIN_WIDTH),
        0.0, 1.0
    )


def pillar_bias_target(color, width, left, right):
    # 0 while the pillar is too far to matter, ramping in a straight line
    # up to the full PILLAR_BIAS_ANGLE as it closes from PILLAR_MIN_WIDTH
    # to PILLAR_FULL_WIDTH. This is the "gets bigger as it gets closer"
    # signal driving the gradual steer -- no pillar in view means width=0
    # and this correctly returns 0.
    if color is None:
        return 0.0
    ramp = pillar_proximity_ramp(width)
    raw_bias = PILLAR_PASS_SIDE[color] * PILLAR_BIAS_ANGLE * ramp

    # Positive bias steers right (see CORNER_ANGLE's ORANGE=34 for the
    # same convention), so a rightward lean is limited by how much room
    # is left on the right, and a leftward lean by the room on the left.
    # This is what makes the robot use as much of the lane as it safely
    # can instead of either ignoring nearby walls or refusing to react
    # near them at all.
    target_wall_distance = right if raw_bias > 0 else left
    return raw_bias * wall_clearance_factor(target_wall_distance)


def update_pillar_bias(target):
    # Exponential smoothing toward whatever pillar_bias_target() currently
    # wants. This is what actually makes the steer "slow" rather than an
    # instant jump: a newly-confirmed pillar eases the bias in over
    # several loops, and a pillar that leaves view eases it back to 0 the
    # same way, since target simply becomes 0 once read_pillar reports
    # nothing in view.
    global pillar_bias
    pillar_bias += (target - pillar_bias) * PILLAR_BIAS_SMOOTHING
    return pillar_bias


def update_pillar_speed(color, width):
    # Same smoothing constant and the same underlying ramp as the steer,
    # so the robot eases into "steering around it" and "slowing down for
    # it" together rather than one lagging the other. No pillar in view
    # means the target ramp is 0, which glides speed back to
    # STRAIGHT_SPEED the same smooth way bias glides back to 0.
    global pillar_speed_ramp
    target_ramp = pillar_proximity_ramp(width) if color is not None else 0.0
    pillar_speed_ramp += (target_ramp - pillar_speed_ramp) * PILLAR_BIAS_SMOOTHING
    return STRAIGHT_SPEED + (PILLAR_APPROACH_SPEED - STRAIGHT_SPEED) * pillar_speed_ramp


def drive_straight(left, right, speed, bias=0.0):
    global integral, last_error

    error = right - left
    integral = clamp(integral + error, -INTEGRAL_LIMIT, INTEGRAL_LIMIT)
    derivative = error - last_error
    last_error = error
    correction = KP * error + KI * integral + KD * derivative

    # Bias rides on top of the normal wall-following correction rather
    # than replacing it, so the robot still tracks the corridor center
    # while leaning off toward the correct side for a pillar. bias is 0.0
    # on a normal straight with nothing to react to.
    drive.on(SpeedPercent(speed))
    max_angle = MAX_PID_ANGLE + PILLAR_BIAS_ANGLE
    set_steering(clamp(-correction + bias, -max_angle, max_angle))


def drive_blind(left, right, speed, now):
    global last_visible_wall, blind_start_time

    if left is not None or right is not None:
        last_visible_wall = 'LEFT' if (right is None or (left is not None and left < right)) else 'RIGHT'
        blind_start_time = None
        drive.on(SpeedPercent(speed))
        set_steering(0)
        return

    if blind_start_time is None:
        blind_start_time = now
        reset_pid()
        print('BLIND RECOVERY | last wall: {}'.format(last_visible_wall))

    drive.on(SpeedPercent(BLIND_SPEED))
    strong = (now - blind_start_time) <= BLIND_STRONG_TIME
    recovery_angle = BLIND_STEER_ANGLE if strong else BLIND_HOLD_ANGLE

    if last_visible_wall == 'LEFT':
        set_steering(-recovery_angle)
    elif last_visible_wall == 'RIGHT':
        set_steering(recovery_angle)
    else:
        set_steering(0)


# ================================================================
# REAR PARKING (after curve 12)
# ================================================================
def arm_parking(position, now):
    global parking_active, parking_state, hold_count
    parking_active = True
    parking_state = 'APPROACH'
    hold_count = 0
    rear_history.clear()
    reset_pid()
    print('PARKING SEARCH ARMED, target rear distance {}'.format(rear_start_distance))
    show('PARKING', x=35, font='luBS18')


def update_parking():
    # Two phases, not one continuous approach-and-match pass:
    #   APPROACH - drive toward the target, slowing in stages as the gap
    #               closes, and brake the instant the filtered reading
    #               enters the tolerance band.
    #   HOLD     - motor is off. Confirm the reading stays in tolerance
    #               for several stationary loops before calling it parked.
    # Because the robot is stopped for the whole HOLD phase, there is no
    # further travel that could push it past the target -- that's what
    # actually removes the overshoot, not the tolerance value itself.
    global parked, parking_state, hold_count

    current = read_rear_filtered()
    if current is None or rear_start_distance is None:
        drive.on(SpeedPercent(PARK_CRAWL_SPEED))
        set_steering(0)
        return False

    error = current - rear_start_distance
    remaining = abs(error) - STOP_MARGIN_CM

    if parking_state == 'APPROACH':
        if remaining <= REAR_TOLERANCE_CM:
            stop_robot()
            parking_state = 'HOLD'
            hold_count = 0
            print('PARK HOLD | filtered rear {:.1f} target {:.1f}'.format(
                current, rear_start_distance
            ))
            return False

        if remaining > PARK_FAR_ERROR:
            speed = PARK_SEARCH_SPEED
        elif remaining > PARK_NEAR_ERROR:
            speed = PARK_CREEP_SPEED
        else:
            speed = PARK_CRAWL_SPEED

        drive.on(SpeedPercent(speed))
        set_steering(0)
        return False

    # HOLD: confirm stationary before declaring parked.
    if abs(error) <= REAR_TOLERANCE_CM:
        hold_count += 1
    else:
        # The brake trigger was a filtered spike, not a real match. Ease
        # back into APPROACH at crawl speed rather than snapping to search
        # speed again.
        print('PARK HOLD LOST, resuming approach at crawl speed')
        parking_state = 'APPROACH'
        hold_count = 0
        return False

    if hold_count >= REAR_HOLD_CONFIRMATIONS:
        parked = True
        print('PARKED at rear distance {:.1f} cm (target {:.1f})'.format(
            current, rear_start_distance
        ))
        show('PARKED!', x=52, font='luBS18')
        return True

    return False


def parking_timed_out(position, search_start_position, search_start_time, now):
    if position - search_start_position >= SEARCH_MAX_DEG:
        show('NO TARGET', x=35, font='luBS18')
        return True
    if now - search_start_time >= SEARCH_TIMEOUT_S:
        show('TIMEOUT', x=52, font='luBS18')
        return True
    return False


# ================================================================
# PRIORITY CHAIN (called once per loop)
# ================================================================
def navigate(left, right, position, now):
    # Priority order, highest first: corner hold, then crash-prevention
    # wall protection, then pillar steering, then plain PID centering,
    # then blind recovery. Pillar steering sits below wall protection on
    # purpose -- a close exterior/interior wall is a harder failure than
    # passing a pillar on the wrong side, so it keeps veto power.
    if corner_active():
        drive_corner(left, right)
        return

    if apply_wall_protection(left, right, STRAIGHT_SPEED, now):
        return

    # Vision is trusted less than the ultrasonics right after a turn, when
    # the robot is still settling into the corridor and the camera angle
    # is least stable -- pillar reaction is fully suppressed for that
    # window. Outside of it, wall proximity no longer blocks pillar
    # reaction outright; it constrains it, via the wall_clearance_factor
    # inside pillar_bias_target below.
    in_post_curve_guard = now < post_curve_guard_until

    pillar_color, pillar_width = (None, 0) if in_post_curve_guard else read_pillar(now)
    bias_target = pillar_bias_target(pillar_color, pillar_width, left, right)

    global pillar_debug_last_color
    if pillar_color != pillar_debug_last_color:
        print('PILLAR {} | width={} bias_target={:.1f} deg'.format(
            pillar_color if pillar_color else 'LOST', pillar_width, bias_target
        ))
        pillar_debug_last_color = pillar_color

    # update_pillar_bias runs every loop, pillar in view or not, so the
    # steering offset always eases smoothly toward wherever it needs to be
    # next -- ramping in as a pillar closes in, and just as smoothly
    # easing back to 0 once it's out of view instead of snapping the
    # wheels straight the instant the pillar disappears.
    bias = update_pillar_bias(bias_target)
    speed = update_pillar_speed(pillar_color, pillar_width)

    if left is not None and right is not None:
        drive_straight(left, right, speed, bias)
    else:
        drive_blind(left, right, STRAIGHT_SPEED, now)


# ================================================================
# START
# ================================================================
def wait_for_left_button():
    show('READY!', x=66, font='luBS24')
    while buttons.left:
        sleep(0.02)
    while not buttons.left:
        sleep(0.02)
    while buttons.left:
        sleep(0.02)


try:
    threading.Thread(target=husky_reader_thread, daemon=True).start()

    wait_for_left_button()

    show('RECORD REAR', x=14, font='luBS14')
    rear_start_distance = sample_rear_start_distance()
    if rear_start_distance is None:
        show('REAR ERROR', x=28, font='luBS18')
        raise RuntimeError('Rear ultrasonic gave no valid start distance')
    print('REAR START DISTANCE: {:.1f} cm'.format(rear_start_distance))

    drive.position = 0
    reset_pid()
    show('RUNNING', x=49, font='luBS18')

    search_start_position = None
    search_start_time = None

    while True:
        now = time()
        position = abs(float(drive.position))

        if buttons.backspace:
            break

        if parking_active:
            if search_start_position is None:
                search_start_position, search_start_time = position, now
            if parking_timed_out(position, search_start_position, search_start_time, now):
                break
            if update_parking():
                break
        else:
            floor_color = read_floor_color()
            update_curve_count(floor_color, position, now)
            left, right = read_walls()
            navigate(left, right, position, now)

        sleep(LOOP_DELAY)

finally:
    stop_robot()
    if not parked:
        show('STOPPED', x=50, font='luBS18')
