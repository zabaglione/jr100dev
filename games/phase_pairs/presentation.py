"""Numeral cards, a circuit-table surround and four-slot fusion rays."""

from art import emit
from artwork import put
from fonts import PANEL_DIGITS
from title_styles import ROM_QUADS


def prepare(bank, screen):
    # Twenty glyphs form ten complete, sixteen-pixel-high numerals.
    bank[:] = [
        byte
        for digit in "0123456789"
        for byte in (
            [row << 1 for row in PANEL_DIGITS[digit] for _ in range(2)] + [0, 255]
        )
    ]
    bank += [
        byte
        for shape in (
            [0, 3, 7, 15, 24, 16, 16, 16],
            [0, 255, 255, 255, 0, 0, 0, 0],
            [0, 192, 224, 240, 56, 24, 24, 24],
            [16] * 8,
            [24] * 8,
            [16, 16, 16, 16, 24, 15, 7, 7],
            [24, 24, 24, 24, 56, 240, 224, 224],
            [0, 255, 255, 255, 60, 24, 0, 0],
        )
        for byte in shape
    ]
    poses = []
    for points in ((4, 5, 6), (1, 2, 4), (0, 2), (0,)):
        quadrant = [0] * 8
        for point in points:
            quadrant[point] = (192 if len(points) > 2 else 128) >> point
        mirrored = [int(f"{row:08b}"[::-1], 2) for row in quadrant]
        poses.append(quadrant + mirrored + quadrant[::-1] + mirrored[::-1])
    bank += poses[0]
    assert len(bank) == 256
    bright = [0, 3, 7, 15, 31, 31, 31, 31]
    mirror = [int(f"{row:08b}"[::-1], 2) for row in bright]
    poses.append(bright + mirror + bright[::-1] + mirror[::-1])
    poses.append(bank[160:168] + bank[176:184] + bank[200:208] + bank[208:216])

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

    housing(0, 2, 19, 19)
    put(screen, 4, 2, " FUSION CORE ")
    for y in range(4, 21):
        raw(19, y, ROM_QUADS[5 if y % 2 else 1])
    for x in range(2, 19):
        raw(x, 21, ROM_QUADS[3])
    for row in range(4):
        for column in range(4):
            x, y = 2 + column * 4, 4 + row * 4
            for dx, dy, quad in ((0, 0, 8), (2, 0, 4), (0, 2, 2), (2, 2, 1)):
                raw(x + dx, y + dy, ROM_QUADS[quad])
        if row < 3:
            put(screen, 3, 7 + row * 4, ".   .   .   .")
    housing(21, 2, 11, 6)
    housing(21, 8, 11, 6)
    housing(21, 14, 11, 7)
    put(screen, 24, 3, "MAKE")
    for digit, x in ((1, 25), (0, 26)):
        raw(x, 5, 128 + digit * 2)
        raw(x, 6, 129 + digit * 2)
    put(screen, 24, 9, "PAIR")
    put(screen, 25, 11, "+")
    put(screen, 22, 15, "LEFT MISS")
    put(screen, 29, 19, "/6")
    return emit("FACE_7_FRAMES", [byte for pose in poses for byte in pose])


def hint_hook(source):
    return source.replace(
        "IDLE:\n    JSR CLOCK_SERVICE\n",
        "IDLE:\n    JSR CLOCK_SERVICE\n    JSR PHASE_HINT_TICK\n",
        1,
    )
