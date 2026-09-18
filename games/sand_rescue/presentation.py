"""Six irrigation fields; PCG contains channels, gates and growing crops."""

from artwork import put
from relief import Pixels


def prepare(bank, hud):
    glyphs = [
        [66] * 8,
        [66, 66, 66, 67, 64, 64, 127, 0],
        [0, 254, 2, 2, 194, 66, 66, 66],
        [24, 126, 66, 126, 126, 126, 66, 66],
        [66, 90, 102, 66, 90, 102, 66, 66],
        [66, 102, 90, 66, 102, 90, 66, 66],
        [24, 126, 126, 66, 66, 66, 66, 66],
        [128, 80, 40, 84, 10, 21, 2, 1],
    ]
    data = [byte for glyph in glyphs for byte in glyph]
    for kind in ("seed", "root", "leaf", "fruit"):
        p = Pixels()
        p.poly([(1, 12), (5, 10), (14, 11), (11, 14), (1, 14)], True)
        p.line(3, 13, 10, 13, 0)
        p.line(7, 11, 7, 6)
        p.poly([(7, 8), (2, 4), (5, 3), (7, 6)], True)
        p.poly([(7, 7), (11, 2), (14, 3), (10, 7)], True)
        if kind != "seed":
            p.line(7, 8, 7, 2)
            p.poly([(6, 8), (1, 7), (2, 9), (6, 10)], True)
            p.poly([(8, 8), (13, 6), (14, 8), (9, 10)], True)
        if kind == "root":
            p.ellipse(7, 10, 4, 3, True)
            p.dot(5, 9, 0)
            p.dot(9, 11, 0)
        elif kind == "fruit":
            p.ellipse(4, 5, 3, 3, True)
            p.ellipse(11, 7, 3, 3, True)
            p.dot(3, 4, 0)
            p.dot(10, 6, 0)
        p.shadow()
        data += p.pack()
    p = Pixels(contact_shadow=False)
    for x, y in ((2, 2), (10, 3), (6, 7), (13, 10), (3, 12)):
        p.line(x, y, x, y + 2)
    data += p.pack()
    data += [
        byte
        for glyph in (
            [0, 0, 255, 0, 0, 255, 0, 0],
            [0, 0, 255, 85, 170, 255, 0, 0],
            [66, 66, 66, 126, 60, 24, 0, 0],
            [66, 90, 102, 126, 60, 24, 0, 0],
        )
        for byte in glyph
    ]
    assert len(data) == 256
    bank[:] = data
    hud[:] = [64] * 768
    put(hud, 0, 0, "SAND RESCUE")
    put(hud, 23, 0, "FIELD")
    put(hud, 0, 1, "WATER      HARVEST")
    put(hud, 21, 1, "/")
    put(hud, 1, 3, "TANK")
    put(hud, 20, 3, "  /9")
    put(hud, 25, 3, "POUR")
    for x in range(2, 24):
        hud[4 * 32 + x] = 0x6E
    for x in (9, 19):
        hud[3 * 32 + x] = 0x71
    for i in range(3):
        put(hud, 4 + i * 10, 5, chr(65 + i))
    for x in (0, 10, 20, 31):
        for y in range(7, 20):
            hud[y * 32 + x] = 0x7F if y % 4 == 0 else 0x0E
    for x in range(32):
        hud[23 * 32 + x] = 0x6E
    return ""


def runtime_hook(source):
    # Keep the checkpoint at d[120:122] across the stage-local clear/load.
    source = source.replace("CPX #$3780", "CPX #$3740")
    source = source.replace("    LDX #128\n", "    LDX #64\n")
    source = source.replace("N_ADVANCE:\n", "N_ADVANCE:\n    JSR FN_CHECKPOINT\n")
    # Reset the shared budget, not just the current field.
    return source.replace("BNE N_NEW_LEVEL\nN_DRAW:", "BNE N_START\nN_DRAW:")
