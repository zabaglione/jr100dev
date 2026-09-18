"""Continuous steering, mandatory jumps, solid geometry and six input-only runs."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import KEYS, Machine, Model, lib, render_bounds
from replay import Player, solve_stage


def constraints():
    r = Model("gate_runner")
    for x, hit in ((9, 0), (10, 1), (19, 1), (20, 0)):
        r.s.x = x
        assert r.env["collides"](0) == hit
    r.s.x = 15
    r.b[0], r.b[1], r.b[2] = 2, 2, 30
    for air, hit in ((0, 2), (1, 2), (2, 2), (3, 0), (4, 0), (6, 0), (7, 2), (8, 2)):
        r.s.air = air
        assert r.env["collides"](0) == hit
    r.b[0] = 3
    r.s.air = 0
    assert r.env["collides"](0) == 0
    r.action(5)
    r.tick()
    r.action(5)
    assert r.s.air == 7  # A second press cannot stretch a jump indefinitely.
    r.tick()
    assert r.env["collides"](0) == 3
    old = r.s.x
    r.action(4)
    assert r.s.x == old + 1 and r.s.air > 0
    for depth in range(20):
        left = r.env["project"](2, depth)
        right = r.env["project"](30, depth)
        assert left == 16 - r.env["widths"][depth]
        assert right == 16 + r.env["widths"][depth]
        r.s.age = depth
        render_bounds(r)


def physical_routes():
    # Independent reachability: at most one one-character move OR one jump per
    # clock step. Proves a fast host key loop is not needed for a perfect run.
    for level in range(6):
        r = Model("gate_runner")
        r.init(level)
        states = {(15, 0): 0}
        forced = 0
        heights = (0, 0, 1, 2, 3, 3, 2, 1, 0)
        for wave in range(r.s.limit):
            r.env["load_gate"](wave, 0)
            objects = [tuple(r.b[offset : offset + 3]) for offset in (0, 3)]
            forced += any(
                kind == 2 and left == 2 and right == 30 for kind, left, right in objects
            )
            for step in range(18 * r.s.speed):
                next_states = {}
                for (x, air), coins in states.items():
                    for key in (0, 3, 4, 5):
                        nx = (
                            max(2, x - 1)
                            if key == 3
                            else min(28, x + 1)
                            if key == 4
                            else x
                        )
                        na = 8 if key == 5 and air == 0 else air
                        na = max(0, na - 1)
                        score = coins
                        if step + 1 == 18 * r.s.speed:
                            if any(
                                nx + 2 > left
                                and nx < right
                                and (
                                    kind == 1
                                    or kind == 2
                                    and heights[na] < 2
                                    or kind == 3
                                    and heights[na] >= 2
                                )
                                for kind, left, right in objects
                            ):
                                continue
                            score += (
                                abs(nx - r.b[6]) <= 1 and (heights[na] >= 2) == r.b[7]
                            )
                        next_states[nx, na] = max(score, next_states.get((nx, na), -1))
                states = next_states
                assert states, (level, wave, step, "No physically reachable safe route")
        assert forced == 3 and max(states.values()) == r.s.limit, (
            level,
            forced,
            max(states.values()),
        )


def native_runs(rom=None, capture=None):
    p = Player("gate_runner", rom=rom, pad=False)
    writes = lib.host_mutations(p.m.p)
    for level in range(6):
        solve_stage(p)
        assert (p.s.level, p.s.mode, p.s.hp, p.s.coins) == (level, 2, 3, p.s.limit)
        if capture:
            p.m.capture(capture / f"course-{level + 1}-clear.png")
        assert p.next() == (level < 5)
    assert lib.host_mutations(p.m.p) == writes and lib.audio_peak(p.m.p) > 0

    m = Machine("gate_runner", rom=rom)
    m.action(5)
    slots = json.loads((ROOT / "gate_runner/build/state_slots.json").read_text())
    original = m.read(0xC000, 256)
    visited, poses = set(), set()
    for key in (3, 4):
        lib.key(m.p, *KEYS[key], 1)
        for _ in range(30):
            m.until("FN_TICK")
            m.until("FRAME_READY")
            visited.add(m.get(slots["s.x"]))
            bank = m.read(0xC000, 256)
            assert bank[:64] == original[:64] and bank[96:] == original[96:]
            poses.add(bank[64:96])
        lib.key(m.p, *KEYS[key], 0)
        m.until("INPUT_DONE")
    assert visited == set(range(2, 29)) and len(poses) >= 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        args.capture.mkdir(parents=True, exist_ok=True)
    constraints()
    physical_routes()
    native_runs(args.rom.read_bytes() if args.rom else None, args.capture)
    print(
        "PASS: 27 horizontal positions, bounded jumps, wall/pit/beam geometry, 6 physically reachable perfect courses, mandatory jumps, PCG ownership and native key-only play"
    )
