"""Check readable card faces, hand classification, swap and scoring holds."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, assert_state, begin
from machine import KEYS, lib
from replay import Player, solve_stage


def check(rom=None, capture=None):
    model = Model("chain_suit")
    cases = (
        ([1, 2, 3, 4, 5], 0, 3, [0, 0, 0, 0, 0]),
        ([1, 1, 3, 4, 5], 1, 8, [1, 1, 0, 0, 0]),
        ([1, 1, 3, 3, 5], 2, 16, [1, 1, 1, 1, 0]),
        ([1, 1, 1, 3, 5], 3, 16, [1, 1, 1, 0, 0]),
        ([1, 1, 1, 3, 3], 4, 16, [1, 1, 1, 1, 1]),
        ([1, 1, 1, 1, 5], 5, 16, [1, 1, 1, 1, 0]),
        ([1, 1, 1, 1, 1], 6, 16, [1, 1, 1, 1, 1]),
    )
    for ranks, hand, points, marked in cases:
        model.b[:5] = bytes(ranks)
        model.c[:5] = bytes([0, 1, 2, 3, 0])
        model.env["evaluate"]()
        assert (model.s.hand, model.s.points) == (hand, points)
        assert model.d[:5] == bytes(marked)
        model.c[:5] = bytes(5)
        model.env["evaluate"]()
        assert (model.s.hand, model.s.points) == (7, 25)
        assert model.d[:5] == bytes([1] * 5)

    player = Player("chain_suit", rom=rom, pad=False)
    plan = []
    original_press = player.press

    def record(action):
        plan.append(action)
        original_press(action)

    player.press = record
    solve_stage(player)
    machine, model = begin("chain_suit", rom)
    slots = json.loads((machine.directory / "build/state_slots.json").read_text())
    bank = machine.read(0xC000, 256)
    assert len({bank[i * 32 : (i + 1) * 32] for i in range(4)}) == 4

    def check_cards():
        screen = machine.read(0xC100, 768)
        for i in range(5):
            x = 1 + i * 6
            assert screen[5 * 32 + x] == 144
            assert screen[11 * 32 + x + 4] == 147
            tens = 150 + model.b[i] // 10 if model.b[i] >= 10 else 64
            assert screen[6 * 32 + x + 1] == tens
            assert screen[6 * 32 + x + 2] == 150 + model.b[i] % 10
            assert screen[8 * 32 + x + 1] == 128 + model.c[i] * 4
            assert screen[9 * 32 + x + 2] == 131 + model.c[i] * 4
            assert screen[12 * 32 + x + 2] == (10 if model.d[i] else 64)

    check_cards()
    scored = []
    for index, action in enumerate(plan):
        if action not in (1, 5):
            machine.action(action)
            model.action(action)
            assert_state(machine, model)
            check_cards()
            continue
        old_board = machine.read("B_ARRAY", 5)
        old_suits = machine.read("C_ARRAY", 5)
        hand, points, score, round_index = (
            model.s.hand,
            model.s.points,
            model.s.score,
            model.s.round,
        )
        if action == 5:
            scored.append((hand, points))
        phases = []
        clocks = []
        lib.key(machine.p, *KEYS[action], 1)
        machine.until("DISPATCH")
        model.action(action)
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
            assert machine.read(0xC000, 256) == bank
            assert machine.get("MODE") == 1
            assert machine.get(slots["s.round"]) == round_index
            clocks.append(lib.clocks(machine.p))
            if action == 5:
                phases.append(machine.get(slots["s.blink"]))
                assert machine.get(slots["s.scoring"]) == 1
                assert machine.get(slots["s.hand"]) == hand
                assert machine.get(slots["s.points"]) == points
                assert machine.get(slots["s.score"]) == score + points
                assert machine.read("B_ARRAY", 5) == old_board
                assert machine.read("C_ARRAY", 5) == old_suits
            else:
                phases.append(machine.get(slots["s.flipping"]))
                if len(phases) <= 2:
                    assert machine.read("B_ARRAY", 5) == old_board
                    assert machine.read("C_ARRAY", 5) == old_suits
            if capture:
                machine.capture(capture / f"action-{index:02}-{len(phases)}.png")
            lib.key(machine.p, *KEYS[action], 0)
            if len(phases) == 2:
                lib.key(machine.p, *KEYS[4], 1)
            if len(phases) == 4:
                lib.key(machine.p, *KEYS[4], 0)
        lib.key(machine.p, *KEYS[action], 0)
        machine.until("INPUT_DONE")
        assert_state(machine, model)
        assert machine.get("MOTION_ACTIVE") == machine.get("KEY_PENDING") == 0
        check_cards()
        assert phases == ([1, 0, 1, 0, 0] if action == 5 else [1, 2, 1, 0])
        if action == 5:
            assert lib.clocks(machine.p) - clocks[0] >= 14900 * 108
    assert scored == [(0, 3), (1, 8), (2, 16)]
    assert model.s.mode == 2 and model.s.score == 27 and model.s.round == 3
    print(
        "PASS: chain_suit, rank/suit card faces, eight hand labels, scoring preserved, flip frames and input isolation"
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
