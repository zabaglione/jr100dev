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
    used = sorted({code for code in screen if code >= 128})
    mapping = {code: 128 + i for i, code in enumerate(used)}
    tiles = [b for code in used for b in tiles[(code - 128) * 8 : (code - 127) * 8]]
    screen = [mapping.get(code, code) for code in screen]
    stream = []
    index = 0
    while index < len(screen):
        end = index + 1
        while end < len(screen) and screen[end] == screen[index] and end - index < 126:
            end += 1
        if screen[index] == 64:
            stream.append(end - index)
        elif end - index >= 4:
            stream.extend((127, end - index, screen[index]))
        else:
            stream.extend(screen[index:end])
        index = end
    stream.append(0)
    lines = ["TITLE_TILES: .BYTE " + ",".join(map(str, tiles)), "TITLE_TILES_END:"]
    lines.append("TITLE_ART: .BYTE " + ",".join(map(str, stream)))
    lines.append("TITLE_ART_END:")
    lines.append("TITLE_SPARK_FRAMES: .BYTE " + ",".join(map(str, sparkles)))
    lines.append(f"TITLE_SPARK_ADDRESS: .equ {0xC000 + (mapping[144] - 128) * 8}")
    return "\n".join(lines), {
        "pcg": tiles,
        "screen": screen,
        "stream_bytes": len(stream),
    }
