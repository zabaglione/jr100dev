"""Check pair motion, live PCG rays, rejected pairs and input isolation."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "native"), str(ROOT / "common")]
from checks import assert_state, begin
from machine import KEYS, lib


def check(rom=None, capture=None):
    machine, model = begin("phase_pairs", rom)
    slots = json.loads((machine.directory / "build/state_slots.json").read_text())
    initial_bank = machine.read(0xC000, 256)
    assert len({initial_bank[i * 16 : (i + 1) * 16] for i in range(10)}) == 10

    def press(action):
        machine.action(action)
        model.action(action)
        assert_state(machine, model)

    def go(cell):
        while model.s.cursor // 4 != cell // 4:
            press(2 if model.s.cursor // 4 < cell // 4 else 1)
        while model.s.cursor % 4 != cell % 4:
            press(4 if model.s.cursor % 4 < cell % 4 else 3)

    def choose(first, second, label, rejected=0):
        go(first)
        press(5)
        expected = {
            cell
            for cell in range(16)
            if abs(cell // 4 - first // 4) + abs(cell % 4 - first % 4) == 1
            and model.b[cell] + model.b[first] == 10
        }
        assert {i for i in range(16) if model.c[i]} == expected
        selected_screen = machine.read(0xC100, 768)
        for cell in range(16):
            x, y = 2 + cell % 4 * 4, 4 + cell // 4 * 4
            if model.b[cell]:
                assert selected_screen[y * 32 + x] == (156 if cell in expected else 148)
                assert selected_screen[(y + 1) * 32 + x + 1] == 128 + model.b[cell] * 2
        if label == "horizontal":
            assert expected == {0, 2}  # Both matching neighbors blink together.
            blink_banks = set()
            board = machine.read("B_ARRAY", 16)
            for _ in range(8):
                lib.ticks(machine.p, 14900 * 8)
                machine.until("INPUT_DONE")
                current = machine.read(0xC000, 256)
                assert current[:224] == initial_bank[:224]
                assert machine.read(0xC100, 768) == selected_screen
                assert machine.read("B_ARRAY", 16) == board
                assert_state(machine, model)
                if capture and current[224:] not in blink_banks:
                    machine.capture(capture / f"hints-{len(blink_banks) + 1}.png")
                blink_banks.add(current[224:])
            assert len(blink_banks) == 2
        go(second)
        old_board = machine.read("B_ARRAY", 16)
        old_left = model.s.left
        if capture:
            machine.capture(capture / f"{label}-before.png")
        phases, banks, frames, positions = [], [], [], []
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
            assert machine.read("B_ARRAY", 16) == old_board
            assert machine.get(slots["s.left"]) == old_left
            current = machine.read(0xC000, 256)
            assert current[:224] == initial_bank[:224]
            phases.append(machine.get(slots["s.merging"]))
            banks.append(current[224:])
            frames.append(machine.read(0xC100, 768))
            positions.append(
                tuple(
                    machine.get(slots[f"s.{axis}"]) for axis in ("ax", "ay", "bx", "by")
                )
            )
            assert machine.get(slots["s.reject"]) == rejected
            if capture:
                machine.capture(capture / f"{label}-{len(phases)}.png")
            lib.key(machine.p, *KEYS[5], 0)
            if len(phases) == 2:
                lib.key(machine.p, *KEYS[4], 1)
            if len(phases) == 4:
                lib.key(machine.p, *KEYS[4], 0)
        lib.key(machine.p, *KEYS[5], 0)
        machine.until("INPUT_DONE")
        assert machine.get("MOTION_ACTIVE") == machine.get("KEY_PENDING") == 0
        assert_state(machine, model)
        assert not any(model.c[:16])
        if rejected:
            assert phases == [0]
            assert machine.read("B_ARRAY", 16) == old_board
            message = "NEIGHBORS ONLY" if rejected == 1 else "SUM MUST BE 10"
            assert frames[0][21 * 32 + 2 : 21 * 32 + 2 + len(message)] == bytes(
                64 if char == " " else ord(char) - 32 for char in message
            )
        else:
            assert phases == [1, 2, 3, 4, 5, 6]
            ax, ay, bx, by = positions[0]
            assert abs(ax - bx) + abs(ay - by) == 2
            assert len(set(banks[2:])) == 4
            assert len(set(frames[:3])) == 3
            cx = machine.get(slots["s.cx"])
            cy = machine.get(slots["s.cy"])
            # The central result has both tall glyphs: 1 followed by 0.
            for dx, value in ((1, 1), (2, 0)):
                assert frames[1][(cy + 1) * 32 + cx + dx] == 128 + value * 2
                assert frames[1][(cy + 2) * 32 + cx + dx] == 129 + value * 2
            assert model.s.left == old_left - 2
        if capture:
            machine.capture(capture / f"{label}-after.png")

    choose(1, 0, "horizontal")
    choose(6, 10, "vertical")
    choose(2, 12, "non-neighbor", rejected=1)
    choose(2, 7, "diagonal", rejected=1)
    choose(8, 9, "wrong-sum", rejected=2)
    # Reproduce the edge-clamping case with a 5 on an actual later board.
    from replay import Player, solve_stage

    player = Player("phase_pairs", rom=rom, pad=False)
    solve_stage(player)
    player.next()
    machine, model = player.m, player.r
    assert model.b[3] == 5 and model.s.level == 1
    choose(3, 3, "same-card", rejected=1)
    print(
        "PASS: phase_pairs, all matching neighbors blink, horizontal/vertical fusion into 10, isolated PCG, input isolation and rejected pairs"
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
