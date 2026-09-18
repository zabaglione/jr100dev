"""Thirty input-only solutions, with independent path occupancy checks."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib

ROOT = Path(__file__).resolve().parent
LEVELS = json.loads((ROOT / "levels.json").read_text())
DIR = {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}


def finish(m):
    for _ in range(3000):
        lib.frame(m.p)
        if m.get("MODE") == 4:
            m.until("IDLE")
            m.until("INPUT_DONE")
            return
    raise AssertionError("Strike did not finish")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rom", type=Path)
    p.add_argument("--capture", action="store_true")
    p.add_argument("--keyboard", action="store_true")
    args = p.parse_args()
    m = Machine("trace_blade", args.rom.read_bytes() if args.rom else None)
    pad = not args.keyboard
    if args.capture:
        assert args.rom
        (ROOT / "images").mkdir(exist_ok=True)
        (ROOT / "art").mkdir(exist_ok=True)
        m.capture(ROOT / "images/title.png")
        m.export_workbench(ROOT / "art/title.pcg.json")
    m.action(5, pad)
    total = 0
    for i, level in enumerate(LEVELS):
        assert m.get("LEVEL") == i
        x = y = 1
        visited = {13}
        marked = 0
        for n, a in enumerate(level["solution"]):
            dx, dy = DIR[a]
            x += dx
            y += dy
            pos = y * 12 + x
            assert pos not in visited and level["map"][y][x] != 1
            visited.add(pos)
            marked += level["map"][y][x] == 2
            m.action(a, pad)
            assert (
                m.get("PLAYER_X"),
                m.get("PLAYER_Y"),
                m.get("PATH_LEN"),
                m.get("MARKED"),
            ) == (x, y, n + 1, marked)
            assert {j for j, b in enumerate(m.read("VISITED", 108)) if b} == visited
        assert marked == level["targets"] and level["map"][y][x] == 3
        if args.capture and i == 14:
            m.capture(ROOT / "images/planning-15.png")
            m.export_workbench(ROOT / "art/planning.pcg.json")
        if pad:
            m.action(5, True)
            m.action(5, True)
        else:
            m.action(8)
        assert m.get("MODE") == 3
        if args.capture and i == 14:
            for _ in range(100):
                lib.frame(m.p)
            m.until("INPUT_DONE")
            m.capture(ROOT / "images/strike-15.png")
        finish(m)
        assert m.get("COMBO") == level["targets"]
        assert not any(v == 2 for v in m.read("MAP", 108))
        total += len(level["solution"])
        m.action(5, pad)
    assert m.get("MODE") == 5
    assert m.read(0x300, len(m.code)) == m.code and lib.min_sp(m.p) >= 0x3E00
    if args.capture:
        m.capture(ROOT / "images/ending.png")
    print(
        f"PASS: thirty chambers, {total} path steps, all targets cut, SP ${lib.min_sp(m.p):04X}"
    )


if __name__ == "__main__":
    main()
