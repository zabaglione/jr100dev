"""Path rejection, undo, reset, pause and execution boundaries."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from replay import LEVELS, finish

m = Machine("trace_blade")
m.action(5)
m.action(3)
assert m.get("PATH_LEN") == 0 and m.get("ERROR") == 1
m.action(8)
assert m.get("MODE") == 1 and m.get("PATH_LEN") == 0
solution = LEVELS[0]["solution"]
a = solution[0]
m.action(a)
old = m.read("VISITED", 108)
m.action({1: 2, 2: 1, 3: 4, 4: 3}[a])
assert m.get("PATH_LEN") == 1 and m.read("VISITED", 108) == old
m.action(6)
assert m.get("PATH_LEN") == 0 and m.get("PLAYER_X") == m.get("PLAYER_Y") == 1
# Every marked target can be unmarked by undo, including the gate endpoint.
for a in solution:
    m.action(a)
assert m.get("MARKED") == m.get("TARGETS")
for _ in solution:
    m.action(6)
assert m.get("MARKED") == 0 and m.get("PATH_LEN") == 0
# Menu navigation and idle do not change the plan.
m.action(solution[0])
old = m.read("PATH", 70)
m.action(5, True)
m.action(2, True)
lib.ticks(m.p, 100_000)
assert m.read("PATH", 70) == old
m.action(5, True)
assert m.get("PATH_LEN") == 0 and m.get("MODE") == 1
# Reset and title are reachable through the one-button menu.
m.action(solution[0])
m.action(5, True)
m.action(2, True)
m.action(2, True)
m.action(5, True)
assert m.get("PATH_LEN") == m.get("MARKED") == 0
for a in solution:
    m.action(a)
m.action(8)
finish(m)
assert m.get("COMBO") == m.get("TARGETS")
m.action(5)
assert m.get("LEVEL") == 1 and m.get("MODE") == 1
print(
    "PASS: walls, repeated cell, incomplete cut, undo, marked targets, pause, reset, animation and next level"
)
