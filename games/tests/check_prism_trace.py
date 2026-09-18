"""Check continuous beam pixels, reflected paths and native stamp placement."""

import argparse
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "native"), str(ROOT / "common"), str(ROOT / "prism_trace")]
from checks import Model, assert_state, begin
from graphics import atlas


def reference(board):
    result = bytearray(49)
    seen = set()
    x, y, dx, dy = 0, 3, 1, 0
    while (x, y, dx, dy) not in seen:
        seen.add((x, y, dx, dy))
        p = y * 7 + x
        incoming = {(0, -1): 2, (0, 1): 1, (-1, 0): 8, (1, 0): 4}[dx, dy]
        if p == 6:
            result[p] |= incoming
            return result, True
        if board[p] == 1:
            dx, dy = -dy, -dx
        elif board[p] == 2:
            dx, dy = dy, dx
        result[p] |= incoming | {(0, -1): 1, (0, 1): 2, (-1, 0): 4, (1, 0): 8}[dx, dy]
        x, y = x + dx, y + dy
        if not (0 <= x < 7 and 0 <= y < 7):
            break
    return result, False


def check(rom=None):
    bank, stamps = atlas()
    assert len(bank) == 256 and max(stamps) == 148

    def pixel(shape, x, y):
        code = stamps[shape * 4 + y // 8 * 2 + x // 8]
        return code != 64 and bank[(code - 128) * 8 + y % 8] >> (7 - x % 8) & 1

    for shape, mask in enumerate((0, 3, 12, 15, 0, 5, 10, 15, 0, 6, 9, 15, 0, 4)):
        for flag, points in (
            (1, [(7, y) for y in range(8)]),
            (2, [(7, y) for y in range(7, 16)]),
            (4, [(x, 7) for x in range(8)]),
            (8, [(x, 7) for x in range(7, 16)]),
        ):
            if mask & flag:
                assert all(pixel(shape, x, y) for x, y in points), (shape, flag)
    model = Model("prism_trace")
    mirrors = [i for i in range(49) if model.b[i]]
    wins = 0
    for orientations in itertools.product((1, 2), repeat=len(mirrors)):
        for cell, kind in zip(mirrors, orientations):
            model.b[cell] = kind
        model.s.mode = 1
        expected, solved = reference(model.b)
        model.env["trace"]()
        assert model.c[:49] == expected
        assert (model.s.mode == 2) == solved
        if solved:
            assert model.c[6] == 4  # This fixed board reaches the goal from its left.
            wins += 1
    assert wins
    machine, model = begin("prism_trace", rom)

    def check_screen():
        screen = machine.read(0xC100, 768)
        for cell in range(49):
            mask = model.c[cell]
            variant = (
                3 if mask == 15 else (1 if mask in (3, 5, 6) else (2 if mask else 0))
            )
            shape = (13 if mask else 12) if cell == 6 else model.b[cell] * 4 + variant
            x, y = 2 + cell % 7 * 2, 4 + cell // 7 * 2
            assert [
                screen[(y + dy) * 32 + x + dx]
                for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1))
            ] == stamps[shape * 4 : shape * 4 + 4]

    check_screen()
    for action in (2, 2, 2, 4, 4, 5):
        machine.action(action)
        model.action(action)
        assert_state(machine, model)
        check_screen()
    print(
        "PASS: prism_trace, 64 mirror configurations, continuous optical ports and native four-quadrant stamps"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    args = parser.parse_args()
    check(args.rom.read_bytes() if args.rom else None)
