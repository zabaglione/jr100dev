"""Three-tone title relief using ROM blocks and exact PCG tiles.

The ROM characters describe geometry, not a bundled copy of the BASIC font.
PB5 remains high. Inverse-ROM mode cannot be mixed with PCG on the same screen.
"""

ROM_QUADS = (
    0x40,
    0x78,
    0x7A,
    0x6E,
    0x73,
    0x72,
    0x62,
    0x64,
    0x61,
    0x67,
    0x68,
    0x66,
    0x54,
    0x63,
    0x76,
    0x4E,
)
RESERVED = {"chrono-breach": (28, 29, 30, 31), "sigil-deck": (28, 29)}


def relief(canvas):
    """Extrude whole letters; keep the bright face and its counters intact."""
    from artwork import Canvas

    pixels = [row.copy() for row in canvas.p]
    for value, x, y, style, wide, tall in canvas.titles:
        mask = Canvas(len(pixels))
        mask.paint_label(value, x, y, style, wide, tall)
        for yy in range(len(pixels) - 1):
            for xx in range(63):
                if mask.p[yy][xx] and not pixels[yy + 1][xx + 1]:
                    pixels[yy + 1][xx + 1] = 2
    return pixels


def tile_bytes(values):
    return tuple(
        sum(
            (value == 1 or value == 2 and (x + y) % 2 == 0) << (7 - x)
            for x in range(8)
            for value in (values[(y // 4) * 2 + x // 4],)
        )
        for y in range(8)
    )


def compile_title(pixels, game_id):
    """Pack losslessly; never approximate a letter to fit the PCG budget."""
    slots = iter(i for i in range(32) if i not in RESERVED.get(game_id, ()))
    assigned = {}
    bank = [0] * 256
    screen = []
    for y in range(0, len(pixels), 2):
        for x in range(0, 64, 2):
            values = tuple(pixels[y + dy][x + dx] for dy in (0, 1) for dx in (0, 1))
            if 2 not in values:
                screen.append(ROM_QUADS[sum(v << i for i, v in enumerate(values))])
                continue
            shape = tile_bytes(values)
            if shape not in assigned:
                slot = next(slots, None)
                assert slot is not None, (game_id, "Title exceeds 32 PCG slots")
                assigned[shape] = 128 + slot
                bank[slot * 8 : slot * 8 + 8] = shape
            screen.append(assigned[shape])
    return bank, screen
