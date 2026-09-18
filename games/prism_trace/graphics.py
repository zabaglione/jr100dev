"""Pack connected optical paths into shared JR-100 character quadrants."""

from relief import Pixels, sprite


def atlas():
    glyphs = {bytes(8): 64}  # The ROM blank needs no PCG character.
    stamps = []
    for kind, masks in (
        (0, (0, 3, 12, 15)),
        (1, (0, 5, 10, 15)),
        (2, (0, 6, 9, 15)),
        (3, (0, 4)),
    ):
        for mask in masks:
            pixels = Pixels(contact_shadow=False)
            if kind:
                shape = sprite({1: "mirror-up", 2: "mirror-down", 3: "socket"}[kind])
                for y in range(16):
                    for x in range(16):
                        byte = shape[(y // 8 * 2 + x // 8) * 8 + y % 8]
                        pixels.dot(x, y, byte >> (7 - x % 8) & 1)
            elif mask == 0:
                pixels.dot(7, 7)
            # All four ports meet at (7, 7), including across cell boundaries.
            if mask & 1:
                pixels.line(7, 0, 7, 7)
            if mask & 2:
                pixels.line(7, 7, 7, 15)
            if mask & 4:
                pixels.line(0, 7, 7, 7)
            if mask & 8:
                pixels.line(7, 7, 15, 7)
            packed = pixels.pack()
            for quadrant in range(4):
                glyph = bytes(packed[quadrant * 8 : quadrant * 8 + 8])
                if glyph not in glyphs:
                    glyphs[glyph] = 127 + len(glyphs)
                stamps.append(glyphs[glyph])
    bank = [byte for glyph, code in glyphs.items() if code >= 128 for byte in glyph]
    assert len(bank) == 21 * 8  # Leaves a complete ten-digit font and one spare.
    return bank + [0] * (256 - len(bank)), stamps
