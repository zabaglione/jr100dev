"""Cycle-based timing, held input, permanent flags, hazards, and gates."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from replay import route

for busy in (False, True):
    m = Machine("loop_ten")
    m.action(5)
    lib.poke(m.p, m.sym["FLAGS"], 0x25)
    lib.poke(m.p, m.sym["FLAGS"] + 1, 0x02)
    start = lib.clocks(m.p)
    if busy:
        lib.key(m.p, 2, 1, 1)
    m.until("TIMER_EXPIRED", 10_000_000)
    elapsed = (lib.clocks(m.p) - start) / 894000
    assert 9.98 <= elapsed <= 10.04, elapsed
    assert int.from_bytes(m.read("CLOCK_MAX", 2), "big") < 65536
    lib.key(m.p, 2, 1, 0)
    m.until("LOOP_STARTED")
    m.until("INPUT_DONE")
    assert m.get("ROOM") == 0 and (m.get("PLAYER_X"), m.get("PLAYER_Y")) == (2, 4)
    assert m.read("FLAGS", 2) == bytes([0x25, 0x02]) and m.get("LOOPS") == 2
    print(
        f'PASS: ten-second expiry {elapsed:.4f} s, {"held movement and SFX" if busy else "idle"}'
    )
# Held directions repeat, without requiring rapid manual tapping.
m = Machine("loop_ten")
m.action(5)
lib.key(m.p, 2, 1, 1)
lib.ticks(m.p, 750_000)
lib.key(m.p, 2, 1, 0)
m.until("INPUT_DONE")
assert m.get("PLAYER_Y") == 1
# A closed gate rejects passage; a lit seal opens it and survives moving rooms.
m = Machine("loop_ten")
m.action(5)
for a in route(0, (2, 4), (12, 4)):
    m.action(a)
m.action(5)
assert m.get("FLAGS") == 1
for a in route(0, (m.get("PLAYER_X"), m.get("PLAYER_Y")), (15, 4), 0, True):
    m.action(a)
assert m.get("ROOM") == 1 and m.get("FLAGS") == 1
# Fixture places the player at a closed gate without changing its lock state.
lib.poke(m.p, m.sym["PLAYER_X"], 14)
lib.poke(m.p, m.sym["PLAYER_Y"], 4)
m.action(4)
assert m.get("ROOM") == 1 and m.get("PLAYER_X") == 14
# The starting anchor selects the first missing persistent seal.
m.action(6)
m.action(5)
assert m.get("ROOM") == 1
# Hazard collision rewinds and keeps already collected seals.
lib.poke(m.p, m.sym["MAP"] + 4 * 16 + 3, 5)
lib.poke(m.p, m.sym["PLAYER_X"], 2)
lib.poke(m.p, m.sym["PLAYER_Y"], 4)
m.action(4)
assert m.get("ROOM") == 0 and m.get("FLAGS") == 1
# Exercise carry across the 16-bit time accumulator with a bounded delayed poll.
m = Machine("loop_ten")
m.action(5)
m.until("CLOCK_SERVICE")
now = (m.get(0xC809) << 8) | m.get(0xC808)
previous = (now + 60_000) & 65535
for name, value in [("CLOCK_PREV", previous), ("CLOCK_ACC", 14899)]:
    lib.poke(m.p, m.sym[name], value >> 8)
    lib.poke(m.p, m.sym[name] + 1, value & 255)
old = m.get("TICK")
m.until("CLOCK_DONE")
assert (m.get("TICK") - old) & 255 == 5
assert int.from_bytes(m.read("CLOCK_ACC", 2), "big") < 14900
print(
    "PASS: held movement, persistent flags, open/closed gate, anchor, hazards, 17-bit timer carry"
)
