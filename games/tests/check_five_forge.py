"""Observe stone landings and winning lines before the native result message."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, assert_state, begin
from machine import KEYS, lib


def winning_cells(board, pos, mark):
    result = set()
    x, y = pos % 8, pos // 8
    for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
        cells = {pos}
        for sign in (-1, 1):
            xx, yy = x + dx * sign, y + dy * sign
            while 0 <= xx < 8 and 0 <= yy < 8 and board[yy * 8 + xx] == mark:
                cells.add(yy * 8 + xx)
                xx += dx * sign
                yy += dy * sign
        if len(cells) >= 5:
            result |= cells
    return result


def check(rom=None, capture=None):
    # This independent Cartesian oracle rejects row wrapping, short chains,
    # and interrupted lines; it also covers overlines and crossing wins.
    model = Model("five_forge")
    patterns = (
        ((24, 25, 26, 27), 28),
        ((3, 11, 19, 27), 35),
        ((0, 9, 18, 27), 36),
        ((7, 14, 21, 28), 35),
        ((24, 25, 26, 28, 29), 27),
        ((26, 27, 29, 30, 12, 20, 36, 44), 28),
        ((5, 6, 7, 8), 9),
        ((24, 25, 26), 27),
        ((24, 25, 27, 29), 28),
    )
    for mark in (1, 2):
        for stones, pos in patterns:
            model.init()
            for cell in (*stones, pos):
                model.b[cell] = mark
            expected = winning_cells(model.b, pos, mark)
            model.env["complete"](pos, mark)
            assert {i for i, value in enumerate(model.d) if value} == expected
            assert model.s.mode == ((2 if mark == 1 else 3) if expected else 1)

    # Fixtures exercise both winners through the actual RETURN dispatch.
    # Only the separate input-only replay produces published screenshots.
    for case, (stones, final) in enumerate(patterns[:6]):
        for mark in (1, 2):
            machine, model = begin("five_forge", rom)
            slots = json.loads(
                (machine.directory / "build/state_slots.json").read_text()
            )
            for cell in stones:
                model.b[cell] = mark
                lib.poke(machine.p, machine.sym["B_ARRAY"] + cell, mark)
            model.s.cursor = final if mark == 1 else 63
            model.s.stones = len(stones)
            for field in ("cursor", "stones"):
                lib.poke(
                    machine.p, machine.sym[slots[f"s.{field}"]], getattr(model.s, field)
                )
            bank = machine.read(0xC000, 256)
            board_before = bytes(model.b)
            model.action(5)
            expected = winning_cells(model.b, model.s.last, mark)
            assert expected and model.s.winner == mark
            frames, blink, timestamps = [], [], []
            lib.key(machine.p, *KEYS[5], 1)
            machine.until("DISPATCH")
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
                assert machine.get("MODE") == 1, (
                    "Result appeared before line flashing finished"
                )
                current_bank = machine.read(0xC000, 256)
                assert (
                    current_bank[:96] == bank[:96] and current_bank[128:] == bank[128:]
                )
                placing = machine.get(slots["s.placing"])
                if placing:
                    pose = machine.get(slots["s.pose"])
                    frames.append(pose)
                    address = machine.sym["FACE_3_FRAMES"] + (pose - 1) * 32
                    assert current_bank[96:128] == machine.read(address, 32)
                    if placing == 1:
                        assert sum(
                            v == 2 for v in machine.read("B_ARRAY", 64)
                        ) == board_before.count(2)
                else:
                    hidden = machine.get(slots["s.blink"])
                    blink.append(hidden)
                    timestamps.append(lib.clocks(machine.p))
                    assert machine.read("B_ARRAY", 128) == bytes(model.b)
                    assert {
                        i
                        for i, value in enumerate(machine.read("D_ARRAY", 64))
                        if value
                    } == expected
                    screen = machine.read(0xC100, 768)
                    for i in range(64):
                        x, y = 1 + i % 8 * 2, 4 + i // 8 * 2
                        shape = 0 if hidden and i in expected else model.b[i]
                        assert screen[y * 32 + x] == 128 + shape * 4
                if capture and case == 0 and mark == 1:
                    machine.capture(
                        capture / f"pose-{len(frames):02}-blink-{len(blink):02}.png"
                    )
                lib.key(machine.p, *KEYS[5], 0)
                if len(frames) == 2:
                    lib.key(machine.p, *KEYS[4], 1)
                if len(frames) >= 4:
                    lib.key(machine.p, *KEYS[4], 0)
            lib.key(machine.p, *KEYS[5], 0)
            machine.until("INPUT_DONE")
            assert_state(machine, model)
            assert frames == list(range(1, 5 if mark == 1 else 9))
            assert blink == [1, 0, 1, 0, 1, 0, 0]
            assert lib.clocks(machine.p) - timestamps[0] >= 14900 * 108
            assert machine.get("KEY_PENDING") == machine.get("MOTION_ACTIVE") == 0
            assert lib.audio_peak(machine.p) > 0
    print(
        "PASS: five_forge, four-frame landings, four-slot animation, both winners in four directions, overlines/crossings, line-only flashing before result and input isolation"
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
