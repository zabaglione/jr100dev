"""Large celestial cards, orbital housings and four-slot resonance flashes."""

from art import emit
from artwork import put
from relief import Pixels
from title_styles import ROM_QUADS


def prepare(bank, screen):
    planets = []
    for kind in range(3):
        pixels = Pixels(contact_shadow=False)
        if kind == 0:
            pixels.poly(
                [
                    (7, 0),
                    (9, 5),
                    (15, 6),
                    (11, 9),
                    (12, 15),
                    (7, 12),
                    (2, 15),
                    (3, 9),
                    (0, 6),
                    (5, 5),
                ],
                True,
            )
            pixels.line(7, 4, 7, 9, 0)
        elif kind == 1:
            pixels.ellipse(7, 7, 5, 5, True)
            pixels.line(0, 10, 15, 3)
            pixels.line(1, 12, 15, 5)
            pixels.line(3, 8, 12, 4, 0)
            pixels.line(10, 9, 11, 6, 0)
        else:
            pixels.ellipse(7, 7, 6, 7, True)
            pixels.ellipse(10, 4, 5, 6, True, 0)
            pixels.dot(2, 7, 0)
            pixels.dot(4, 11, 0)
            pixels.dot(13, 2)
        planets += pixels.pack()
    flashes = []
    for radius in (3, 5, 7):
        pixels = Pixels(contact_shadow=False)
        pixels.ellipse(7, 7, radius, radius, True)
        pixels.line(7, 0, 7, 15)
        pixels.line(0, 7, 15, 7)
        pixels.line(0, 0, 14, 14)
        pixels.line(0, 14, 14, 0)
        flashes += pixels.pack()
    borders = [
        [0, 0, 0, 7, 8, 16, 16, 16],
        [0, 0, 0, 224, 16, 16, 16, 16],
        [16, 16, 8, 7, 0, 0, 0, 0],
        [16, 16, 16, 224, 0, 0, 0, 0],
        [0, 0, 0, 255, 0, 0, 0, 0],
        [16] * 8,
    ]
    bank[:] = (
        planets + flashes[:32] + [v for glyph in borders for v in glyph] + [0] * 80
    )
    assert len(bank) == 256

    def raw(x, y, quad):
        screen[y * 32 + x] = ROM_QUADS[quad]

    def housing(x, y, width, height):
        for xx in range(x + 1, x + width - 1):
            raw(xx, y, 3)
            raw(xx, y + height - 1, 12)
        for yy in range(y + 1, y + height - 1):
            raw(x, yy, 5)
            raw(x + width - 1, yy, 10)
        for xx, yy, quad in (
            (x, y, 2),
            (x + width - 1, y, 1),
            (x, y + height - 1, 8),
            (x + width - 1, y + height - 1, 4),
        ):
            raw(xx, yy, quad)

    orbit = Pixels(width=40, height=36, contact_shadow=False)
    orbit.ellipse(19, 17, 18, 12)
    orbit.ellipse(19, 17, 13, 16)
    for y in range(18):
        for x in range(20):
            quad = sum(
                orbit.p[y * 2 + dy][x * 2 + dx] << (dy * 2 + dx)
                for dy in range(2)
                for dx in range(2)
            )
            if quad:
                raw(x, y + 2, quad)
    housing(0, 2, 20, 18)
    # Card housings are static: bake them into the screen rather than spending
    # native CPU time reconstructing 216 border cells for every motion frame.
    for row in range(3):
        for column in range(3):
            x, y = 1 + column * 6, 4 + row * 5
            for dx, dy, slot in ((0, 0, 16), (4, 0, 17), (0, 4, 18), (4, 4, 19)):
                screen[(y + dy) * 32 + x + dx] = 128 + slot
            for offset in range(3):
                screen[y * 32 + x + offset + 1] = 148
                screen[(y + 4) * 32 + x + offset + 1] = 148
                screen[(y + offset + 1) * 32 + x] = 149
                screen[(y + offset + 1) * 32 + x + 4] = 149
                put(screen, x + 1, y + offset + 1, "   ")
    for x in range(2, 20):
        raw(x, 20, 3)
    for y in (4, 8, 12, 16):
        raw(20, y, 9)
    housing(21, 2, 11, 8)
    housing(21, 10, 11, 6)
    housing(21, 16, 11, 5)
    put(screen, 22, 3, "PICK 1/2")
    put(screen, 26, 13, "/")
    put(screen, 22, 17, "CARDS  /9")
    put(screen, 22, 19, "SPINS  /2")
    return emit("FACE_3_FRAMES", flashes)
