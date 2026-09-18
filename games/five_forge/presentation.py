"""Forged board, embossed stones and one four-glyph landing animation slot."""

from art import emit
from artwork import put
from relief import Pixels
from title_styles import ROM_QUADS


def cell(mark=0, height=7, radius=5, selected=False):
    pixels = Pixels(contact_shadow=False)
    pixels.line(0, 8, 15, 8)
    pixels.line(7, 0, 7, 15)
    if mark:
        pixels.ellipse(7, height + 2, 6, radius, True, 0)
        pixels.ellipse(7, height + 2, 6, radius)
        pixels.ellipse(7, height, 6, radius, True)
        if mark == 1:
            pixels.ellipse(7, height, 3, max(1, radius - 2), True, 0)
        else:
            pixels.line(4, height - radius + 2, 10, height + radius - 2, 0)
            pixels.line(10, height - radius + 2, 4, height + radius - 2, 0)
        pixels.dot(11, height + 2, 0)
    if selected:
        for x, dx in ((0, 1), (15, -1)):
            for y, dy in ((0, 1), (15, -1)):
                pixels.line(x, y, x + 3 * dx, y)
                pixels.line(x, y, x, y + 3 * dy)
    return pixels.pack()


def prepare(bank, screen):
    poses = [
        cell(mark, height, radius, selected=True)
        for mark in (1, 2)
        for height, radius in ((3, 3), (6, 5), (10, 3), (7, 5))
    ]
    bank[:] = cell() + cell(1) + cell(2) + poses[3] + cell(selected=True) + [0] * 96
    assert len(bank) == 256

    def raw(x, y, code):
        screen[y * 32 + x] = code

    def housing(x, y, width, height):
        for xx in range(x + 1, x + width - 1):
            raw(xx, y, ROM_QUADS[3])
            raw(xx, y + height - 1, ROM_QUADS[12])
        for yy in range(y + 1, y + height - 1):
            raw(x, yy, ROM_QUADS[5])
            raw(x + width - 1, yy, ROM_QUADS[10])
        for xx, yy, quad in (
            (x, y, 2),
            (x + width - 1, y, 1),
            (x, y + height - 1, 8),
            (x + width - 1, y + height - 1, 4),
        ):
            raw(xx, yy, ROM_QUADS[quad])

    housing(0, 3, 18, 18)
    for y in range(5, 21):
        raw(18, y, ROM_QUADS[5 if y % 2 else 1])
    for x in range(2, 19):
        raw(x, 21, ROM_QUADS[3])
    for i in range(8):
        put(screen, 1 + i * 2, 2, chr(65 + i))
        put(screen, 0, 4 + i * 2, str(i + 1))
    put(screen, 1, 1, "FORGE A LINE OF FIVE")
    for y in (3, 9, 15):
        housing(20, y, 12, 6)
    put(screen, 22, 4, "YOU / O")
    put(screen, 22, 10, "RIVAL / X")
    return emit("FACE_3_FRAMES", [byte for pose in poses for byte in pose])
