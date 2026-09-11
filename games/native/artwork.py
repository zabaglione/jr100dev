"""Authored monochrome scenes, compact sprites and individual screen composition."""

import math

from art import quad_bank, quads, word


class Canvas:
    def __init__(self):
        self.p = [[0] * 64 for _ in range(48)]

    def dot(self, x, y, v=1):
        x, y = round(x), round(y)
        if 0 <= x < 64 and 0 <= y < 48:
            self.p[y][x] = v

    def line(self, x, y, u, v):
        steps = max(abs(round(u - x)), abs(round(v - y)), 1)
        for i in range(steps + 1):
            self.dot(x + (u - x) * i / steps, y + (v - y) * i / steps)

    def rect(self, x, y, w, h, fill=False):
        if fill:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.dot(xx, yy)
        else:
            self.line(x, y, x + w - 1, y)
            self.line(x, y + h - 1, x + w - 1, y + h - 1)
            self.line(x, y, x, y + h - 1)
            self.line(x + w - 1, y, x + w - 1, y + h - 1)

    def circle(self, x, y, r):
        for a in range(180):
            self.dot(
                x + r * math.cos(a * math.pi / 90), y + r * math.sin(a * math.pi / 90)
            )

    def poly(self, points):
        for a, b in zip(points, points[1:]):
            self.line(*a, *b)


