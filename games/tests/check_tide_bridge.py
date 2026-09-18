"""Check line selection, an actual crossing and its delayed clear celebration."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import assert_state, begin
from machine import KEYS, lib
from replay import Player, solve_stage


def check(rom=None, capture=None):
    machine, model = begin("tide_bridge", rom)

    def press(action):
        machine.action(action)
        model.action(action)
        assert_state(machine, model)

    initial_bank = machine.read(0xC000, 256)
    assert initial_bank[32:64] == bytes(v ^ 255 for v in initial_bank[:32])
    assert initial_bank[128:160] == bytes(v ^ 255 for v in initial_bank[96:128])
    for axis in range(2):
        for cursor in range(6):
            assert model.s.axis == axis and model.s.cursor == cursor
            screen = machine.read(0xC100, 768)
            for cell in range(36):
                if cell in (5, 30):
                    continue  # Gate and player remain legible over the line.
                chosen = (cell // 6 if axis == 0 else cell % 6) == cursor
                tile = (4 if model.b[cell] else 1) if chosen else model.b[cell]
                x, y = 2 + cell % 6 * 2, 5 + cell // 6 * 2
                assert screen[y * 32 + x] == 128 + tile * 4
            if capture and cursor == 2:
                machine.capture(capture / f"selection-{axis}.png")
            press(2)
        press(4)
    assert model.s.moves == 0

    # Obtain the existing input-only solution, then observe its final operation.
    player = Player("tide_bridge", rom=rom, pad=False)
    plan = []
    original_press = player.press

    def record(action):
        plan.append(action)
        original_press(action)

    player.press = record
    solve_stage(player)
    assert player.s.mode == 2 and plan[-1] == 5
    machine, model = begin("tide_bridge", rom)
    for action in plan[:-1]:
        press(action)
    slots = json.loads((machine.directory / "build/state_slots.json").read_text())
    fields = ("pos", "origin", "half", "hop", "facing", "arrived")
    frames = []
    banks = set()
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
        assert machine.get("MODE") == 1  # Only clear after the celebration.
        values = tuple(machine.get(slots[f"s.{field}"]) for field in fields)
        frames.append(values)
        current = machine.read(0xC000, 256)
        assert current[:64] == initial_bank[:64]
        assert current[96:] == initial_bank[96:]
        banks.add(current[64:96])
        if capture:
            machine.capture(capture / f"crossing-{len(frames):02}.png")
        lib.key(machine.p, *KEYS[5], 0)
        if len(frames) == 2:
            lib.key(machine.p, *KEYS[4], 1)
        if len(frames) == 4:
            lib.key(machine.p, *KEYS[4], 0)
    lib.key(machine.p, *KEYS[5], 0)
    machine.until("INPUT_DONE")
    assert_state(machine, model)
    assert machine.get("MOTION_ACTIVE") == machine.get("KEY_PENDING") == 0
    assert model.s.mode == 2 and model.s.pos == 5
    assert frames[0][:4] == (30, 30, 0, 0)
    walking = [frame for frame in frames[1:] if not frame[-1]]
    previous = 30
    for half, whole in zip(walking[::2], walking[1::2], strict=True):
        pos, origin, mid, hop, facing, _ = half
        assert mid == 1 and hop == 0 and origin == previous
        assert abs(pos // 6 - origin // 6) + abs(pos % 6 - origin % 6) == 1
        assert model.b[pos] or pos == 5
        assert whole == (pos, origin, 0, 0, facing, 0)
        previous = pos
    assert previous == 5
    cheers = [frame for frame in frames if frame[-1]]
    assert [(frame[3], frame[4]) for frame in cheers] == [
        (1, 5),
        (0, 6),
        (1, 5),
        (0, 6),
        (0, 5),
    ]
    assert len(banks) >= 4 and lib.audio_peak(machine.p) > 0
    print(
        "PASS: tide_bridge, 12 line selections, half-cell crossing, four-slot actor, celebration before clear and input isolation"
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
