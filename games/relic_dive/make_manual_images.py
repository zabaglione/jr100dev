"""Expand the assembled JR-100 PCG rows into lossless 64x64 manual PNGs."""

import re
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GLYPHS = {
    "unknown": 0,
    "wall": 1,
    "floor": 2,
    "stairs": 4,
    "relic": 5,
    "player": 6,
    "food": 7,
    "potion": 8,
    "scroll": 9,
    "weapon": 10,
    "armor": 11,
    "gold": 12,
    "slime": 13,
    "goblin": 14,
    "orc": 15,
    "wraith": 16,
    "rat": 17,
    "bat": 18,
    "skeleton": 19,
    "troll": 20,
    "thief": 21,
    "snake": 22,
    "rust-beast": 23,
    "centaur": 24,
    "trap": 25,
    "vampire": 26,
    "dragon": 27,
    "nymph": 28,
    "wand": 29,
    "ring": 30,
}


def png(width, height, pixels):
    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data))
        )

    rows = b"".join(b"\0" + pixels[y * width : (y + 1) * width] for y in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def main():
    symbols = {
        name: int(value, 16)
        for name, value in re.findall(
            r"^(\w+)\s*=\s*\$([0-9A-Fa-f]+)",
            (ROOT / "build/relic-dive.map").read_text(),
            re.MULTILINE,
        )
    }
    binary = (ROOT / "build/relic-dive.bin").read_bytes()
    tiles = binary[symbols["TILES"] - 0x300 : symbols["TILES_END"] - 0x300]
    destination = ROOT / "images"
    destination.mkdir(exist_ok=True)
    sheet = bytearray(8 * 72 * 4 * 72)
    for number, (name, tile) in enumerate(GLYPHS.items()):
        rows = tiles[tile * 8 : (tile + 1) * 8]
        assert len(rows) == 8
        pixels = bytes(
            255 if rows[y // 8] & (128 >> (x // 8)) else 0
            for y in range(64)
            for x in range(64)
        )
        (destination / f"{name}.png").write_bytes(png(64, 64, pixels))
        sx, sy = number % 8 * 72, number // 8 * 72
        for y in range(64):
            offset = (sy + y) * 576 + sx
            sheet[offset : offset + 64] = pixels[y * 64 : (y + 1) * 64]
    (ROOT / "build/pcg-guide-contact.png").write_bytes(png(576, 288, bytes(sheet)))
    print(f"Generated {len(GLYPHS)} PCG images")


if __name__ == "__main__":
    main()
