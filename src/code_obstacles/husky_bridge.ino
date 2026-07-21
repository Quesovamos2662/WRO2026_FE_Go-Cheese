// WRO Future Engineers 2026 - Go!Cheese
// Nano side of the HuskyLens bridge. The Nano is I2C master to the
// HuskyLens (A4/A5, address 0x32) and, separately, a plain USB serial
// device to the EV3. It does not do any driving logic itself: it just
// picks the single most relevant pillar each cycle and hands the EV3 a
// small text packet it can parse in one line.
//
// Requires the "HUSKYLENS" library (DFRobot) installed in the Arduino IDE.
// Requires the HuskyLens to already be trained with Color Recognition:
// red pillar learned as ID1, green pillar learned as ID2, matching what
// was confirmed on the device screen.

#include "HUSKYLENS.h"
#include <Wire.h>

HUSKYLENS huskylens;

const int PILLAR_RED_ID = 1;
const int PILLAR_GREEN_ID = 2;

const unsigned long SERIAL_BAUD = 115200;
// Matches the EV3 main loop's ~10ms cadence (LOOP_DELAY in navigate.py) so
// the EV3 gets a fresh reading roughly every loop instead of piling up a
// serial backlog it has to catch up on.
const unsigned long SEND_INTERVAL_MS = 10;

// A real pillar is 50mm wide x 100mm tall, so its block should read
// noticeably taller than wide (~2:1 head-on). A shadow along the base of
// a wall is the opposite shape: a low, wide strip. Rejecting anything
// outside this range throws out most wall-shadow false positives before
// they're ever sent. These bounds are still an estimate, not measured --
// use DEBUG_RAW below to capture real numbers off your own hardware and
// tighten further from there.
const float PILLAR_ASPECT_MIN = 1.4;
const float PILLAR_ASPECT_MAX = 4.0;

// A shadow strip can still occasionally pass the aspect check for one or
// two frames as the camera angle sweeps through it during a curve. A real
// pillar stays in view and keeps roughly the same shape for many frames
// in a row; a shadow doesn't. This used to be the main defense against
// the wall shadow, which is why it was raised to 5 -- but the actual
// captured shadow came back at 0.52 aspect, well outside the 1.4-4.0
// window on its own, so the aspect check is doing the real rejection work
// with a wide margin. Confirm count's job now is just smoothing over
// incidental single-frame noise, not stopping the shadow, so it can run
// lower. Each frame here costs SEND_INTERVAL_MS of real reaction delay
// regardless of robot speed (2 frames = ~20ms, vs 50ms at the old value
// of 5) -- if the shadow starts getting through again, raise this back
// up before touching the aspect bounds.
const int CONFIRM_COUNT = 2;

// Set true and reflash, then run with the Nano plugged into a laptop
// (not the EV3) with the Arduino Serial Monitor open at 115200 baud.
// Point the camera at a real pillar and note the width/height/aspect it
// prints, then point it at the problem shadow near the wall and note
// those numbers too. That comparison is what should actually set
// PILLAR_ASPECT_MIN/MAX and CONFIRM_COUNT above, instead of guessing.
// Set back to false before flashing the version that runs on the EV3.
const bool DEBUG_RAW = false;

unsigned long lastSend = 0;

// Independent leaky counters per color instead of one shared streak. A
// frame that fails the aspect check costs 1 point instead of wiping the
// whole streak to 0 -- an occasional dip near the aspect boundary just
// pauses progress for a frame rather than restarting the count from
// scratch, which is what was making red (or whichever color runs closer
// to the aspect threshold on this hardware) confirm noticeably later
// than the other despite showing up on the HuskyLens screen just as fast.
// A real shadow never passes the aspect check in the first place, so it
// never earns any points here either way -- this only fixes slow
// confirmation of a real pillar, it doesn't loosen shadow rejection.
int redStreak = 0;
int greenStreak = 0;
int redWidth = 0, redXCenter = 0;
int greenWidth = 0, greenXCenter = 0;

void setup() {
  Serial.begin(SERIAL_BAUD);
  Wire.begin();

  // Keep retrying instead of giving up silently. Sending a heartbeat line
  // while waiting means the EV3 side sees "no pillar" rather than a dead
  // port if the HuskyLens is slow to power up or the cable is loose.
  while (!huskylens.begin(Wire)) {
    Serial.println(F("N,0,0"));
    delay(100);
  }

  huskylens.writeAlgorithm(ALGORITHM_COLOR_RECOGNITION);
}

