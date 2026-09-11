"""Input-only hold/release, short-tap, reversal and physics-progress regression."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import KEYS, PADS, Machine, lib


def check(rom=None):
    slots = json.loads((Path(__file__).parent / "build/state_slots.json").read_text())

    def value(machine, name):
        return machine.get(slots["s." + name])

    def set_direction(machine, direction, down, pad):
        if pad:
            lib.pad(machine.p, PADS[direction] if down else 0)
        else:
            lib.key(machine.p, *KEYS[direction], int(down))

    for pad in (False, True):
        for direction, step, edge in ((3, -2, 0), (4, 2, 24)):
            machine = Machine("brick_pulse", rom)
            machine.action(5)
            machine.action(direction, pad=pad)
            assert value(machine, "paddle") == 12 + step
            lib.ticks(machine.p, 250_000)
            assert value(machine, "paddle") == 12 + step, (
                "Short tap repeats after release"
            )
            start = value(machine, "clock")
            set_direction(machine, direction, True, pad)
            lib.ticks(machine.p, 1_200_000)
            assert value(machine, "paddle") == edge, (
                "Hold must move continuously to the edge"
            )
            assert (value(machine, "clock") - start) & 255 >= 4, (
                "Holding stalls the ball"
            )
            lib.ticks(machine.p, 200_000)
            assert value(machine, "paddle") == edge, "Paddle moved outside the arena"
            set_direction(machine, direction, False, pad)
            opposite = 7 - direction
            set_direction(machine, opposite, True, pad)
            lib.ticks(machine.p, 250_000)
            pos = value(machine, "paddle")
            assert 0 < pos < 24, "Reversal must respond while the ball is moving"
            set_direction(machine, opposite, False, pad)
            machine.until("INPUT_DONE")
            pos = value(machine, "paddle")
            lib.ticks(machine.p, 200_000)
            assert value(machine, "paddle") == pos, "Movement continues after release"
            assert machine.read(0x300, len(machine.code)) == machine.code
            assert lib.min_sp(machine.p) >= 0x3E00
        print(
            f"PASS: {'pad' if pad else 'keyboard'} taps, sustained hold, both bounds, reversal, release and live physics"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    args = parser.parse_args()
    check(args.rom.read_bytes() if args.rom else None)
