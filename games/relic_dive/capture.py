"""Capture publication frames after a genuine BASIC/PRG boot and key inputs."""

import argparse
import ctypes
import json
import re
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tests"))
from machine import lib

SYMBOLS = {
    name: int(value, 16)
    for name, value in re.findall(
        r"^(\w+)\s*=\s*\$([0-9A-Fa-f]+)",
        (ROOT / "build/relic-dive.map").read_text(),
        re.MULTILINE,
    )
}
KEYS = {1: (2, 1), 2: (0, 3), 3: (1, 0), 4: (1, 2), 5: (8, 3)}
DIRECTIONS = ((0, -1, 1), (0, 1, 2), (-1, 0, 3), (1, 0, 4))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--title-only", action="store_true")
    args = parser.parse_args()
    rom = args.rom.read_bytes()
    machine = lib.create(rom, len(rom))
    inputs = []

    def get(name):
        return lib.peek(machine, SYMBOLS[name] if isinstance(name, str) else name)

    def until(name):
        assert lib.until(machine, SYMBOLS[name], 30_000_000), f"Timeout: {name}"

    def action(number):
        inputs.append(number)
        lib.key(machine, *KEYS[number], 1)
        until("DISPATCH")
        until("FRAME_READY")
        lib.key(machine, *KEYS[number], 0)
        until("POLL_DONE")

    def capture(name):
        pixels = ctypes.create_string_buffer(256 * 192)
        lib.pixels(machine, pixels)
        frame = Image.frombytes(
            "L", (256, 192), bytes(255 if value else 0 for value in pixels.raw)
        ).resize((768, 576), Image.Resampling.NEAREST)
        ImageOps.expand(frame, border=24, fill=0).save(ROOT / "images" / name)

    def route_to_item():
        start = (get("G_X"), get("G_Y"))
        targets = set()
        for index in range(SYMBOLS["MAX_ITEMS"]):
            item = SYMBOLS["FLOORS"] + SYMBOLS["ITEM_START"] + index * 3
            x, y, kind = (get(item + offset) for offset in range(3))
            if kind and (x, y) != start:
                targets.add((x, y))
        queue = deque([(start, [])])
        seen = {start}
        while queue:
            (x, y), route = queue.popleft()
            if (x, y) in targets:
                return route
            for dx, dy, number in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < 64 and 0 <= ny < 32):
                    continue
                tile = get(SYMBOLS["FLOORS"] + ny * 32 + nx // 2)
                tile = (tile >> (4 if nx & 1 else 0)) & 15
                if tile not in (1, 3, 4):
                    continue
                seen.add((nx, ny))
                queue.append(((nx, ny), route + [number]))
        return []

    try:
        for _ in range(100):
            lib.frame(machine)
        prg = (ROOT / "build/relic-dive.prg").read_bytes()
        assert lib.load_prg(machine, prg, len(prg)), "PRG loading failed"
        for _ in range(450):
            lib.frame(machine)
        assert 0x300 <= lib.pc(machine) < SYMBOLS["CODE_END"]
        assert get("G_MODE") == 0, "BASIC autostart did not reach title"
        capture("title.png")
        if args.title_only:
            print("Captured title from BASIC boot")
            return
        action(1)
        action(5)
        assert get("G_MODE") == 1
        capture("play-01.png")
        # Read-only route selection; all changes to the game come from keys.
        for _ in range(48):
            bag_count = sum(bool(get(SYMBOLS["G_BAG"] + slot)) for slot in range(6))
            if get("G_MODE") != 1 or get("G_HP") < 10 or bag_count >= 4:
                break
            route = route_to_item()
            if not route:
                break
            action(route[0])
        assert get("G_MODE") == 1, "Exploration ended before capture"
        capture("play-02.png")
        action(5)
        if get("G_CONTEXT"):
            action(2)
        action(5)
        assert get("G_MODE") == 3, "Inventory did not open"
        capture("inventory.png")
        (ROOT / "build/publication-capture.json").write_text(
            json.dumps({"boot": "BASIC autostart", "inputs": inputs}, indent=2) + "\n"
        )
        print("Captured title, two exploration scenes and inventory from BASIC boot")
    finally:
        lib.destroy(machine)


if __name__ == "__main__":
    main()
