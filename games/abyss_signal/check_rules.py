"""Explicit boundary fixtures run the actual program's input path."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from model import State, advance
from replay import FIELDS, act, compare


def scenario(s, action):
    m = Machine("abyss_signal")
    m.action(5)
    for field, name in FIELDS.items():
        lib.poke(m.p, m.sym[name], getattr(s, field))
    act(m, action, False)
    expected = advance(s, action)
    compare(m, expected)
    return m, expected


# Rock, exhausted oxygen, one remaining hull, all current directions, and blocked current.
for s, a in [
    (State(x=1), 3),
    (State(oxygen=1), 4),
    (State(x=1, hull=1), 3),
    (State(x=14, y=7), 7),
    (State(x=27, y=18), 7),
    (State(x=20, y=26), 7),
    (State(x=4, y=8), 7),
    (State(x=20, y=7), 7),
    (State(x=22, y=16, hull=1, grace=0), 7),
    (State(x=22, y=16, grace=3), 7),
    (State(flags=31, x=3, y=2, oxygen=1), 3),
    (State(flags=31, x=3, y=2, oxygen=2), 3),
]:
    scenario(s, a)
# Sonar lasts six subsequent actions; quiet mode slows the hunter but costs extra oxygen.
for s, a in [
    (State(), 8),
    (State(quiet=1, turn=1), 7),
    (State(quiet=1, turn=3), 7),
    (State(sight=1, noise=1), 7),
    (State(), 10),
    (State(x=7, y=5), 9),
    (State(x=7, y=5, flags=1), 9),
    (State(), 9),
]:
    scenario(s, a)
# Menus and idle consume no oxygen or world turns.
m = Machine("abyss_signal")
m.action(5)
old = m.read("PLAYER_X", 14)
m.action(5, True)
m.action(2, True)
lib.ticks(m.p, 200_000)
assert m.read("PLAYER_X", 14) == old
m.action(6)
assert m.get("MODE") == 1
# Photos cannot be harvested repeatedly. Closing a photo is free.
m, s = scenario(State(x=7, y=5), 9)
before = m.get("OXYGEN")
m.action(5)
act(m, 9, False)
assert m.get("SAMPLES") == 1 and m.get("OXYGEN") == before
# Retry clears all survey flags and damage.
m, s = scenario(State(oxygen=1), 4)
m.action(5, True)
m.answer_reset(True, pad=True)
compare(m, State())
# Single-voice title audio is produced without waiting for input.
t = Machine("abyss_signal")
lib.ticks(t.p, 150_000)
assert lib.audio_peak(t.p) > 0
print(
    "PASS: collisions, four currents, oxygen, hull, grace, sonar, quiet, records, pause, retry, PCM"
)
