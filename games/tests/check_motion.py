"""Observe real intermediate frames; compare the settled state to rule replay."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "native"))
from checks import Model, assert_state
from machine import KEYS, Machine, lib


def check(name, setup, action, rom=None, capture=None):
    m = Machine(name, rom=rom)
    model = Model(name)
    m.action(5)
    model.s.action = 5
    for a in setup:
        m.action(a)
        model.action(a)
    if capture:
        m.capture(capture / f"{name}-before.png")
    states = []
    lib.key(m.p, *KEYS[action], 1)
    m.until("DISPATCH")
    model.action(action)
    while True:
        event = lib.until_either(
            m.p, m.sym["N_ANIMATE"], m.sym["FRAME_READY"], 12_000_000
        )
        assert event, name
        if event == 2:
            break
        m.until("MOTION_VISIBLE")
        assert m.get("MOTION_ACTIVE") == 1
        states.append((lib.clocks(m.p), m.read(0xC100, 768)))
        if capture:
            m.capture(capture / f"{name}-{len(states)}.png")
        lib.key(m.p, *KEYS[action], 0)
    lib.key(m.p, *KEYS[action], 0)
    m.until("INPUT_DONE")
    assert_state(m, model)
    if capture:
        m.capture(capture / f"{name}-after.png")
    assert states and len({screen for _, screen in states}) >= min(2, len(states)), name
    assert len({screen for _, screen in states} | {m.read(0xC100, 768)}) >= 2, name
    for (a, _), (b, _) in zip(states, states[1:]):
        assert b - a > 14900 * 2, (name, "Intermediate frame not held")
    assert m.get("MOTION_ACTIVE") == 0 and m.get("KEY_PENDING") == 0
    print(
        f"PASS: {name}, {len(states)} intermediate frames, settled rules and input isolation"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        assert args.rom, "Public images require an owned BASIC ROM"
        args.capture.mkdir(parents=True, exist_ok=True)
    options = {
        "rom": args.rom.read_bytes() if args.rom else None,
        "capture": args.capture,
    }
    root = Path(__file__).resolve().parents[1]
    for name in ("frost_steps", "gravity_well"):
        route = json.loads((root / name / "solutions.json").read_text())[0]
        check(name, [], route[0], **options)
    check("seed_merge", [], 3, **options)
    check("quiet_route", [], 4, **options)
    check("prism_trace", [2, 2, 2, 4, 4], 5, **options)
    check("peg_garden", [1, 1, 5, 2, 2], 5, **options)
