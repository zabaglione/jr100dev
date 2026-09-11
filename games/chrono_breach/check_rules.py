"""Behavior checks exercise real input and program bytes, with explicit fixtures."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from replay import play_action

m = Machine()
m.action(5)
# Idle is frozen while the title/game audio clock continues.
tick = m.get("TICK")
turn = m.get("TURNS")
lib.ticks(m.p, 150_000)
assert m.get("TICK") != tick and m.get("TURNS") == turn
# A held key creates one action, then requires a release.
lib.key(m.p, 1, 0, 1)
m.until("DISPATCH")
m.until("FRAME_READY")
x = m.get("PLAYER_X")
turn = m.get("TURNS")
lib.ticks(m.p, 100_000)
assert m.get("PLAYER_X") == x and m.get("TURNS") == turn
lib.key(m.p, 1, 0, 0)
for _ in range(3):
    m.until("INPUT_DONE")
    if not m.get("KEY_LAST"):
        break
# Walking into the left border changes aim but consumes no action.
m.action(3)
assert m.get("TURNS") == turn and m.get("PLAYER_X") == 1
# Menu navigation and aiming never advance enemy time.
state = m.read("ENEMIES", 80)
turn = m.get("TURNS")
m.action(5)
m.action(4)
m.action(4)
assert m.read("ENEMIES", 80) == state and m.get("TURNS") == turn
m.action(6)
assert m.get("MODE") == 1
# Retry restores exact authored initial state.
m.action(5)
m.action(2)
m.action(2)
m.action(5)
m.answer_reset(True)
assert (m.get("PLAYER_X"), m.get("PLAYER_Y"), m.get("TURNS"), m.get("AMMO")) == (
    2,
    4,
    0,
    2,
)
# Shooting empty floor consumes ammunition; the third shot does not advance time.
play_action(m, 9, False)
play_action(m, 9, False)
assert m.get("AMMO") == 0
turn = m.get("TURNS")
m.action(8)
assert m.get("TURNS") == turn
# Wait in the first firing lane until death; retry works via pad alone.
for _ in range(12):
    if m.get("MODE") == 3:
        break
    m.action(7)
assert m.get("MODE") == 3 and m.get("DEATHS") == 1
m.action(5, pad=True)
m.answer_reset(True, pad=True)
assert m.get("MODE") == 1 and m.get("DEATHS") == 1 and m.get("TURNS") == 0
# A live lethal effect may not block movement or the input scan.
assert m.get("SFX_PRIORITY") == 0
m.action(7)
assert m.get("MODE") == 1
# The title music progresses while no game input is given, producing PCM.
t = Machine()
before = t.read("BGM_PTR", 2)
lib.ticks(t.p, 900_000)
assert t.read("BGM_PTR", 2) != before and lib.audio_peak(t.p) > 0
print(
    "PASS: frozen time, held input, wall, free aim, retry, empty ammo, death, title PCM"
)
# A short second tap during rendering is captured without advancing it early.
b = Machine()
b.action(5)
lib.key(b.p, 2, 1, 1)
b.until("DISPATCH")
b.until("DRAW_GAME")
lib.key(b.p, 2, 1, 0)
lib.ticks(b.p, 20_000)
lib.key(b.p, 1, 2, 1)
lib.ticks(b.p, 20_000)
lib.key(b.p, 1, 2, 0)
b.until("DISPATCH")
assert b.get("KEY_PENDING") == 0
b.until("FRAME_READY")
assert (b.get("PLAYER_X"), b.get("PLAYER_Y"), b.get("TURNS")) == (3, 3, 2)
print("PASS: input captured during rendering")
