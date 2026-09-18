"""Five celestial cards and a sixteen-cell orbit with ROM burst animations."""

from artwork import put
from relief import Pixels
from title_styles import ROM_QUADS


def prepare(bank, screen):
    planets = []
    for kind in range(5):
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
        elif kind == 2:
            pixels.ellipse(7, 7, 6, 7, True)
            pixels.ellipse(10, 4, 5, 6, True, 0)
            pixels.dot(2, 7, 0)
            pixels.dot(4, 11, 0)
            pixels.dot(13, 2)
        elif kind == 3:
            pixels.poly([(4, 8), (15, 0), (11, 10), (5, 14)], True)
            pixels.ellipse(4, 11, 4, 4, True)
            pixels.line(7, 7, 14, 1, 0)
            pixels.line(8, 11, 12, 6, 0)
            pixels.dot(2, 10, 0)
        else:
            pixels.poly([(0, 4), (4, 4), (4, 11), (0, 11)], True)
            pixels.poly([(11, 4), (15, 4), (15, 11), (11, 11)], True)
            pixels.poly([(6, 5), (9, 5), (9, 10), (6, 10)], True)
            pixels.line(3, 7, 12, 7)
            pixels.line(7, 3, 7, 13)
            pixels.line(2, 5, 2, 10, 0)
            pixels.line(13, 5, 13, 10, 0)
        planets += pixels.pack()
    borders = [
        [0, 0, 0, 255, 0, 0, 0, 0],
        [16] * 8,
    ]
    bank[:] = planets + [v for glyph in borders for v in glyph] + [0] * 80
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
    housing(0, 2, 21, 18)
    # ROM corner blocks leave ten PCG glyphs for a complete numeral alphabet.
    for row in range(4):
        for column in range(4):
            x, y = 1 + column * 5, 3 + row * 4
            for dx, dy, quad in ((0, 0, 8), (3, 0, 4), (0, 3, 2), (3, 3, 1)):
                raw(x + dx, y + dy, quad)
            for offset in range(2):
                screen[y * 32 + x + offset + 1] = 148
                screen[(y + 3) * 32 + x + offset + 1] = 148
            for offset in range(2):
                screen[(y + offset + 1) * 32 + x] = 149
                screen[(y + offset + 1) * 32 + x + 3] = 149
                put(screen, x + 1, y + offset + 1, "  ")
    for x in range(2, 21):
        raw(x, 20, 3)
    housing(21, 2, 11, 8)
    housing(21, 10, 11, 6)
    housing(21, 16, 11, 5)
    put(screen, 22, 3, "PICK 1/2")
    put(screen, 22, 8, "NEXT")
    put(screen, 22, 11, "SCORE")
    put(screen, 22, 14, "CHAIN X")
    put(screen, 22, 17, "GOAL  /  ")
    put(screen, 22, 19, "SPIN  /4")
    put(screen, 25, 0, "RND")
    return ""


def runtime_hook(source):
    """A round advances its goal while preserving board, score, tool and deck."""
    before, tail = source.split("N_ADVANCE:\n", 1)
    _, after = tail.split("N_GAME_INPUT:\n", 1)
    source = (
        before
        + "N_ADVANCE:\n    JSR FN_ADVANCE\n    JMP N_DRAW\nN_GAME_INPUT:\n"
        + after
    )
    result_input = "    LDAB ACTION\n    CMPB #5\n"
    assert source.count(result_input) == 1
    source = source.replace(
        result_input, "    LDAB ACTION\n    CMPB #6\n    BEQ N_RETRY\n    CMPB #5\n"
    )
    retry = "    JSR CONFIRM_RESET\n    TSTA\n    BNE N_NEW_LEVEL\n"
    assert source.count(retry) == 1
    return source.replace(retry, retry.replace("BNE N_NEW_LEVEL", "BNE N_START"))
