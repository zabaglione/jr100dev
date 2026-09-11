"""Explicit CPU fixtures cover armor, every pickup, expiry, drone and bomb rules."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "native"))
from checks import begin, lib, tick


def fixture(**fields):
    m, r = begin("brick_pulse")
    slots = json.loads((m.directory / "build/state_slots.json").read_text())
    for field, value in fields.items():
        setattr(r.s, field, value)
        lib.poke(m.p, m.sym[slots["s." + field]], value)
    return m, r


def check():
    for kind in (1, 2, 3):
        m, r = fixture(item=kind, ix=14, iy=16, clock=1)
        tick(m, r)
        assert r.s.item == 0 and r.s.caught == 1
        assert (r.s.width == 10, r.s.slow == 96, r.s.guard == 1)[kind - 1]
    m, r = fixture(wide=1, width=10)
    tick(m, r)
    assert r.s.width == 6 and r.s.wide == 0
    m, r = fixture(slow=5, clock=0)
    old = r.s.x, r.s.y
    tick(m, r)
    assert (r.s.x, r.s.y) == old
    m, r = fixture(guard=1, x=1, y=15, dy=1)
    tick(m, r)
    assert r.s.hp == 3 and r.s.dy == 0 and r.s.guard == 0
    for guard in (0, 1):
        m, r = fixture(guard=guard, bomb=16, bx=14, clock=1)
        tick(m, r)
        assert r.s.hp == 3 and r.s.bomb == 0
        assert r.s.guard == 0
        assert r.s.width == (6 if guard else 4)
        assert r.s.jam == (0 if guard else 48)
    m, r = fixture(jam=1, width=4, paddle=26)
    tick(m, r)
    assert r.s.width == 6 and r.s.paddle == 24
    m, r = fixture(enemy=1, ex=14, x=13, y=11, dy=0)
    tick(m, r)
    assert r.s.enemy == 0 and r.s.item == 3
    m, r = fixture(x=0, y=2, dy=0)
    r.b[0] = 3
    lib.poke(m.p, m.sym["B_ARRAY"], 3)
    tick(m, r)
    assert r.b[0] == 2 and r.s.left == 12
    m, r = fixture(left=0, enemy=1)
    tick(m, r)
    assert r.s.mode == 1, "The drone is a required target"
    m, r = fixture(hp=1, x=0, y=15, dy=1)
    tick(m, r)
    assert r.s.mode == 3 and r.s.hp == 0
    print(
        "PASS: armor, three pickups, expiry, slow movement, guard, drone, jam, win and loss boundaries"
    )


if __name__ == "__main__":
    check()
