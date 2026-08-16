#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-3-Clause
"""Tests for the decision and measurement logic, without touching audio."""

from importlib.machinery import SourceFileLoader
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bt-volume-step"
m = SourceFileLoader("btvs", str(SCRIPT)).load_module()

AIRPODS = 6.25   # 16 steps
BOX32 = 3.125    # 32 steps
BOX8 = 12.5      # 8 steps

fails = 0


def check(ok, text):
    global fails
    if not ok:
        fails += 1
    print(f"{'ok  ' if ok else 'FAIL'}  {text}")


# ---------------------------------------------------------------- decide()
# (description, step size, device step, last, cur, expected target)
CASES = [
    # --- AirPods, 5 % steps: deltas taken from a real capture
    ("swipe up   from 60",              5, AIRPODS, 60.0, 66.1,  65.0),
    ("swipe up   from 45",              5, AIRPODS, 45.0, 51.2,  50.0),
    ("swipe down from 65",              5, AIRPODS, 65.0, 59.1,  60.0),
    ("swipe down from 35",              5, AIRPODS, 35.0, 28.3,  30.0),
    ("swipe from an off-grid value",    5, AIRPODS, 65.35, 59.1, 60.0),
    # Keyboard: Plasma sets exactly +/-5 %, so target == cur, no double step
    ("key up   55->60",                 5, AIRPODS, 55.0, 60.0,  60.0),
    ("key down 60->55",                 5, AIRPODS, 60.0, 55.0,  55.0),
    # Foreign absolute changes must pass through
    ("foreign set 60->50",              5, AIRPODS, 60.0, 50.0,  50.0),
    ("foreign set 60->20",              5, AIRPODS, 60.0, 20.0,  20.0),
    # Ambiguous: -13 % is indistinguishable from two swipes (-12.5 %)
    ("foreign jump 60->47 (ambiguous)", 5, AIRPODS, 60.0, 47.0,  50.0),
    # Noise / our own echo
    ("noise 65->65.35",                 5, AIRPODS, 65.0, 65.35, None),
    ("no change",                       5, AIRPODS, 60.0, 60.0,  None),
    # Two fast swipes coalesced into one event
    ("double swipe up",                 5, AIRPODS, 60.0, 72.5,  70.0),
    ("double swipe down",               5, AIRPODS, 60.0, 47.5,  50.0),
    # Limits
    ("swipe up at maximum",             5, AIRPODS, 100.0, 100.0, None),
    ("swipe up near maximum",           5, AIRPODS, 96.9, 100.0, 100.0),
    ("swipe down at minimum",           5, AIRPODS, 0.0, 0.0,    None),
    ("swipe down near zero",            5, AIRPODS, 3.1, 0.0,    0.0),

    # --- other desktop step sizes
    ("10%: swipe up from 60",           10, AIRPODS, 60.0, 66.1, 70.0),
    ("10%: swipe down from 60",         10, AIRPODS, 60.0, 53.5, 50.0),
    ("10%: swipe from off-grid",        10, AIRPODS, 65.0, 71.1, 80.0),
    ("10%: key up 60->70",              10, AIRPODS, 60.0, 70.0, 70.0),
    # 61 sits exactly between; half_up locks onto 62, one step down -> 60
    ("2%: swipe down from 61",          2, AIRPODS, 61.0, 54.8, 60.0),
    ("2%: swipe up from 60",            2, AIRPODS, 60.0, 66.1, 62.0),

    # --- speaker with 32 steps (3.125 %)
    ("32-step: key up from 60",         5, BOX32, 60.0, 63.1, 65.0),
    ("32-step: key down from 60",       5, BOX32, 60.0, 56.9, 55.0),
    ("32-step: double press up",        5, BOX32, 60.0, 66.3, 70.0),
    # A 10 % foreign jump is no multiple of 3.125 within MAXMULT -> pass through
    ("32-step: foreign jump 60->50",    5, BOX32, 60.0, 50.0, 50.0),

    # --- speaker with 8 steps (12.5 %)
    ("8-step: key up from 50",          5, BOX8, 50.0, 62.5, 55.0),
    ("8-step: key down from 50",        5, BOX8, 50.0, 37.5, 45.0),
]

for desc, step, devstep, last, cur, want in CASES:
    got = m.decide(last, cur, float(step), devstep)
    ok = (got is None and want is None) or (
        got is not None and want is not None and abs(got - want) < 0.01
    )
    check(ok, f"{desc:34s} {last:6.2f} -> {cur:6.2f}  want {want}  got {got}")

print()


# ---------------------------------------------------------------- calibrate()

def feed(deltas, plasma_step=5.0):
    """Feed samples one by one; return the first locked-in device step."""
    samples = []
    for d in deltas:
        found = m.calibrate(d, samples, plasma_step)
        if found:
            return found
    return None


got = feed([6.1, -6.4, 6.2])
check(got is not None and abs(got - 6.25) < 0.3,
      f"AirPods spread calibrates -> {got}")

got = feed([5.9, 6.7, 6.1, 6.4])
check(got is not None and abs(got - 6.25) < 0.4,
      f"wider spread calibrates -> {got}")

got = feed([3.1, 3.2, 3.1])
check(got is not None and abs(got - 3.125) < 0.2,
      f"32-step speaker calibrates -> {got}")

got = feed([5.0, 5.0, 5.0, 5.0, 5.0])
check(got is None, f"keyboard deltas (= desktop step) do NOT calibrate -> {got}")

got = feed([10.0, 10.0, 10.0], plasma_step=10.0)
check(got is None, f"keyboard at a 10 % desktop step does NOT calibrate -> {got}")

got = feed([0.8, 0.79, 0.8, 0.8])
check(got is None, f"fine-grained device (<1.5 %) is ignored -> {got}")

got = feed([25.0, 25.0, 25.0])
check(got is None, f"jumps that are too large (>20 %) are ignored -> {got}")

got = feed([6.2, 13.0, 2.0, 6.1, 19.0, 6.3])
check(got is not None and abs(got - 6.25) < 0.4,
      f"measurement finds the cluster despite noise -> {got}")

got = feed([6.2, 6.2])
check(got is None, f"two samples are not enough yet -> {got}")

print()


# ---------------------------------------------------------------- misc

check(m.label("AA_BB", "Speaker") == "Speaker (AA_BB)", "label with name")
check(m.label("AA_BB", None) == "AA_BB", "label without name")
check(m.half_up(6.5) == 7 and m.half_up(7.5) == 8, "half_up rounds consistently")
check(abs(m.snap(65, 10) - 70) < 0.01 and abs(m.snap(75, 10) - 80) < 0.01,
      "snap is consistent for exact midpoints")

print()
total = len(CASES) + 9 + 4
print(f"{total - fails}/{total} passed")
raise SystemExit(1 if fails else 0)
