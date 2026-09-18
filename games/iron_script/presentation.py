"""An industrial programming panel and a two-rail laser tile; no ROM artwork."""

from art import emit
from artwork import put
from relief import Pixels


def prepare(bank, hud):
    p = Pixels()
    for x in (1, 14):
        p.rect(x - 1, 1, 3, 14, True)
    for y in (5, 10):
        p.line(3, y, 12, y)
    p.shadow()
    bank[224:256] = p.pack()
    doors = []
    for gap in (0, 2, 4, 6):
        panel = Pixels()
        panel.rect(0, 0, 16, 15)
        for x in range(1, 8 - gap):
            panel.line(x, 1, x, 13)
            panel.line(15 - x, 1, 15 - x, 13)
        for x in (2, 13):
            panel.line(x, 3, x, 10, 0)
        panel.shadow()
        doors += panel.pack()
    bank[192:224] = doors[:32]
    for y in range(2, 20):
        hud[y * 32 + 18 : y * 32 + 32] = [64] * 14
    for y in (2, 8, 19):
        put(hud, 18, y, "+" + "-" * 12 + "+")
    for y in range(3, 19):
        put(hud, 31, y, ":")
    for x, y, value in [
        (18, 3, "AMMO"),
        (26, 3, "DIR"),
        (18, 5, "DOOR"),
        (18, 6, "NEXT LASER"),
        (18, 9, "PROGRAM"),
        (28, 9, "/12"),
        (1, 1, "GOAL: DIAMOND / 24 ROOMS"),
        (18, 20, "STEPS"),
    ]:
        put(hud, x, y, value)
    for i in range(12):
        x, y = 18 + i % 4 * 3, 11 + i // 4 * 3
        put(hud, x, y, "[ ]")
        put(hud, x + 1, y - 1, "123456789ABC"[i])
    return emit("FACE_6_FRAMES", doors)
