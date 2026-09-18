"""Scarce water, partial growth, optional harvest, carryover and real-key runs."""

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, action, assert_state, lib, render_bounds
from replay import Player, sand_irrigate


def water_left(r):
    return r.s.water + r.s.tank + r.s.flow + sum(r.c[:6]) + r.s.waste


def model_choices():
    for amount, harvest, grown, lost in (
        (1, 0, (1, 0), 0),
        (2, 3, (2, 0), 0),
        (3, 3, (2, 0), 1),
        (7, 11, (2, 4), 1),
        (9, 11, (2, 4), 3),
    ):
        r = Model("sand_rescue")
        for _ in range(amount * 5):
            r.tick()
        assert r.s.tank == amount
        r.action(5)
        for _ in range(20):
            if not r.s.flow:
                break
            r.tick()
            render_bounds(r)
            assert water_left(r) == 108
        assert (r.s.score, (r.c[0], r.c[3]), r.s.waste) == (harvest, grown, lost)
        assert r.s.flow == 0

    r = Model("sand_rescue")
    r.action(1)  # Cannot bank an unfulfilled target.
    r.action(5)  # Cannot pour an empty tank.
    assert r.s.mode == 1 and r.s.flow == 0
    for _ in range(50):
        r.tick()
    assert (r.s.tank, r.s.waste, r.s.water) == (9, 1, 98)
    while r.s.water:
        r.tick()
    assert r.s.mode == 1  # Water in the tank remains playable after the source ends.
    r.action(5)
    while r.s.flow:
        r.tick()
    assert r.s.mode == 3 and water_left(r) == 108

    outcomes = []
    for extra in (0, 3):
        r = Model("sand_rescue")

        def choice(field, target, r=r):
            while getattr(r.s, field) != target:
                r.action(4)

        p = SimpleNamespace(r=r, s=r.s, wait=r.tick, press=r.action, choice=choice)
        sand_irrigate(p, extra)
        assert r.s.mode == 2 and water_left(r) == 108
        outcomes.append((r.s.total, r.s.water + r.s.tank))
    assert outcomes == [(14, 99), (17, 97)], outcomes


def native_campaign(rom=None, capture=None):
    p = Player("sand_rescue", rom=rom, pad=False)
    writes = lib.host_mutations(p.m.p)
    water, previous_score = 108, 0
    for level in range(6):
        assert p.s.level == level and p.s.water == water
        assert p.s.total == previous_score
        sand_irrigate(p, 3 if level == 0 else 0)
        assert p.s.mode == 2 and p.s.score >= p.s.quota
        assert water_left(p.r) == water
        water = p.s.water + p.s.tank
        previous_score = p.s.total
        if capture:
            p.m.capture(capture / f"field-{level + 1}-clear.png")
        assert p.next() == (level < 5)
    assert (p.s.total, water) == (129, 13), (p.s.total, water)
    assert lib.host_mutations(p.m.p) == writes
    assert lib.audio_peak(p.m.p) > 0
    assert_state(p.m, p.r)

    # Cancelling reset keeps the scarce water; accepting starts a new campaign.
    p = Player("sand_rescue", rom=rom, pad=False)
    sand_irrigate(p)
    p.next()
    initial = p.s.water
    action(p.m, p.r, 6, confirm=False)
    assert p.s.level == 1 and p.s.water == initial
    action(p.m, p.r, 6, confirm=True)
    assert p.s.level == 0 and p.s.water == 108 and p.s.total == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        args.capture.mkdir(parents=True, exist_ok=True)
    model_choices()
    native_campaign(args.rom.read_bytes() if args.rom else None, args.capture)
    print(
        "PASS: six fields, water conservation, small/full pours, sand loss, overflow, optional crops, carryover, reset and input-only native completion"
    )
