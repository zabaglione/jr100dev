"""Input-only persistent progress and a twelve-chamber escape."""

import argparse
import json
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib

ROOT = Path(__file__).resolve().parent
ROOMS = json.loads((ROOT / "rooms.json").read_text())
DIR = {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}


def route(room, start, target, radius=1, opened=False):
    grid = ROOMS[room]["map"]
    q = deque([(start, [])])
    seen = {start}
    while q:
        (x, y), path = q.popleft()
        if abs(x - target[0]) + abs(y - target[1]) <= radius:
            return path
        for a, (dx, dy) in DIR.items():
            pos = (x + dx, y + dy)
            if not (0 <= pos[0] < 16 and 0 <= pos[1] < 10):
                continue
            if grid[pos[1]][pos[0]] in ((1, 5) if opened else (1, 4, 5)):
                continue
            if pos not in seen:
                seen.add(pos)
                q.append((pos, [*path, a]))
    raise AssertionError("No safe route")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--rom", type=Path)
    p.add_argument("--capture", action="store_true")
    p.add_argument("--keyboard", action="store_true")
    args = p.parse_args()
    m = Machine("loop_ten", args.rom.read_bytes() if args.rom else None)
    pad = not args.keyboard
    if args.capture:
        assert args.rom
        (ROOT / "images").mkdir(exist_ok=True)
        (ROOT / "art").mkdir(exist_ok=True)
        m.capture(ROOT / "images/title.png")
        m.export_workbench(ROOT / "art/title.pcg.json")
    m.action(5, pad)
    steps = 0
    for i in range(12):
        if i:
            m.action(5, pad)
        assert m.get("ROOM") == i, (i, m.get("ROOM"))
        x, y = m.get("PLAYER_X"), m.get("PLAYER_Y")
        for a in route(i, (x, y), (12, 4)):
            m.action(a, pad)
            dx, dy = DIR[a]
            x += dx
            y += dy
            steps += 1
            assert (m.get("ROOM"), m.get("PLAYER_X"), m.get("PLAYER_Y")) == (i, x, y)
        if args.capture and i == 4:
            m.capture(ROOT / "images/chamber-05.png")
            m.export_workbench(ROOT / "art/chamber.pcg.json")
        if args.capture and i == 0:
            # Wait in the actual game; keep the timer running for this scene.
            for _ in range(600):
                lib.frame(m.p)
                m.until("INPUT_IDLE")
                if m.get("SECONDS") == 1:
                    break
            else:
                raise AssertionError("Last-second capture was not reached")
            assert m.get("MODE") == 1 and m.get("ROOM") == 0
            m.capture(ROOT / "images/last-second.png")
        m.action(5, pad)
        assert int.from_bytes(m.read("FLAGS", 2), "little") == (1 << (i + 1)) - 1
        if i < 11:
            if args.capture and i == 4:
                m.capture(ROOT / "images/seal-open.png")
            m.action(5, pad)
            assert m.get("ROOM") == 0 and m.get("LOOPS") == i + 2
    assert m.get("MODE") == 3
    assert m.read(0x300, len(m.code)) == m.code and lib.min_sp(m.p) >= 0x3E00
    if args.capture:
        m.capture(ROOT / "images/ending.png")
    print(
        f"PASS: twelve seals persist across rewinds, {steps} moves, {m.get('LOOPS')} loops, SP ${lib.min_sp(m.p):04X}"
    )


if __name__ == "__main__":
    main()
