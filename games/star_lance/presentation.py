"""Compact fighter silhouettes and an uninterrupted combat area."""

from artwork import put
from relief import Pixels


def prepare(bank, hud):
    sprites = []
    for kind in range(4):
        p = Pixels(contact_shadow=False)
        if kind == 2:
            p.poly(
                [
                    (7, 0),
                    (10, 8),
                    (15, 12),
                    (15, 14),
                    (9, 12),
                    (7, 15),
                    (5, 12),
                    (0, 14),
                    (0, 12),
                    (4, 8),
                ],
                True,
            )
            p.line(7, 5, 7, 10, 0)
            p.dot(6, 13, 0)
        else:
            p.poly(
                [
                    (1, 2),
                    (5, 5),
                    (10, 5),
                    (14, 2),
                    (15, 10),
                    (11, 13),
                    (8, 10),
                    (4, 13),
                    (0, 10),
                ],
                True,
            )
            p.rect(5, 6, 6, 3, True, 0)
            p.line(2, 6, 2, 9, 0)
            p.line(13, 6, 13, 9, 0)
            if kind == 1:
                p.poly([(3, 2), (7, 0), (12, 2), (11, 4), (4, 4)], True)
                p.line(6, 2, 9, 2, 0)
            if kind == 3:
                p.line(7, 3, 7, 14)
                p.line(4, 7, 11, 7)
                p.dot(3, 0)
                p.dot(12, 0)
        sprites += p.pack()
    for phase in range(3):
        p = Pixels(contact_shadow=False)
        if phase == 0:
            p.poly(
                [
                    (7, 0),
                    (9, 5),
                    (15, 3),
                    (11, 8),
                    (15, 13),
                    (9, 11),
                    (7, 15),
                    (5, 11),
                    (0, 13),
                    (3, 8),
                    (0, 3),
                    (5, 5),
                ],
                True,
            )
            p.rect(6, 6, 3, 3, True, 0)
        elif phase == 1:
            for x, y, u, v in (
                (6, 5, 3, 1),
                (10, 5, 14, 2),
                (10, 10, 14, 14),
                (5, 10, 1, 14),
                (2, 7, 0, 7),
                (13, 8, 15, 8),
            ):
                p.line(x, y, u, v)
        else:
            for x, y in ((2, 1), (13, 1), (0, 8), (15, 8), (2, 14), (13, 15)):
                p.dot(x, y)
        sprites += p.pack()
    sprites += [24] * 8 + [60, 126, 126, 60, 60, 60, 60, 24]
    sprites += [24, 60, 60, 24, 24, 60, 24, 0] + [0, 24, 60, 24, 24, 60, 60, 24]
    assert len(sprites) == 256
    bank[:] = sprites
    hud[:] = [64] * 768
    put(hud, 0, 0, "STAR LANCE")
    put(hud, 24, 0, "WAVE")
    for x, y in ((2, 3), (30, 5), (0, 11), (31, 16), (4, 18), (25, 17)):
        put(hud, x, y, ".")
    put(hud, 1, 22, "HULL     ENEMIES")
    put(hud, 1, 23, "HEAT [............]")
    return ""


def runtime_hook(source):
    before, after = source.split("N_RENDER:\n", 1)
    _, after = after.split("    JSR COPY\n", 1)
    source = before + "N_RENDER:\n    JSR SL_BACKGROUND\n" + after
    source = source.replace(
        "    JSR FN_ACT\n    JMP N_DRAW", "    JSR FN_ACT\n    JMP FRAME_READY"
    )
    before, after = source.split("N_XY:\n", 1)
    _, after = after.split("N_TEXT:\n", 1)
    source = (
        before
        + """N_XY:
    LDAA N_ARG1
    ASLA
    LDX #SL_ROW_TABLE
    JSR N_INDEX
    LDX 0,X
    LDAA N_ARG0
    JMP N_INDEX
N_TEXT:
"""
        + after
    )
    source = source.replace(
        "    ANDA #3\n    ASLA\n    LDX #SFX_TABLE",
        "    ANDA #7\n    ASLA\n    LDX #SL_SFX_TABLE",
    )
    source = source.replace("FRAMEBUFFER + 21 * 32", "FRAMEBUFFER + 23 * 32")
    return source
