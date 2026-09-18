"""Large station signs: each owns four PCG characters and two lighting poses."""

from art import FONT_ROWS, emit
from artwork import put
from relief import Pixels


def station(char, lit):
    sign = Pixels(contact_shadow=False)
    sign.rect(0, 0, 16, 16, fill=lit)
    rows = bytes.fromhex(FONT_ROWS[char])
    for y, row in enumerate(rows):
        for x in range(5):
            if row & (1 << (4 - x)):
                sign.rect(3 + x * 2, 1 + y * 2, 2, 2, fill=True, value=not lit)
    return sign.pack()


def prepare(bank, hud):
    car = Pixels(contact_shadow=False)
    car.poly([(1, 4), (4, 1), (14, 11), (11, 14)], fill=True)
    car.poly([(4, 5), (5, 4), (10, 9), (9, 10)], fill=True, value=0)
    for x, y in ((2, 7), (7, 2), (8, 13), (13, 8)):
        car.rect(x, y, 2, 2, fill=True)
    frames = emit("FACE_2_FRAMES", bank[64:96] + car.pack())
    for tile, char in enumerate("ABC", 3):
        off, on = station(char, False), station(char, True)
        bank[tile * 32 : tile * 32 + 32] = off
        frames += emit(f"FACE_{tile}_FRAMES", off + on)

    def rail(shape):
        p = Pixels(8, 8, contact_shadow=False)
        if shape in ("straight", "point-straight"):
            p.rect(0, 3, 8, 2, fill=True)
        elif shape == "point-down":
            p.rect(0, 3, 4, 2, fill=True)
        elif shape == "landing":
            p.rect(3, 3, 5, 2, fill=True)
        if shape in ("diagonal", "point-down", "landing"):
            for x in range(8):
                if shape == "diagonal" or (x >= 3 if shape == "point-down" else x <= 3):
                    p.dot(x, x)
                    p.dot(x, x + 1)
        if shape == "straight":
            for x in (1, 5):
                p.line(x, 1, x, 6)
        if shape == "point-straight":
            p.dot(6, 6)
            p.dot(7, 7)
        elif shape == "point-down":
            p.dot(7, 3)
        return [sum(v << (7 - x) for x, v in enumerate(row)) for row in p.p]

    for slot, shape in (
        (24, "point-straight"),
        (25, "point-down"),
        (26, "straight"),
        (27, "diagonal"),
        (30, "landing"),
    ):
        bank[slot * 8 : slot * 8 + 8] = rail(shape)
    put(hud, 7, 3, "[1]")
    put(hud, 16, 8, "[2]")
    for left, y in ((3, 6), (14, 11), (23, 16)):
        put(hud, left, y, "-" * (28 - left))
    for x, y in ((9, 6), (18, 11)):
        for i in range(1, 5):
            hud[(y + i) * 32 + x + i] = 0x7F
        hud[(y + 5) * 32 + x + 5] = 158
    return frames
