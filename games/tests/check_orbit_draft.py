"""Check celestial card travel, line scoring and isolated resonance frames."""

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, assert_state, begin
from machine import KEYS, lib

LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def oracle(board):
    lines = [
        line
        for line in LINES
        if board[line[0]] != 255 and len({board[i] for i in line}) == 1
    ]
    return len(lines) * 3, {i for line in lines for i in line}


def check(rom=None, capture=None):
    model = Model("orbit_draft")
    rng = random.Random(71)
    boards = []
    for line in LINES:
        board = [255] * 9
        for i in line:
            board[i] = 2
        boards.append(board)
    for _ in range(100):
        board = [i // 3 for i in range(9)]
        rng.shuffle(board)
        for i in rng.sample(range(9), rng.randrange(10)):
            board[i] = 255
        boards.append(board)
    for board in boards:
        model.init()
        model.b[:9] = bytes(board)
        expected, marked = oracle(board)
        model.env["evaluate"]()
        assert (model.s.score, model.s.gain) == (expected, expected)
        assert {i for i, value in enumerate(model.c[:9]) if value} == marked
        model.env["evaluate"]()
        assert model.s.gain == 0 and not any(model.d)

    machine, model = begin("orbit_draft", rom)
    slots = json.loads((machine.directory / "build/state_slots.json").read_text())
    bank = machine.read(0xC000, 256)
    assert len({bank[i * 32 : (i + 1) * 32] for i in range(3)}) == 3
    matches = 0
    for turn in range(9):
        kind = model.s.card
        target = kind * 3 + turn // 3
        while model.s.cursor != target:
            cursor = model.s.cursor
            action = (
                (1 if target // 3 < cursor // 3 else 2)
                if target // 3 != cursor // 3
                else (3 if target % 3 < cursor % 3 else 4)
            )
            machine.action(action)
            model.action(action)
            assert_state(machine, model)
        before = bytes(model.b)
        prior_score = model.s.score
        model.action(5)
        expected_score, expected_marked = oracle(model.b)
        assert model.s.score == expected_score
        motions, glows = [], []
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
            assert machine.get("MODE") == 1
            assert machine.get(slots["s.card"]) == kind, (
                "NEXT advanced before effects ended"
            )
            now_bank = machine.read(0xC000, 256)
            assert now_bank[:96] == bank[:96] and now_bank[128:] == bank[128:]
            if machine.get(slots["s.flying"]):
                assert machine.read("B_ARRAY", 128) == before
                assert machine.get(slots["s.placed"]) == turn
                assert machine.get(slots["s.score"]) == prior_score
                motions.append((machine.get(slots["s.fx"]), machine.get(slots["s.fy"])))
            else:
                assert machine.read("B_ARRAY", 128) == bytes(model.b)
                assert machine.get(slots["s.placed"]) == turn + 1
                assert machine.get(slots["s.score"]) == expected_score
                assert {
                    i for i, value in enumerate(machine.read("C_ARRAY", 9)) if value
                } == expected_marked
                glow = machine.get(slots["s.glow"])
                glows.append(glow)
                screen = machine.read(0xC100, 768)
                for i in range(9):
                    if model.b[i] == 255:
                        continue
                    x, y = 3 + i % 3 * 6, 6 + i // 3 * 5
                    tile = 3 if glow and model.d[i] else model.b[i]
                    assert screen[y * 32 + x] == 128 + tile * 4
            if capture and turn == 6:
                machine.capture(
                    capture / f"travel-{len(motions):02}-glow-{len(glows):02}.png"
                )
            lib.key(machine.p, *KEYS[5], 0)
            if len(motions) == 2:
                lib.key(machine.p, *KEYS[4], 1)
            if len(motions) == 4:
                lib.key(machine.p, *KEYS[4], 0)
        lib.key(machine.p, *KEYS[5], 0)
        machine.until("INPUT_DONE")
        assert_state(machine, model)
        assert motions[0] == (24, 5)
        assert motions[-1] == (3 + target % 3 * 6, 6 + target // 3 * 5)
        assert len(set(motions)) == 5
        assert glows == ([0, 1, 2, 3, 0] if model.s.gain else [0])
        matches += int(model.s.gain > 0)
        assert machine.get("MOTION_ACTIVE") == machine.get("KEY_PENDING") == 0
    assert matches == 3 and model.s.score == 9 and model.s.mode == 2
    assert lib.audio_peak(machine.p) > 0
    print(
        "PASS: orbit_draft, eight scoring directions, five-step card travel, three resonance lines, four-slot flashes, next-card delay and input isolation"
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
