"""PCG ownership, original type and MB8861H presentation/bank-switch checks."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "common"))
from fonts import FONT_ROWS, STYLES, SYMBOLS, glyph
from machine import Machine, lib


def check(directory):
    metadata = json.loads((directory / "game.json").read_text())
    data = json.loads((directory / "build/fonts.json").read_text())
    machine = Machine(directory.name)
    original = machine.code
    assert machine.read("FONT_OFFSET", 1) == bytes(1)
    maps = {}
    for scene in ("title", "game"):
        assigned = data[scene]["characters"]
        slots = list(assigned.values())
        assert len(slots) == len(set(slots)) and set(slots) <= set(
            data[scene]["free_slots"]
        )
        maps[scene] = machine.read("FONT_" + scene.upper() + "_MAP", 64)
        bank = machine.read(scene.upper() + "_PCG", 256)
        for char, slot in assigned.items():
            assert maps[scene][ord(char) - 32] == 128 + slot
            assert bank[slot * 8 : slot * 8 + 8] == bytes(glyph(char, data["style"]))
        digits = set(assigned) & set("0123456789")
        assert not digits or len(digits) == 10, "Never mix numeral styles"
    # Rendering fixture: exercise all byte codes through the real 6800 routine,
    # using both banks repeatedly. This is not presented as gameplay evidence.
    raw = bytes(range(256)) * 3
    for scene in ("title", "game", "title", "game"):
        bank = machine.sym[scene.upper() + "_PCG"]
        load, present = machine.sym["LOAD_PCG"], machine.sym["PRESENT"]
        thunk = bytes(
            [
                0xCE,
                bank >> 8,
                bank & 255,
                0xBD,
                load >> 8,
                load & 255,
                0xBD,
                present >> 8,
                present & 255,
                0x01,
            ]
        )
        for i, byte in enumerate(thunk):
            lib.poke(machine.p, 0x3800 + i, byte)
        for i, byte in enumerate(raw):
            lib.poke(machine.p, 0x3000 + i, byte)
        lib.fixture_pc(machine.p, 0x3800, 0x3FFF)
        machine.until(0x3809)
        expected = bytes(maps[scene][v] if v < 64 else v for v in raw)
        assert machine.read(0xC100, 768) == expected
        assert machine.read(0x3000, 768) == raw, "Semantic text changed"
        assert machine.read(0x300, len(original)) == original
        assert lib.min_sp(machine.p) >= 0x3E00
    print(f"PASS: {metadata['id']}, font ownership, all 256 codes, four bank switches")


if __name__ == "__main__":
    alphabet = set(FONT_ROWS | SYMBOLS) - {" "}
    for style in STYLES:
        shapes = [bytes(glyph(char, style)) for char in sorted(alphabet)]
        assert len(set(shapes)) == len(shapes), (style, "Ambiguous glyphs")
        assert all(len(shape) == 8 and shape[-1] == 0 for shape in shapes)
    for name in sys.argv[1:]:
        check(ROOT / name)