def scene(m):
    c = Canvas()
    L, R, C, P = c.line, c.rect, c.circle, c.poly
    if m == "breach":
        for x in (5, 12, 19, 43, 50, 57):
            L(x, 7, x, 35)
        P([(27, 5), (33, 14), (27, 20), (36, 27), (29, 36)])
        for y in (11, 19, 28):
            L(4, y, 22, y)
            L(40, y + 3, 60, y + 3)
        C(17, 22, 7)
        L(17, 22, 17, 17)
        L(17, 22, 21, 24)
    elif m in ("cards", "fan", "chips"):
        for i in range(4):
            x = 7 + i * 11
            y = 13 - abs(i - 1) * 3
            R(x, y, 14, 21)
            C(x + 7, y + 10, 3)
            L(x + 3, y + 3, x + 5, y + 3)
        if m == "cards":
            C(32, 23, 17)
            P([(2, 34), (10, 27), (20, 33), (44, 33), (54, 27), (62, 34)])
        if m == "fan":
            P([(5, 31), (30, 37), (59, 29)])
            C(53, 10, 4)
        if m == "chips":
            for x in (10, 31, 52):
                for y in (30, 33, 36):
                    R(x, y, 10, 3)
    elif m == "submarine":
        for y in (7, 10):
            P(
                [
                    (0, y),
                    (8, y + 2),
                    (17, y),
                    (26, y + 2),
                    (35, y),
                    (44, y + 2),
                    (55, y),
                    (63, y + 2),
                ]
            )
        R(8, 19, 25, 10)
        C(10, 24, 5)
        C(34, 24, 5)
        R(17, 15, 9, 4)
        L(20, 15, 20, 11)
        for x in (14, 22, 30):
            C(x, 23, 2)
        for r in (8, 13, 18):
            for a in range(-45, 46):
                c.dot(
                    36 + r * math.cos(a * math.pi / 180),
                    24 + r * math.sin(a * math.pi / 180),
                )
        P([(0, 38), (10, 34), (21, 38), (29, 35), (40, 39), (50, 34), (63, 38)])
    elif m == "blade":
        P([(4, 34), (49, 9), (59, 7), (54, 15), (11, 39), (4, 34)])
        L(14, 30, 19, 39)
        for x, y in ((11, 15), (32, 29), (49, 31)):
            R(x, y, 7, 7)
            L(x - 2, y + 9, x + 9, y - 2)
    elif m == "dice":
        R(7, 11, 19, 19)
        P([(7, 11), (14, 6), (33, 6), (26, 11)])
        P([(26, 11), (33, 6), (33, 25), (26, 30)])
        for x, y in ((12, 16), (21, 25), (12, 25), (21, 16), (17, 21)):
            R(x, y, 2, 2, True)
        R(38, 19, 19, 19)
        P([(38, 19), (44, 14), (63, 14), (57, 19)])
        R(45, 26, 3, 3, True)
    elif m == "hourglass":
        R(18, 5, 28, 3, True)
        R(18, 37, 28, 3, True)
        P([(21, 8), (22, 17), (31, 23), (22, 29), (21, 37)])
        P([(43, 8), (42, 17), (33, 23), (42, 29), (43, 37)])
        P([(24, 13), (40, 13), (32, 20), (24, 13)])
        P([(25, 35), (32, 29), (39, 35)])
        for y in (24, 26, 28):
            c.dot(32, y)
        for x in (5, 55):
            C(x, 22, 5)
            L(x, 22, x + 3, 19)
    elif m == "robot":
        R(24, 13, 16, 14)
        R(27, 5, 10, 8)
        R(29, 8, 2, 2, True)
        R(34, 8, 2, 2, True)
        P([(24, 16), (18, 20), (13, 15)])
        P([(40, 16), (48, 13), (51, 19)])
        R(24, 28, 5, 8, True)
        R(35, 28, 5, 8, True)
        for x in (3, 13, 44, 54):
            R(x, 37, 7, 5)
            L(x + 2, 39, x + 4, 39)
    elif m == "searchlight":
        P([(4, 35), (30, 12), (58, 35)])
        C(30, 12, 5)
        L(2, 37, 62, 37)
        R(42, 22, 3, 11, True)
        C(43, 19, 3)
        R(11, 23, 9, 14, True)
        R(52, 15, 8, 22, True)
    elif m == "factory":
        P(
            [
                (5, 32),
                (5, 17),
                (15, 10),
                (15, 17),
                (26, 10),
                (26, 17),
                (37, 10),
                (37, 32),
                (5, 32),
            ]
        )
        R(42, 5, 6, 27)
        R(52, 12, 6, 20)
        L(2, 36, 61, 36)
        for x in range(6, 59, 7):
            C(x, 36, 2)
        for x in (10, 20, 30):
            R(x, 21, 4, 5)
    elif m == "furnace":
        R(17, 11, 30, 26)
        R(22, 16, 20, 17)
        R(27, 4, 10, 7)
        P([(24, 29), (28, 19), (31, 26), (36, 18), (40, 29), (35, 32), (24, 29)])
        for x, y in ((5, 10), (55, 8), (7, 28), (55, 30)):
            L(x - 3, y, x + 3, y)
            L(x, y - 3, x, y + 3)
    elif m == "swarm":
        C(32, 23, 5)
        R(30, 21, 4, 4, True)
        for x, y in (
            (9, 9),
            (24, 8),
            (49, 10),
            (58, 20),
            (49, 35),
            (26, 37),
            (9, 32),
            (5, 21),
        ):
            P([(x - 3, y - 2), (x, y + 2), (x + 3, y - 2)])
            c.dot(x - 1, y)
            c.dot(x + 1, y)
    elif m == "constellation":
        for x, y in ((9, 12), (30, 9), (51, 15), (44, 32), (17, 35)):
            L(x - 3, y, x + 3, y)
            L(x, y - 3, x, y + 3)
        P(
            [
                (9, 12),
                (30, 9),
                (51, 15),
                (44, 32),
                (17, 35),
                (9, 12),
                (44, 32),
                (30, 9),
                (17, 35),
            ]
        )
    elif m == "magnet":
        P(
            [
                (13, 8),
                (13, 28),
                (20, 35),
                (43, 35),
                (50, 28),
                (50, 8),
                (40, 8),
                (40, 24),
                (36, 27),
                (27, 27),
                (23, 24),
                (23, 8),
                (13, 8),
            ]
        )
        for x in (13, 40):
            L(x, 16, x + 10, 16)
        R(29, 9, 6, 6)
        L(32, 18, 32, 23)
    elif m == "iceberg":
        P([(3, 27), (14, 16), (24, 23), (34, 5), (44, 17), (52, 12), (62, 27), (3, 27)])
        P([(9, 28), (21, 39), (37, 31), (50, 37), (58, 28)])
        L(34, 5, 30, 24)
        L(34, 5, 40, 24)
    elif m == "prism":
        P([(24, 33), (34, 8), (47, 33), (24, 33)])
        L(1, 17, 30, 22)
        for y in (11, 19, 29, 37):
            L(42, 24, 62, y)
    elif m == "bridge":
        L(3, 27, 61, 27)
        for x in (14, 48):
            L(x, 8, x, 37)
        P([(3, 26), (14, 10), (31, 24), (48, 10), (61, 26)])
        for x in range(17, 46, 4):
            L(x, 18 + abs(31 - x) // 3, x, 27)
        for y in (33, 38):
            P([(0, y), (13, y + 1), (24, y), (39, y + 1), (63, y)])
    elif m == "glyphs":
        for x in (6, 25, 44):
            R(x, 10, 14, 25)
        P([(10, 27), (13, 17), (16, 27), (10, 27)])
        C(32, 22, 4)
        P([(48, 16), (54, 28), (48, 28), (54, 16)])
    elif m == "well":
        for r in (5, 10, 16):
            C(32, 24, r)
        for x, y in ((10, 13), (47, 7), (55, 31), (19, 38)):
            R(x, y, 3, 3, True)
            L(x, y, 32, 24)
    elif m in ("tree", "orchard"):
        trees = (
            [(32, 22, 13)] if m == "tree" else [(12, 22, 8), (32, 17, 9), (52, 23, 8)]
        )
        for x, y, r in trees:
            C(x, y, r)
            R(x - 2, y + 3, 4, 15)
            L(x - 7, y + 20, x + 7, y + 20)
        if m == "tree":
            P([(16, 37), (27, 34), (32, 31), (40, 35), (49, 38)])
    elif m == "orrery":
        C(32, 23, 4)
        for r in (10, 16, 22):
            C(32, 23, r)
        for x, y in ((21, 23), (45, 13), (31, 1), (54, 23)):
            R(x - 2, y - 2, 4, 4, True)
    elif m == "anvil":
        P(
            [
                (6, 18),
                (56, 18),
                (47, 26),
                (36, 26),
                (40, 36),
                (19, 36),
                (24, 25),
                (13, 25),
                (6, 18),
            ]
        )
        P([(30, 6), (39, 10), (35, 17), (26, 13), (30, 6)])
        L(30, 14, 22, 23)
    elif m == "crown":
        P(
            [
                (10, 14),
                (23, 23),
                (31, 8),
                (42, 23),
                (54, 14),
                (49, 34),
                (15, 34),
                (10, 14),
            ]
        )
        R(17, 29, 30, 4)
        C(31, 25, 3)
    elif m == "scales":
        L(32, 8, 32, 37)
        L(13, 12, 51, 12)
        L(23, 38, 41, 38)
        for x in (13, 51):
            L(x, 12, x - 8, 27)
            L(x, 12, x + 8, 27)
            P([(x - 8, 27), (x - 4, 31), (x + 4, 31), (x + 8, 27)])
    elif m == "mosaic":
        for y in range(3):
            for x in range(5):
                R(8 + x * 10, 8 + y * 10, 8, 8)
                if (x + y) % 3 == 0:
                    C(12 + x * 10, 12 + y * 10, 2)
                elif (x + y) % 3 == 1:
                    L(9 + x * 10, 9 + y * 10, 14 + x * 10, 14 + y * 10)
    elif m == "eclipse":
        C(32, 22, 12)
        C(32, 22, 20)
        for a in range(180):
            x, y = 32 + 11 * math.cos(a * math.pi / 90), 22 + 11 * math.sin(
                a * math.pi / 90
            )
            if x < 34:
                L(x, y, 34, y)
        P([(51, 30), (57, 29), (53, 36), (51, 30)])
    elif m == "tunnel":
        for inset in (1, 7, 13, 19):
            R(inset, 5 + inset // 3, 64 - inset * 2, 36 - inset // 2)
        L(1, 40, 27, 19)
        L(63, 40, 37, 19)
    elif m == "bricks":
        for y in range(3):
            for x in range(6 - y):
                R(3 + x * 10 + y * 5, 6 + y * 6, 9, 5)
        R(22, 37, 19, 3, True)
        C(44, 29, 2)
        L(41, 33, 29, 24)
    elif m == "fleet":
        for x, y in ((10, 10), (28, 10), (46, 10), (18, 20), (40, 20)):
            P(
                [
                    (x, y),
                    (x + 4, y - 4),
                    (x + 8, y),
                    (x + 6, y + 3),
                    (x + 2, y + 3),
                    (x, y),
                ]
            )
        P([(25, 38), (32, 28), (39, 38), (32, 35), (25, 38)])
        L(32, 25, 32, 22)
    elif m == "ribbon":
        P(
            [
                (7, 32),
                (7, 12),
                (20, 12),
                (20, 26),
                (35, 26),
                (35, 8),
                (54, 8),
                (54, 32),
                (43, 32),
            ]
        )
        P(
            [
                (10, 32),
                (10, 15),
                (17, 15),
                (17, 29),
                (38, 29),
                (38, 11),
                (51, 11),
                (51, 29),
                (43, 29),
            ]
        )
        R(40, 28, 5, 5)
        C(26, 37, 2)
    elif m == "lander":
        P([(20, 24), (27, 12), (38, 12), (44, 24), (20, 24)])
        R(27, 7, 11, 7)
        L(23, 24, 17, 32)
        L(41, 24, 47, 32)
        L(13, 32, 21, 32)
        L(43, 32, 51, 32)
        P([(29, 25), (32, 35), (36, 25)])
        L(2, 40, 62, 40)
    elif m == "shield":
        P([(18, 9), (32, 4), (46, 9), (44, 27), (32, 39), (20, 27), (18, 9)])
        P([(23, 12), (32, 9), (41, 12), (40, 25), (32, 33), (24, 25), (23, 12)])
        L(4, 12, 18, 18)
        L(6, 26, 20, 23)
        L(48, 18, 61, 10)
    elif m == "pendulum":
        for x, y, a in ((10, 7, 23), (32, 4, -21), (54, 7, 23)):
            C(x, y, 2)
            L(x, y, x + a // 2, y + 24)
            C(x + a // 2, y + 24, 4)
        for x in (6, 28, 50):
            R(x, 38, 10, 3)
    elif m == "tablet":
        P([(13, 7), (47, 7), (51, 12), (49, 37), (14, 37), (11, 29), (13, 7)])
        for y in (14, 22, 30):
            for x in (19, 29, 39):
                P([(x, y + 3), (x + 3, y - 2), (x + 5, y + 3), (x, y + 3)])
    elif m == "dossier":
        R(5, 12, 29, 26)
        R(8, 8, 12, 4)
        R(35, 5, 22, 29)
        C(45, 14, 5)
        P([(39, 27), (40, 22), (45, 20), (50, 22), (52, 27)])
        for y in (19, 24, 29, 34):
            L(9, y, 28, y)
    elif m == "compass":
        C(32, 23, 17)
        C(32, 23, 20)
        P(
            [
                (32, 4),
                (36, 20),
                (52, 23),
                (36, 26),
                (32, 42),
                (28, 26),
                (12, 23),
                (28, 20),
                (32, 4),
            ]
        )
        P([(32, 7), (32, 23), (48, 23)])
    elif m == "mirror":
        R(5, 7, 23, 31)
        R(36, 7, 23, 31)
        R(8, 10, 17, 25)
        R(39, 10, 17, 25)
        P([(12, 30), (17, 18), (22, 30)])
        P([(42, 30), (47, 18), (52, 30)])
        L(23, 5, 41, 40)
        L(29, 18, 34, 18)
        L(29, 26, 34, 26)
    elif m == "nets":
        for x in range(5, 59, 6):
            L(x, 10, x + 4, 36)
        for y in range(10, 38, 5):
            L(5, y, 59, y)
        for x, y in ((18, 20), (39, 29)):
            C(x, y, 4)
            P([(x + 4, y), (x + 10, y - 4), (x + 10, y + 4), (x + 4, y)])
    elif m == "flask":
        P(
            [
                (26, 5),
                (38, 5),
                (38, 17),
                (49, 32),
                (46, 38),
                (18, 38),
                (15, 32),
                (26, 17),
                (26, 5),
            ]
        )
        L(21, 25, 43, 25)
        C(29, 31, 2)
        C(36, 28, 2)
        C(31, 16, 2)
        for x, y in ((7, 15), (54, 11), (55, 32)):
            L(x - 2, y, x + 2, y)
            L(x, y - 2, x, y + 2)
    elif m == "gavel":
        P([(23, 8), (40, 17), (34, 27), (17, 18), (23, 8)])
        P([(27, 23), (14, 38), (9, 35), (24, 20)])
        R(35, 33, 22, 5, True)
        R(40, 29, 13, 4)
    elif m == "metro":
        P([(3, 11), (23, 11), (35, 23), (59, 23)])
        P([(10, 38), (10, 29), (26, 13), (49, 13)])
        P([(32, 4), (32, 36), (54, 36)])
        for x, y in ((10, 11), (23, 11), (35, 23), (49, 13), (32, 36), (54, 36)):
            C(x, y, 3)
    elif m == "cargo":
        P([(4, 27), (60, 27), (54, 38), (15, 38), (4, 27)])
        for x, y in ((13, 17), (24, 17), (35, 17), (24, 7), (46, 17)):
            R(x, y, 10, 10)
            L(x, y, x + 9, y + 9)
        L(2, 41, 62, 41)
    elif m == "garden":
        for y in range(5):
            for x in range(5):
                if 1 <= x <= 3 or 1 <= y <= 3:
                    C(12 + x * 10, 6 + y * 8, 2)
        P([(17, 18), (21, 13), (26, 17)])
    elif m == "safe":
        R(11, 5, 42, 35)
        R(15, 9, 34, 27)
        C(33, 23, 10)
        C(33, 23, 4)
        for x, y in ((33, 13), (43, 23), (33, 33), (23, 23)):
            L(33, 23, x, y)
        R(48, 14, 6, 4)
        R(48, 29, 6, 4)
    elif m == "phase":
        for x, y in ((9, 8), (30, 8), (20, 23), (41, 23)):
            R(x, y, 14, 13)
            L(x + 3, y + 6, x + 10, y + 6)
        L(26, 7, 26, 37)
        L(6, 22, 57, 22)
    elif m == "switchboard":
        R(5, 6, 54, 33)
        for y in (12, 22, 32):
            for x in (12, 25, 38, 51):
                C(x, y, 3)
                L(x - 2, y + 1, x + 2, y - 1)
        L(12, 12, 25, 22)
        L(25, 22, 51, 32)
    elif m == "sand":
        P([(2, 34), (20, 11), (37, 34), (2, 34)])
        P([(28, 36), (46, 9), (63, 36)])
        for x, y in ((13, 28), (20, 24), (24, 29), (44, 20), (48, 24), (51, 29)):
            c.dot(x, y)
        L(1, 39, 62, 39)
        L(7, 41, 55, 41)
    elif m == "typewriter":
        R(14, 5, 36, 16)
        R(7, 22, 50, 17)
        R(10, 19, 44, 4)
        for y in (26, 31):
            for x in range(13, 53, 6):
                R(x, y, 4, 3)
        L(24, 36, 43, 36)
        L(19, 10, 45, 10)
        L(19, 15, 39, 15)
    else:
        raise ValueError(m)
    return c


def put(screen, x, y, value):
    assert x >= 0 and x + len(value) <= 32 and 0 <= y < 24, (x, y, value)
    screen[y * 32 + x : y * 32 + x + len(value)] = [
        64 if ch == " " else ord(ch) - 32 for ch in value
    ]


def title(info):
    original = scene(info["motif"]).p
    canvas = Canvas()
    words = info["title"].split()
    layout = sum(map(ord, info["id"])) % 5
    special = {
        "chrono-breach": 2,
        "sigil-deck": 0,
        "abyss-signal": 3,
        "trace-blade": 2,
        "dice-relic": 1,
        "loop-ten": 4,
    }
    layout = special.get(info["id"], layout)
    if layout == 4 and max(map(len, words)) > 5:
        layout = 2

    def paste(sx, sy, ox, oy):
        for y, row in enumerate(original):
            for x, value in enumerate(row):
                if value:
                    canvas.dot(ox + x * sx, oy + y * sy)

    def lettering(value, x, y):
        # Opaque cartouche keeps the lettering separate from the illustration.
        for yy in range(y - 1, y + 8):
            for xx in range(x - 1, x + len(value) * 6):
                canvas.dot(xx, yy, 0)
        word(canvas.p, value, y, x)

    if layout == 0:
        paste(0.84, 0.50, 5, 10)
        lettering(words[0], (64 - len(words[0]) * 6 + 1) // 2, 1)
        lettering(words[-1], (64 - len(words[-1]) * 6 + 1) // 2, 34)
    elif layout == 1:
        paste(1, 0.72, 0, 0)
        lettering(words[0], 2, 25)
        lettering(words[-1], max(2, 62 - len(words[-1]) * 6), 34)
    elif layout == 2:
        paste(0.70, 0.85, 18, 1)
        lettering(words[0], 2, 25)
        lettering(words[-1], 2, 34)
    elif layout == 3:
        paste(0.82, 0.52, 11, 18)
        lettering(words[0], 2, 1)
        lettering(words[-1], 2, 10)
    else:
        paste(0.46, 0.84, 0, 2)
        lettering(words[0], 32, 10)
        lettering(words[-1], 32, 25)
    screen = quads(canvas.p)
    if info["id"] == "chrono-breach":
        put(screen, 10, 22, "SECTOR")
    put(screen, 3, 21, "RETURN / BUTTON : START")
    put(screen, 3, 23, "SPACE : GUIDE   CTRL+C EXIT")
    return quad_bank(), screen


def sprite_bank(info):
    # Eight 16x16 glyphs. Character silhouettes follow the game's setting.
    motif = info["motif"]
    bank = []
    for k in range(8):
        p = [[0] * 16 for _ in range(16)]
        for y in range(16):
            for x in range(16):
                if k == 0:
                    v = (x, y) == (7, 7)
                elif k == 1:
                    v = x in (0, 15) or y in (0, 15) or (y == 7 and x % 8 < 6)
                elif k == 2:
                    if info["genre"] == "action":
                        v = (abs(x - 7) <= y // 2 and y < 12) or (
                            y > 11 and x in (3, 4, 10, 11)
                        )
                    elif info["genre"] == "tabletop":
                        v = 20 <= (x - 7) ** 2 + (y - 7) ** 2 <= 42 or (
                            5 <= x <= 9 and 5 <= y <= 9
                        )
                    else:
                        v = (
                            (4 <= x <= 10 and 2 <= y <= 5)
                            or (3 <= x <= 11 and 7 <= y <= 11)
                            or (y >= 12 and x in (4, 5, 9, 10))
                        )
                elif k == 3:
                    v = abs(x - 7) + abs(y - 7) in (5, 6) or (x == 7 and y in (6, 7, 8))
                elif k == 4:
                    v = (
                        2 <= x <= 13
                        and 2 <= y <= 13
                        and (
                            x in (2, 3, 12, 13)
                            or y in (2, 3, 12, 13)
                            or x == y
                            or x + y == 15
                        )
                    )
                elif k == 5:
                    v = (
                        2 <= x <= 13
                        and 3 <= y <= 11
                        and not (5 <= y <= 7 and x in (4, 5, 10, 11))
                    ) or (y > 11 and x in (3, 6, 9, 12))
                elif k == 6:
                    v = x in (1, 4, 11, 14) or y in (1, 14) or (x == 7 and 5 <= y <= 10)
                else:
                    v = (x in (0, 15) and (y < 3 or y > 12)) or (
                        y in (0, 15) and (x < 3 or x > 12)
                    )
                if info["id"] in ("five-forge", "corner-crown") and k in (2, 5):
                    if info["id"] == "five-forge":
                        v = (
                            (28 <= (x - 7) ** 2 + (y - 7) ** 2 <= 43)
                            if k == 2
                            else (abs(x - y) <= 1 or abs(x + y - 15) <= 1)
                            and 2 <= x <= 13
                            and 2 <= y <= 13
                        )
                    else:
                        v = (
                            (x - 7) ** 2 + (y - 7) ** 2 <= 40
                            if k == 2
                            else 28 <= (x - 7) ** 2 + (y - 7) ** 2 <= 43
                        )
                if k == 4 and motif in ("iceberg", "prism", "constellation"):
                    v = abs(x - 7) + abs(y - 7) <= 6 and (
                        x in (6, 7, 8) or y in (6, 7, 8) or x == y or x + y == 14
                    )
                if k == 4 and motif in ("tree", "orchard", "garden"):
                    v = (x - 7) ** 2 + (y - 5) ** 2 <= 21 or (
                        x in (6, 7, 8) and 6 <= y <= 14
                    )
                if k == 4 and motif in ("flask", "nets", "sand"):
                    v = abs(x - 7) <= min(y, 14 - y) // 2 and 2 <= y <= 13
                if motif == "prism" and k in (4, 5):
                    v = (abs(x + y - 15) <= 1) if k == 4 else (abs(x - y) <= 1)
                if motif == "well" and k == 4:
                    v = (x - 7) ** 2 + (y - 7) ** 2 <= 37 and not (x < 6 and y < 6)
                if motif == "furnace" and k == 3:
                    v = (2 <= y <= 13 and abs(x - 7) <= min(y // 2, 14 - y)) or (
                        x == 9 and 1 <= y <= 4
                    )
                if motif == "ribbon" and k == 4:
                    v = (
                        2 <= x <= 13
                        and 2 <= y <= 13
                        and (y not in (6, 10) or x % 4 < 2)
                    )
                if motif == "ribbon" and k == 2:
                    v = (x - 7) ** 2 + (y - 7) ** 2 <= 46 and not (
                        y in (4, 5) and x in (4, 5, 10, 11)
                    )
                if motif in ("chips", "fan") and k == 7:
                    v = x in (0, 15) or y in (0, 15)
                if motif == "shield" and k == 5:
                    v = (3 <= x <= 12 and 2 <= y <= 10) or (
                        y > 10 and abs(x - 7) < 15 - y
                    )
                if motif == "shield" and k == 2:
                    v = (
                        (3 <= x <= 11 and 3 <= y <= 8)
                        or (6 <= y <= 13 and x in (4, 5, 10, 11))
                        or (x >= 12 and y == 5)
                    )
                if motif == "shield" and k == 6:
                    v = (
                        (2 <= y <= 11 and x in (2, 3, 12, 13))
                        or (y == 2 and 3 <= x <= 12)
                        or (y >= 11 and abs(x - 7) == 14 - y)
                    )
                p[y][x] = int(v)
        bank += [
            sum(p[y + dy][x + dx] << (7 - dx) for dx in range(8))
            for y in (0, 8)
            for x in (0, 8)
            for dy in range(8)
        ]
    return bank
