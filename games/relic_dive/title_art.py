"""Authored stone lettering and dungeon portal using sixteen quarter-cell tiles."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "native"))
from artwork import poster


def build():
    pixels = poster({"id": "relic-dive"}).p[:34]
    tiles = []
    for mask in range(16):
        tiles += [(0xF0 if mask & 1 else 0) | (0x0F if mask & 2 else 0)] * 4
        tiles += [(0xF0 if mask & 4 else 0) | (0x0F if mask & 8 else 0)] * 4
    # Fine sparkles are separate from the stone lettering and architecture.
    sparkles = [0, 0, 16, 56, 16, 0, 0, 0, 0, 16, 84, 56, 254, 56, 84, 16]
    tiles += sparkles[:8]
    for mask in range(1, 16):
        # Two small chisel marks per quarter preserve the outer letter shape.
        tile = tiles[mask * 8 : mask * 8 + 8].copy()
        for quadrant in range(4):
            if mask & (1 << quadrant):
                y, x = (quadrant // 2) * 4, (quadrant % 2) * 4
                tile[y + 2] &= ~(128 >> (x + 2))
                tile[y + 3] &= ~(128 >> (x + 3))
        tiles += tile
    screen = [64] * 768
    for y in range(17):
        for x in range(32):
            mask = sum(
                pixels[y * 2 + dy][x * 2 + dx] << (dy * 2 + dx)
                for dy in (0, 1)
                for dx in (0, 1)
            )
            screen[y * 32 + x] = (
                (144 + mask if x < 15 and y < 13 else 128 + mask) if mask else 64
            )
    for x, y in ((16, 2), (16, 10), (24, 13)):
        screen[y * 32 + x] = 144
    stream = []
    index = 0
    while index < len(screen):
        if screen[index] != 64:
            stream.append(screen[index])
            index += 1
        else:
            end = index
            while end < len(screen) and screen[end] == 64 and end - index < 127:
                end += 1
            stream.append(end - index)
            index = end
    stream.append(0)
    lines = ["TITLE_TILES: .BYTE " + ",".join(map(str, tiles)), "TITLE_TILES_END:"]
    lines.append("TITLE_ART: .BYTE " + ",".join(map(str, stream)))
    lines.append("TITLE_ART_END:")
    lines.append("TITLE_SPARK_FRAMES: .BYTE " + ",".join(map(str, sparkles)))
    return "\n".join(lines), {
        "pcg": tiles,
        "screen": screen,
        "stream_bytes": len(stream),
    }