void loop() {
  if (millis() - lastSend < SEND_INTERVAL_MS) {
    return;
  }
  lastSend = millis();

  int bestRedWidth = 0, bestRedXCenter = 0, bestRedHeight = 0;
  int bestGreenWidth = 0, bestGreenXCenter = 0, bestGreenHeight = 0;

  // If both pillars are visible at once (e.g. an X-intersection with
  // signs on both sides), each color's own widest block is tracked
  // separately -- whichever color actually confirms below gets used,
  // preferring the nearer one if somehow both cross the threshold on
  // the same frame. Anything that isn't a learned ID1/ID2 block, or
  // doesn't look pillar-shaped, is ignored outright.
  if (huskylens.request()) {
    while (huskylens.available()) {
      HUSKYLENSResult result = huskylens.read();
      if (result.command != COMMAND_RETURN_BLOCK) {
        continue;
      }
      if (result.ID != PILLAR_RED_ID && result.ID != PILLAR_GREEN_ID) {
        continue;
      }
      if (result.width <= 0) {
        continue;
      }
      float aspect = (float)result.height / (float)result.width;

      if (DEBUG_RAW) {
        // Extra field count (5, not 3) means the EV3's parser harmlessly
        // drops these lines if this ever accidentally ships with
        // DEBUG_RAW left on -- but flash with it off for a real run
        // regardless, this is meant for the laptop bench test only.
        Serial.print(F("DBG,"));
        Serial.print(result.ID == PILLAR_RED_ID ? 'R' : 'G');
        Serial.print(',');
        Serial.print(result.width);
        Serial.print(',');
        Serial.print(result.height);
        Serial.print(',');
        Serial.println(aspect);
      }

      if (aspect < PILLAR_ASPECT_MIN || aspect > PILLAR_ASPECT_MAX) {
        continue;
      }

      if (result.ID == PILLAR_RED_ID) {
        if (result.width > bestRedWidth) {
          bestRedWidth = result.width;
          bestRedHeight = result.height;
          bestRedXCenter = result.xCenter;
        }
      } else {
        if (result.width > bestGreenWidth) {
          bestGreenWidth = result.width;
          bestGreenHeight = result.height;
          bestGreenXCenter = result.xCenter;
        }
      }
    }
  }

  // Leaky update: a color that had a passing block this frame gains a
  // point (capped at CONFIRM_COUNT, no benefit to overshooting it); a
  // color that didn't loses a point, floored at 0 instead of snapping
  // straight back to 0 on one miss.
  if (bestRedWidth > 0) {
    redStreak = min(redStreak + 1, CONFIRM_COUNT);
    redWidth = bestRedWidth;
    redXCenter = bestRedXCenter;
  } else {
    redStreak = max(redStreak - 1, 0);
  }

  if (bestGreenWidth > 0) {
    greenStreak = min(greenStreak + 1, CONFIRM_COUNT);
    greenWidth = bestGreenWidth;
    greenXCenter = bestGreenXCenter;
  } else {
    greenStreak = max(greenStreak - 1, 0);
  }

  bool redConfirmed = redStreak >= CONFIRM_COUNT;
  bool greenConfirmed = greenStreak >= CONFIRM_COUNT;

  char confirmedColor = 'N';
  int confirmedXCenter = 0;
  int confirmedWidth = 0;

  if (redConfirmed && greenConfirmed) {
    // Both confirmed at once (an X-intersection with a sign on each
    // side) -- report whichever is currently nearer.
    if (redWidth >= greenWidth) {
      confirmedColor = 'R';
      confirmedXCenter = redXCenter;
      confirmedWidth = redWidth;
    } else {
      confirmedColor = 'G';
      confirmedXCenter = greenXCenter;
      confirmedWidth = greenWidth;
    }
  } else if (redConfirmed) {
    confirmedColor = 'R';
    confirmedXCenter = redXCenter;
    confirmedWidth = redWidth;
  } else if (greenConfirmed) {
    confirmedColor = 'G';
    confirmedXCenter = greenXCenter;
    confirmedWidth = greenWidth;
  }

  // Plain ASCII CSV, one line per reading: <color>,<xCenter>,<width>\n
  // color is 'R', 'G', or 'N' (nothing relevant, confirmed, in view).
  // xCenter and width are in HuskyLens frame pixels (320x240 frame,
  // so xCenter ranges roughly 0-320).
  Serial.print(confirmedColor);
  Serial.print(',');
  Serial.print(confirmedXCenter);
  Serial.print(',');
  Serial.println(confirmedWidth);
}
