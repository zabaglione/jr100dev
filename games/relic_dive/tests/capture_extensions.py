"""Render explicitly constructed visual fixtures for new monsters and items."""

import argparse
from pathlib import Path

from capture_screen import capture
from check_game import enemy, reset_room
from machine import EMU, SYMS, Machine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, default=EMU / "datas/jr100rom.prg")
    args = parser.parse_args()
    m = Machine(args.rom.read_bytes())
    reset_room(m)
    enemy(m, 10, 10, kind=13, hp=12)
    enemy(m, 14, 10, kind=14, hp=16, index=1)
    enemy(m, 12, 9, kind=15, hp=7, index=2)
    m.call("RENDER_SCREEN")
    capture(m, "new-monsters-fixture")
    for kind, x, y in [("vampire", 10, 10), ("dragon", 14, 10), ("nymph", 12, 9)]:
        m.set("G_MODE", 5)
        m.set("G_INSPECT_X", x)
        m.set("G_INSPECT_Y", y)
        m.call("RENDER_SCREEN")
        capture(m, f"{kind}-fixture")
    for i, item in enumerate([2, 3, 4, 14, 15, 16]):
        m.set(SYMS["G_BAG"] + i, item)
    for i in range(8):
        m.set(SYMS["G_IDENTITIES"] + i, i)
    m.set("G_KNOWN", 255)
    m.set("G_MODE", 3)
    m.call("RENDER_SCREEN")
    capture(m, "new-magic-fixture")
    for i, item in enumerate([17, 18, 19, 20, 21, 22]):
        m.set(SYMS["G_BAG"] + i, item)
    m.call("RENDER_SCREEN")
    capture(m, "ring-wands-fixture")
    m.set("G_MODE", 1)
    m.set("G_SLOT", 0)
    m.call("USE_ITEM")
    m.call("RENDER_SCREEN")
    capture(m, "wand-target-fixture")
    m.set("G_MODE", 6)
    m.call("RENDER_SCREEN")
    capture(m, "keyboard-help")
    m.close()


if __name__ == "__main__":
    main()
