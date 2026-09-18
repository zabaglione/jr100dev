"""A semi-graphic desert highway and a four-character running/jumping actor."""

from art import emit
from artwork import put
from relief import Pixels
from title_styles import ROM_QUADS


def prepare(bank, hud):
    glyphs = [
        [255, 128, 191, 160, 175, 168, 171, 170],
        [170, 128, 191, 160, 175, 168, 171, 170],
        [0, 128, 192, 160, 208, 168, 212, 170],
        [0, 0, 255, 255, 255, 255, 255, 255],
        [255, 128, 128, 128, 128, 128, 128, 255],
        [24, 24, 24, 24, 24, 24, 24, 24],
        [0, 0, 0, 0, 0, 0, 0, 85],
        [0, 0, 85, 170, 85, 0, 0, 0],
    ]
    bank[:] = [byte for glyph in glyphs for byte in glyph] + [0] * 192
    poses = []
    for pose in range(3):
        p = Pixels(contact_shadow=False)
        p.ellipse(7, 3, 3, 3, True)
        p.line(5, 2, 8, 2, 0)
        p.rect(4, 7, 7, 6, True)
        p.line(8, 8, 8, 11, 0)
        if pose == 2:
            p.line(1, 5, 4, 9)
            p.line(11, 9, 14, 5)
            p.line(4, 12, 2, 14)
            p.line(10, 12, 13, 13)
        else:
            p.line(1, 8 + pose * 3, 4, 9)
            p.line(10, 9, 14, 11 - pose * 3)
            p.line(5, 12, 3 + pose * 3, 15)
            p.line(10, 12, 12 - pose * 3, 15)
        poses += p.pack()
    bank[64:96] = poses[:32]
    jewel = Pixels(contact_shadow=False)
    jewel.poly([(7, 1), (13, 7), (7, 14), (1, 7)], True)
    jewel.line(7, 3, 4, 7, 0)
    jewel.line(3, 8, 6, 11, 0)
    bank[128:160] = jewel.pack()

    canvas = Pixels(64, 48, contact_shadow=False)
    # Echo the title's converging road and angular structures at the horizon.
    canvas.line(0, 39, 27, 10)
    canvas.line(63, 39, 36, 10)
    canvas.line(27, 10, 36, 10)
    for x, height in ((0, 10), (9, 7), (18, 4), (45, 5), (55, 9)):
        canvas.poly(
            [(x, 16), (x, 16 - height), (x + 5, 13 - height), (x + 5, 16)], True
        )
        canvas.line(x + 2, 15 - height, x + 2, 15, 0)
    for x, y in ((2, 25), (12, 20), (48, 22), (57, 30), (4, 35)):
        canvas.line(x, y, x + 5, y)
        canvas.line(x + 5, y, x + 7, y + 2)
    hud[:] = [64] * 768
    for y in range(3, 21):
        for x in range(32):
            quad = sum(
                canvas.p[y * 2 + dy][x * 2 + dx] << (dy * 2 + dx)
                for dy in range(2)
                for dx in range(2)
            )
            hud[y * 32 + x] = ROM_QUADS[quad]
    put(hud, 0, 0, "GATE RUNNER")
    put(hud, 23, 0, "STAGE")
    put(hud, 0, 1, "HULL")
    put(hud, 1, 22, "GATES   /12  CRYSTALS   /12")
    return emit("FACE_2_FRAMES", poses)
