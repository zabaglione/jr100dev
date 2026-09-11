"""Authored stone lettering and dungeon portal using sixteen quarter-cell tiles."""

FONT = {
    "R": (30, 17, 17, 30, 20, 18, 17),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "I": (31, 4, 4, 4, 4, 4, 31),
    "C": (15, 16, 16, 16, 16, 16, 15),
    "D": (30, 17, 17, 17, 17, 17, 30),
    "V": (17, 17, 17, 17, 17, 10, 4),
}


def build():
    pixels = [[0] * 64 for _ in range(34)]

    def dot(x, y, value=1):
        assert 0 <= x < 64 and 0 <= y < 34
        pixels[y][x] = value

    def line(x0, y0, x1, y1, value=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        error = dx + dy
        while True:
            dot(x0, y0, value)
            if (x0, y0) == (x1, y1):
                break
            twice = error * 2
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    # Broken stone frame and a full-width, 28-pixel-high inscription.
    line(1, 1, 62, 1)
    line(1, 1, 1, 11)
    line(62, 1, 62, 11)
    line(2, 12, 61, 12)
    x = 4
    for letter in "RELIC DIVE":
        if letter == " ":
            x += 3
            continue
        for y, bits in enumerate(FONT[letter]):
            for bit in range(5):
                if bits & (16 >> bit):
                    dot(x + bit, y + 4)
        x += 6
    # Perspective columns, a central relic and descending steps.
    for left, right in ((3, 60), (12, 51), (20, 43)):
        top = 19 + (left // 9)
        for edge in (left, right):
            line(edge, top, edge, 32)
            line(
                edge + (1 if edge < 32 else -1),
                top,
                edge + (1 if edge < 32 else -1),
                32,
            )
        line(left, top, left + 4, top)
        line(right - 4, top, right, top)
        line(left, 32, left + 3, 32)
        line(right - 3, 32, right, 32)
    for x0, x1, y in ((27, 36, 28), (25, 38, 30), (23, 40, 32)):
        line(x0, y, x1, y)
    line(27, 28, 22, 33)
    line(36, 28, 41, 33)
    # Faceted diamond hanging in the dark doorway.
    for a, b in (
        ((31, 19), (27, 23)),
        ((27, 23), (31, 27)),
        ((31, 27), (35, 23)),
        ((35, 23), (31, 19)),
    ):
        line(*a, *b)
    line(29, 23, 33, 23)
    line(31, 21, 31, 25)
    for y in (20, 24, 28):
        for x in (5, 58):
            dot(x, y)
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
                (144 + mask if 2 <= y <= 5 else 128 + mask) if mask else 64
            )
    for x, y in ((10, 8), (21, 8), (12, 11), (19, 11), (9, 14), (22, 14)):
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
