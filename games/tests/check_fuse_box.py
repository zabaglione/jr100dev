"""Check live hint feedback and both directions of the switch animation."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "native"), str(ROOT / "common")]
from checks import assert_state, begin
from fonts import glyph
from machine import KEYS, lib
from replay import fuse_plan


def hints(machine, model):
    for line in range(5):
        for cells, x, y in (
            ([line * 5 + i for i in range(5)], 2, 5 + line * 3),
            ([i * 5 + line for i in range(5)], 5 + line * 3, 2),
        ):
            target = sum(model.d[i] for i in cells)
            actual = sum(model.b[i] for i in cells)
            slot = (
                10 + target
                if actual == target
                else machine.fonts["game"]["characters"][str(target)]
            )
            assert machine.get(0xC100 + y * 32 + x) == 128 + slot, (
                line,
                x,
                target,
                actual,
            )


def check(rom=None, capture=None):
    machine, model = begin("fuse_box", rom)
    slots = json.loads((machine.directory / "build/state_slots.json").read_text())
    bank = machine.read(0xC000, 256)
    assert bank[80:128] == bytes(
        byte ^ 255 for digit in "012345" for byte in glyph(digit, "panel")
    )
    hints(machine, model)

    def press(action):
        machine.action(action)
        model.action(action)
        assert_state(machine, model)
        hints(machine, model)

    def go(cell):
        while model.s.cursor // 5 != cell // 5:
            press(2 if model.s.cursor // 5 < cell // 5 else 1)
        while model.s.cursor % 5 != cell % 5:
            press(4 if model.s.cursor % 5 < cell % 5 else 3)

    def flip(label):
        turning_on = model.b[model.s.cursor] == 0
        old_bank = machine.read(0xC000, 256)
        phases = []
        if capture:
            machine.capture(capture / f"{label}-before.png")
        lib.key(machine.p, *KEYS[5], 1)
        machine.until("DISPATCH")
        model.action(5)
        while True:
            event = lib.until_either(
                machine.p,
                machine.sym["N_MOTION_ENTER"],
                machine.sym["FRAME_READY"],
                12_000_000,
            )
            assert event
            if event == 2:
                break
            machine.until("MOTION_VISIBLE")
            assert machine.get(slots["s.flipping"]) == 1
            current = machine.read(0xC000, 256)
            assert current[:192] == old_bank[:192] and current[224:] == old_bank[224:]
            phases.append(
                (
                    machine.get(slots["s.flip_frame"]),
                    current[192:224],
                    lib.clocks(machine.p),
                )
            )
            if capture:
                machine.capture(capture / f"{label}-{len(phases)}.png")
            lib.key(machine.p, *KEYS[5], 0)
            if len(phases) == 2:
                lib.key(machine.p, *KEYS[4], 1)
            if len(phases) == 4:
                lib.key(machine.p, *KEYS[4], 0)
        lib.key(machine.p, *KEYS[5], 0)
        machine.until("INPUT_DONE")
        assert [phase for phase, _, _ in phases] == (
            list(range(1, 6)) if turning_on else list(range(5, 0, -1))
        )
        assert len({pose for _, pose, _ in phases}) == 5
        assert all(b[2] - a[2] >= 14900 * 2 for a, b in zip(phases, phases[1:]))
        assert machine.get("MOTION_ACTIVE") == machine.get("KEY_PENDING") == 0
        assert_state(machine, model)
        hints(machine, model)
        if capture:
            machine.capture(capture / f"{label}-after.png")

    go(7)
    flip("switch-on")
    for cell in (6, 8, 9):
        go(cell)
        press(5)  # Row: below target, equal, then above target.
    flip("switch-off")  # Return to equality; its inverse hint must return.
    go(8)
    press(5)  # Below target again; its inverse hint must disappear.
    for cell in (12, 17, 17, 12):
        go(cell)
        press(5)  # Column: equal, over, equal, then under target.
    assert fuse_plan([2, 3, 2, 2, 2], [3, 2, 2, 2, 2])[:3] == [7, 6, 8]
    assert fuse_plan([1, 3, 5, 4, 1], [2, 3, 4, 3, 2])[:5] == [12, 11, 13, 10, 14]
    print(
        "PASS: fuse_box, row/column hints below/equal/over target, five poses both ways, isolated PCG and input, centre-first replay"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        assert args.rom, "Screenshots require the owned BASIC ROM"
        args.capture.mkdir(parents=True, exist_ok=True)
    check(args.rom.read_bytes() if args.rom else None, args.capture)
