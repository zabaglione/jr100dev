"""Per-game title posters. Composition is authored, never selected by a hash."""

import math

from art import FONT_ROWS, quad_bank, quads
from title_styles import FINISH_FOR, finish_bank


class Canvas:
    def __init__(self, height=40):
        self.p = [[0] * 64 for _ in range(height)]
        self.titles = []

    def dot(self, x, y, ink=1):
        x, y = round(x), round(y)
        if 0 <= x < 64 and 0 <= y < len(self.p):
            self.p[y][x] = ink

    def line(self, x, y, u, v, ink=1):
        count = max(abs(round(u - x)), abs(round(v - y)), 1)
        for i in range(count + 1):
            self.dot(x + (u - x) * i / count, y + (v - y) * i / count, ink)

    def box(self, x, y, w, h, fill=False, ink=1):
        if fill:
            for yy in range(y, y + h):
                for xx in range(x, x + w):
                    self.dot(xx, yy, ink)
        else:
            for a, b in [
                ((x, y), (x + w - 1, y)),
                ((x, y), (x, y + h - 1)),
                ((x + w - 1, y), (x + w - 1, y + h - 1)),
                ((x, y + h - 1), (x + w - 1, y + h - 1)),
            ]:
                self.line(*a, *b, ink)

    def poly(self, points, fill=False, ink=1):
        for a, b in zip(points, points[1:] + points[:1]):
            self.line(*a, *b, ink)
        if fill:
            for y in range(min(p[1] for p in points), max(p[1] for p in points) + 1):
                hits = []
                for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
                    if y1 != y2 and min(y1, y2) <= y < max(y1, y2):
                        hits.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
                hits.sort()
                for a, b in zip(hits[::2], hits[1::2]):
                    self.line(math.ceil(a), y, math.floor(b), y, ink)

    def circle(self, x, y, r, fill=False, ink=1):
        for yy in range(y - r, y + r + 1):
            for xx in range(x - r, x + r + 1):
                d = (xx - x) ** 2 + (yy - y) ** 2
                if d <= r * r and (fill or d >= (r - 1) ** 2):
                    self.dot(xx, yy, ink)

    def diamond(self, x, y, r, fill=False, ink=1):
        self.poly([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill, ink)

    def label(self, value, x, y, style="plain", wide=1, tall=1, ink=1):
        if ink:
            self.titles.append((value, x, y, style, wide, tall))
            return
        self.paint_label(value, x, y, style, wide, tall, ink)

    def paint_label(self, value, x, y, style, wide, tall, ink=1):
        width = (len(value) * 6 - 1) * wide + (2 if style == "speed" else 0)
        assert x >= 0 and y >= 0 and x + width <= 64 and y + 7 * tall <= len(self.p), (
            value,
            x,
            y,
            width,
        )
        for index, char in enumerate(value):
            rows = bytes.fromhex(FONT_ROWS[char])
            for row, bits in enumerate(rows):
                if style == "slab" and row in (0, 6):
                    bits |= ((bits << 1) | (bits >> 1)) & 31
                for col in range(5):
                    if bits & (16 >> col):
                        shear = (6 - row) // 3 if style == "speed" else 0
                        self.box(
                            x + (index * 6 + col) * wide + shear,
                            y + row * tall,
                            wide,
                            tall,
                            True,
                            ink,
                        )

    def stars(self, points):
        for x, y in points:
            self.line(x - 1, y, x + 1, y)
            self.line(x, y - 1, x, y + 1)

    def card(self, x, y, w, h, kind=0):
        self.box(x, y, w, h, True)
        self.box(x + 1, y + 1, w - 2, h - 2, True, 0)
        cx, cy = x + w // 2, y + h // 2
        if kind == 0:
            self.diamond(cx, cy, 3, True)
        elif kind == 1:
            self.circle(cx - 2, cy - 1, 2, True)
            self.circle(cx + 2, cy - 1, 2, True)
            self.poly([(cx - 4, cy), (cx + 4, cy), (cx, cy + 5)], True)
        else:
            self.line(cx - 3, cy, cx + 3, cy)
            self.line(cx, cy - 3, cx, cy + 3)

    def gear(self, x, y, r):
        self.circle(x, y, r, True)
        self.circle(x, y, r - 2, True, 0)
        for dx, dy in [(r, 0), (-r, 0), (0, r), (0, -r)]:
            self.box(x + dx - 1, y + dy - 1, 3, 3, True)


def poster(info):
    c = Canvas()
    g = info["id"]
    B, L, C, P, D, T = c.box, c.line, c.circle, c.poly, c.diamond, c.label
    # Each branch has its own hierarchy, title placement and recognisable scene.
    if g == "chrono-breach":
        B(0, 0, 18, 40, True)
        B(2, 3, 12, 14, False, 0)
        for y in (5, 9, 13):
            L(4, y, 12, y, 0)
        P([(20, 0), (26, 7), (21, 15), (29, 22), (23, 30), (28, 39)])
        C(49, 12, 9)
        L(49, 12, 49, 5)
        L(49, 12, 55, 15)
        T("CHRONO", 25, 25)
        T("BREACH", 25, 33)
        for x, y in [(4, 23), (9, 29), (4, 35)]:
            B(x, y, 5, 2, True, 0)
    elif g == "sigil-deck":
        C(46, 22, 16)
        C(46, 22, 13)
        for x, y in [(31, 10), (58, 9), (31, 34), (59, 33)]:
            D(x, y, 2, True)
        c.card(34, 12, 15, 22, 0)
        c.card(45, 8, 15, 22, 2)
        T("SIGIL", 1, 3, "slab")
        T("DECK", 1, 13, "slab", tall=2)
        L(2, 32, 26, 32)
        D(14, 35, 2)
    elif g == "abyss-signal":
        T("ABYSS", 3, 2, wide=2)
        T("SIGNAL", 26, 12)
        for x in range(0, 64, 4):
            L(x, 21, x + 2, 21)
        P(
            [
                (0, 38),
                (9, 33),
                (15, 35),
                (21, 30),
                (26, 38),
                (42, 38),
                (49, 28),
                (55, 31),
                (63, 26),
                (63, 39),
                (0, 39),
            ],
            True,
        )
        B(6, 25, 19, 5, True)
        P([(25, 25), (30, 27), (25, 29)], True)
        B(12, 23, 7, 2, True)
        L(15, 23, 15, 20)
        for x in (10, 16, 22):
            c.dot(x, 27, 0)
        for x, y in [(35, 24), (41, 22), (47, 20)]:
            L(x, y, x, y + 5)
    elif g == "trace-blade":
        T("TRACE", 1, 1, "speed")
        T("BLADE", 31, 9, "speed")
        for x, y in [(4, 23), (17, 31), (32, 24), (49, 30)]:
            D(x, y, 3)
        P([(2, 36), (14, 26), (22, 34), (36, 20), (49, 32), (62, 20)])
        P([(7, 39), (52, 16), (62, 14), (56, 21)], True)
        L(13, 33, 17, 39)
    elif g == "dice-relic":
        T("DICE", 3, 1, "slab", wide=2)
        T("RELIC", 33, 31, "slab")
        P([(5, 17), (18, 12), (30, 18), (17, 24)], True)
        P([(5, 18), (17, 25), (17, 38), (5, 31)])
        P([(19, 25), (31, 18), (31, 31), (19, 38)])
        for x, y in [(13, 18), (20, 17), (18, 20)]:
            c.dot(x, y, 0)
        for x, y in [(9, 24), (13, 32), (24, 28)]:
            B(x, y, 2, 2, True)
        C(48, 20, 7)
        D(48, 20, 4)
        c.stars([(36, 10), (60, 18)])
    elif g == "loop-ten":
        C(19, 20, 17)
        C(19, 20, 14)
        P([(4, 3), (5, 14), (14, 8)], True)
        P([(34, 37), (32, 26), (24, 32)], True)
        T("10", 8, 13, wide=2)
        T("LOOP", 38, 7)
        T("TEN", 43, 24, tall=2)
        for x in (38, 44, 50, 56, 62):
            c.dot(x, 20)
    elif g == "iron-script":
        T("IRON", 1, 2, wide=2)
        T("SCRIPT", 26, 31)
        B(4, 15, 16, 13, True)
        B(7, 12, 10, 3, True)
        B(7, 18, 3, 3, True, 0)
        B(14, 18, 3, 3, True, 0)
        L(9, 24, 15, 24, 0)
        B(3, 29, 6, 7, True)
        B(15, 29, 6, 7, True)
        for x, y in [(29, 13), (41, 13), (53, 13)]:
            B(x, y, 9, 9)
            P([(x + 2, y + 3), (x + 6, y + 3), (x + 4, y + 6)], True)
        L(27, 25, 58, 25)
        D(58, 25, 2)
    elif g == "chain-suit":
        for x, y, k in [(2, 11, 0), (19, 15, 1), (36, 11, 2)]:
            c.card(x, y, 14, 20, k)
        L(14, 26, 21, 26)
        L(31, 26, 39, 26)
        T("CHAIN", 2, 1, wide=2)
        T("SUIT", 40, 32)
        D(58, 6, 3, True)
        D(58, 15, 3)
    elif g == "quiet-route":
        for x, h in [(0, 12), (9, 18), (18, 10), (47, 17), (57, 24)]:
            B(x, 40 - h, 7, h, True)
        P([(24, 38), (37, 17), (45, 38)], True)
        B(35, 30, 4, 8, True, 0)
        T("QUIET", 1, 1)
        T("ROUTE", 25, 10)
        C(57, 4, 3)
        C(59, 3, 3, True, 0)
        for x, y in [(25, 36), (27, 33), (29, 30)]:
            c.dot(x, y, 0)
    elif g == "circuit-works":
        T("CIRCUIT", 2, 4)
        T("WORKS", 26, 29)
        B(18, 17, 25, 7, True)
        T("AND", 21, 17, ink=0)
        for x, y in [(2, 16), (2, 25), (51, 20)]:
            B(x, y, 5, 5)
        P([(7, 18), (12, 18), (12, 20), (18, 20)])
        P([(7, 27), (14, 27), (14, 23), (18, 23)])
        L(43, 20, 51, 20)
        for x in (5, 11, 17, 23):
            B(x, 32, 3, 3, True)
        L(2, 0, 62, 0)
    elif g == "hearth-zero":
        T("HEARTH", 2, 1, "slab")
        T("ZERO", 38, 29, "slab")
        B(0, 12, 31, 28, True)
        B(4, 16, 23, 24, True, 0)
        P(
            [
                (8, 37),
                (6, 30),
                (12, 24),
                (14, 16),
                (20, 27),
                (21, 23),
                (25, 33),
                (21, 37),
            ],
            True,
        )
        P([(13, 36), (15, 28), (19, 34), (18, 37)], True, 0)
        for x, y in [(40, 14), (55, 4), (59, 21), (33, 21)]:
            c.stars([(x, y)])
        for y in range(14, 37, 5):
            L(0, y, 3, y, 0)
            L(28, y, 30, y, 0)
    elif g == "night-swarm":
        T("NIGHT", 16, 3, "speed")
        T("SWARM", 16, 13, "speed")
        for x, y in [
            (2, 2),
            (54, 1),
            (3, 19),
            (53, 21),
            (14, 30),
            (44, 31),
            (0, 35),
            (58, 35),
        ]:
            P(
                [(x, y), (x + 3, y + 2), (x + 6, y), (x + 5, y + 4), (x + 1, y + 4)],
                True,
            )
            c.dot(x + 2, y + 2, 0)
            c.dot(x + 4, y + 2, 0)
        C(32, 34, 5)
        D(32, 34, 2, True)
        for x, y in [(27, 27), (38, 27), (24, 34), (40, 36)]:
            c.dot(x, y)
    elif g == "lumen-cross":
        B(7, 3, 10, 31, True)
        B(0, 13, 31, 10, True)
        B(10, 6, 4, 25, True, 0)
        B(3, 16, 25, 4, True, 0)
        T("LUMEN", 33, 2)
        T("CROSS", 33, 12)
        for x, y in [(36, 29), (48, 24), (57, 33)]:
            D(x, y, 3)
        L(31, 38, 62, 38)
        c.stars([(49, 36)])
    elif g == "magnet-vault":
        B(2, 2, 30, 27, True)
        B(8, 2, 18, 19, True, 0)
        B(2, 2, 6, 7, True, 0)
        B(26, 2, 6, 7, True, 0)
        B(3, 3, 4, 4, True)
        B(27, 3, 4, 4, True)
        for x, y in [(42, 1), (52, 7), (40, 12)]:
            B(x, y, 7, 7)
            B(x + 2, y + 2, 3, 3, True)
        L(32, 11, 38, 8)
        L(32, 18, 38, 20)
        T("MAGNET", 1, 32)
        T("VAULT", 34, 23)
    elif g == "frost-steps":
        T("FROST", 2, 1, wide=2)
        T("STEPS", 2, 11)
        for x, y in [(2, 34), (14, 30), (26, 26), (38, 22), (50, 18)]:
            P([(x, y), (x + 9, y), (x + 12, y + 3), (x + 3, y + 3)], True)
            L(x + 4, y + 2, x + 9, y + 2, 0)
        D(52, 13, 4)
        L(52, 9, 52, 17)
        c.stars([(37, 13), (45, 5), (5, 24)])
    elif g == "prism-trace":
        T("PRISM", 1, 1)
        T("TRACE", 32, 32)
        P([(29, 12), (17, 29), (45, 29)], False)
        L(0, 21, 24, 21)
        L(24, 21, 37, 22)
        for end in (12, 19, 27):
            L(37, 22, 63, end)
        L(29, 12, 30, 26)
        c.stars([(8, 32), (46, 3)])
    elif g == "tide-bridge":
        T("TIDE", 1, 2, wide=2)
        T("BRIDGE", 27, 12)
        B(1, 24, 62, 3, True)
        for x in (5, 21, 37, 53):
            B(x, 27, 6, 12, True)
        for x in (12, 28, 44):
            C(x, 33, 5, True, 0)
        for y in (31, 36):
            for x in range(0, 64, 9):
                L(x, y, x + 5, y)
        B(4, 19, 2, 5, True)
        L(5, 19, 8, 21)
    elif g == "glyph-shift":
        T("GLYPH", 2, 2, "slab")
        T("SHIFT", 26, 31, "slab")
        for x, y in [(3, 17), (25, 13), (47, 8)]:
            B(x, y, 13, 13, True)
            D(x + 6, y + 6, 4, False, 0)
            L(x + 3, y + 6, x + 9, y + 6, 0)
        P([(18, 27), (22, 23), (18, 23)])
        P([(40, 22), (44, 18), (40, 18)])
        L(1, 38, 20, 38)
    elif g == "gravity-well":
        C(44, 24, 13, True)
        C(44, 24, 8, True, 0)
        for r in (16, 19):
            for angle in range(200, 341, 4):
                c.dot(
                    44 + r * math.cos(angle * math.pi / 180),
                    24 + r * 0.55 * math.sin(angle * math.pi / 180),
                )
        C(24, 18, 3, True)
        C(15, 28, 2)
        C(31, 35, 2, True)
        T("GRAVITY", 1, 1)
        T("WELL", 1, 10)
        L(1, 37, 18, 37)
    elif g == "seed-merge":
        B(0, 34, 64, 2, True)
        for x, y, r in [(4, 29, 2), (16, 25, 4), (33, 22, 6), (52, 16, 10)]:
            B(x - 1, y, 3, 34 - y, True)
            C(x, y, r, True)
            L(x, y - 2, x, y + 3, 0)
        T("SEED", 1, 1)
        T("MERGE", 1, 10)
        for x in (8, 26, 43):
            P([(x, 38), (x + 4, 38), (x + 3, 37)])
    elif g == "orbit-draft":
        C(30, 19, 17)
        C(30, 19, 11)
        for x, y, k in [(9, 5, 0), (43, 2, 2), (44, 23, 1)]:
            c.card(x, y, 10, 15, k)
        T("ORBIT", 2, 1)
        T("DRAFT", 2, 27)
        D(30, 19, 3, True)
    elif g == "five-forge":
        T("FIVE", 3, 1, "slab", wide=2)
        T("FORGE", 34, 30, "slab")
        P(
            [
                (1, 16),
                (34, 16),
                (28, 21),
                (18, 21),
                (18, 29),
                (27, 32),
                (5, 32),
                (11, 28),
                (11, 21),
                (4, 21),
            ],
            True,
        )
        for x in (4, 10, 16, 22, 28):
            C(x, 13, 2, True)
        B(38, 11, 17, 5, True)
        P([(50, 16), (53, 16), (45, 27), (42, 27)], True)
        c.stars([(35, 19), (33, 24), (60, 21)])
    elif g == "corner-crown":
        T("CORNER", 1, 1)
        T("CROWN", 34, 31)
        B(2, 11, 25, 25)
        for x in (8, 14, 20):
            L(x, 11, x, 35)
        for y in (17, 23, 29):
            L(2, y, 26, y)
        for x, y in [(5, 14), (23, 14), (5, 32), (23, 32)]:
            B(x - 1, y - 1, 3, 3, True)
        P([(35, 15), (40, 21), (46, 12), (52, 21), (59, 15), (56, 29), (38, 29)], True)
        B(40, 31, 15, 2, True)
    elif g == "stone-balance":
        T("STONE", 2, 1, "slab")
        T("BALANCE", 2, 32, "slab")
        P([(8, 21), (32, 15), (56, 20)])
        B(31, 15, 3, 15, True)
        L(21, 30, 44, 30)
        for x, y in [(8, 21), (56, 20)]:
            L(x, y, x, y + 5)
            L(x - 6, y + 5, x + 6, y + 5)
        for x, y, r in [(3, 18, 2), (8, 17, 3), (14, 17, 2), (56, 13, 5)]:
            C(x, y, r, True)
    elif g == "memory-mosaic":
        T("MEMORY", 2, 2)
        T("MOSAIC", 25, 31)
        for x, y, k in [(3, 14, 0), (16, 14, 2), (29, 14, 1), (42, 14, 0), (52, 1, 1)]:
            B(x, y, 10, 12)
            if k == 0:
                D(x + 5, y + 6, 3, True)
            elif k == 1:
                C(x + 5, y + 6, 3)
            else:
                B(x + 2, y + 3, 6, 6, True)
        L(8, 28, 47, 28)
        c.dot(8, 27)
        c.dot(47, 27)
    elif g == "twenty-one":
        B(0, 0, 64, 2, True)
        c.card(3, 8, 17, 24, 1)
        c.card(13, 12, 17, 24, 0)
        T("21", 34, 4, wide=2, tall=2)
        T("TWENTY", 27, 22)
        T("ONE", 39, 32)
        for x in (2, 8, 14, 20):
            L(x, 39, x + 2, 39)
    elif g == "orbit-dodge":
        C(20, 19, 17)
        C(20, 19, 9, True)
        C(23, 17, 8, True, 0)
        P([(31, 5), (35, 12), (28, 11)], True)
        for x, y in [(3, 7), (5, 32), (28, 34)]:
            D(x, y, 2, True)
        T("ORBIT", 32, 19)
        T("DODGE", 32, 29, "speed")
        L(44, 1, 44, 12)
        L(52, 3, 52, 9)
        L(60, 0, 60, 14)
    elif g == "gate-runner":
        T("GATE", 1, 1, wide=2)
        T("RUNNER", 25, 11, "speed")
        P([(0, 39), (28, 22), (36, 22), (63, 39)])
        L(31, 22, 21, 39)
        L(33, 22, 43, 39)
        P([(9, 33), (9, 25), (20, 22), (20, 28)])
        P([(44, 28), (44, 22), (55, 25), (55, 33)])
        B(28, 33, 8, 4, True)
        L(30, 38, 29, 39)
        L(33, 38, 34, 39)
    elif g == "brick-pulse":
        for y in (1, 6):
            for x in range(1, 63, 10):
                B(x, y, 8, 3, True)
        T("BRICK", 2, 13, "speed")
        T("PULSE", 26, 25, "speed")
        L(2, 26, 10, 20)
        L(5, 30, 16, 21)
        C(47, 16, 3, True)
        for x, y in [(40, 21), (36, 24), (32, 27)]:
            c.dot(x, y)
        B(2, 36, 25, 3, True)
        L(7, 37, 22, 37, 0)
    elif g == "star-lance":
        T("STAR", 2, 2, "speed", tall=2)
        T("LANCE", 33, 31, "speed")
        P([(46, 10), (40, 26), (45, 23), (46, 29), (48, 23), (55, 26)], True)
        L(46, 0, 46, 7)
        for x, y in [(4, 25), (13, 29), (24, 24)]:
            P(
                [(x, y), (x + 3, y - 3), (x + 6, y), (x + 4, y + 2), (x + 2, y + 2)],
                True,
            )
        c.stars([(33, 3), (60, 8), (30, 34), (4, 37)])
    elif g == "ribbon-snake":
        T("RIBBON", 2, 2)
        T("SNAKE", 32, 30)
        P([(4, 13), (58, 13), (58, 25), (17, 25), (17, 36), (3, 36), (3, 21), (40, 21)])
        P([(4, 15), (56, 15), (56, 23), (15, 23), (15, 34), (5, 34), (5, 19), (40, 19)])
        B(39, 18, 7, 5, True)
        c.dot(43, 19, 0)
        c.dot(43, 21, 0)
        D(51, 20, 2, True)
    elif g == "lunar-touchdown":
        T("LUNAR", 2, 1, wide=2)
        T("TOUCHDOWN", 5, 10)
        P([(0, 39), (7, 35), (17, 37), (29, 34), (38, 35), (49, 31), (62, 35)], True)
        B(17, 24, 11, 6, True)
        B(19, 20, 7, 4, True)
        B(21, 22, 3, 3, True, 0)
        L(18, 30, 13, 35)
        L(27, 30, 32, 35)
        L(11, 35, 17, 35)
        L(29, 35, 34, 35)
        P([(21, 31), (22, 35), (24, 31)], True)
        C(55, 24, 4)
        C(57, 23, 3, True, 0)
    elif g == "echo-parry":
        T("ECHO", 2, 1, wide=2)
        T("PARRY", 28, 31)
        P([(5, 16), (15, 12), (25, 16), (23, 29), (15, 36), (7, 29)], True)
        P([(9, 19), (15, 16), (21, 19), (19, 27), (15, 30), (11, 27)], False, 0)
        P([(29, 25), (55, 9), (61, 8), (58, 14), (34, 29)], True)
        L(30, 21, 36, 32)
        c.stars([(28, 17), (38, 18), (31, 35)])
    elif g == "pendulum-port":
        T("PENDULUM", 2, 2)
        T("PORT", 1, 29)
        L(39, 12, 39, 16)
        L(39, 15, 56, 29)
        C(56, 29, 4, True)
        for x, y in [(19, 21), (23, 28), (31, 32), (40, 34)]:
            c.dot(x, y)
        for x, y in [(0, 22), (25, 37), (49, 37)]:
            B(x, y, 13, 3, True)
        D(39, 12, 2, True)
    elif g == "ruin-lexicon":
        T("RUIN", 1, 1, "slab", wide=2)
        T("LEXICON", 20, 31, "slab")
        P([(5, 13), (27, 13), (31, 17), (30, 35), (4, 35), (3, 18)], True)
        for x, y in [(8, 18), (19, 18), (8, 28), (21, 27)]:
            D(x, y, 2, False, 0)
        L(7, 24, 24, 24, 0)
        P([(27, 13), (25, 19), (29, 22), (25, 27)], False, 0)
        for x, y in [(40, 16), (53, 22)]:
            D(x, y, 4)
            L(x - 2, y, x + 2, y)
    elif g == "shadow-archive":
        B(0, 0, 64, 10, True)
        T("SHADOW", 2, 1, ink=0)
        T("ARCHIVE", 20, 31)
        B(3, 17, 28, 19)
        B(3, 13, 13, 4)
        for y in (21, 26, 31):
            B(7, y, 18 if y != 26 else 12, 2, True)
        C(47, 20, 8)
        L(52, 26, 60, 33)
        B(44, 16, 6, 3, True)
        P([(40, 24), (43, 20), (51, 20), (54, 24)], True)
    elif g == "compass-rose":
        T("COMPASS", 2, 2)
        T("ROSE", 39, 29, "slab")
        C(19, 26, 11)
        C(19, 26, 8)
        P([(19, 11), (23, 26), (19, 39), (15, 26)], True)
        P([(4, 26), (19, 22), (34, 26), (19, 30)], False)
        D(49, 17, 3, True)
        for x, y in [(36, 24), (40, 20), (43, 19)]:
            c.dot(x, y)
    elif g == "mirror-relic":
        T("MIRROR", 1, 1, "slab")
        T("RELIC", 33, 32, "slab")
        B(23, 12, 18, 23, True)
        B(26, 15, 12, 17, True, 0)
        L(27, 29, 37, 18)
        L(27, 24, 33, 18)
        for x, y in [(11, 23), (52, 23)]:
            D(x, y, 6)
            D(x, y, 3, True)
        L(3, 37, 24, 37)
    elif g == "orchard-days":
        T("ORCHARD", 1, 1)
        T("DAYS", 39, 31)
        for x, y, r in [(8, 23, 7), (27, 20, 9), (51, 21, 8)]:
            B(x - 1, y, 3, 36 - y, True)
            C(x, y, r, True)
            for dx, dy in [(-3, -2), (3, -1), (0, 3)]:
                C(x + dx, y + dy, 1, True, 0)
        L(0, 37, 30, 37)
        L(0, 39, 22, 39)
        C(57, 5, 3)
        L(43, 8, 49, 8)
    elif g == "tidal-nets":
        T("TIDAL", 1, 2, wide=2)
        T("NETS", 37, 13)
        P([(1, 18), (9, 25), (35, 25), (43, 18)], True)
        L(22, 13, 22, 24)
        L(16, 13, 29, 13)
        for x in (6, 12, 18, 24, 30, 36):
            L(x, 27, x + 6, 39)
        for y in (28, 33, 38):
            L(6, y, 42, y)
        P([(48, 28), (55, 25), (60, 28), (55, 31)], True)
        P([(60, 28), (63, 25), (63, 31)], True)
        for x in (1, 13, 46, 58):
            L(x, 36, x + 4, 36)
    elif g == "potion-path":
        T("POTION", 1, 1)
        T("PATH", 40, 29, "slab")
        B(9, 13, 10, 2, True)
        B(11, 15, 6, 8)
        P([(11, 22), (2, 34), (4, 39), (28, 39), (30, 34), (17, 22)], True)
        B(11, 28, 12, 2, True, 0)
        C(9, 34, 2, True, 0)
        C(23, 35, 1, True, 0)
        P([(34, 25), (39, 25), (39, 19), (47, 19), (47, 12), (59, 12)])
        D(59, 12, 3)
        C(23, 17, 2)
        C(27, 10, 1)
    elif g == "auction-house":
        T("AUCTION", 1, 1)
        T("HOUSE", 31, 31, "slab")
        P([(10, 12), (17, 8), (31, 21), (25, 27)], True)
        P([(25, 22), (28, 25), (14, 36), (11, 33)], True)
        B(1, 37, 31, 3, True)
        for y in (15, 20, 25):
            B(42, y, 17, 3, True)
            L(45, y + 1, 55, y + 1, 0)
        c.stars([(35, 10), (58, 5)])
    elif g == "metro-weave":
        T("METRO", 2, 3)
        T("WEAVE", 32, 30)
        P([(1, 17), (18, 17), (28, 27), (44, 27), (59, 12)])
        P([(1, 30), (12, 30), (33, 9), (61, 9)])
        for x, y in [(5, 17), (18, 17), (35, 27), (55, 16), (9, 30), (31, 11), (49, 9)]:
            C(x, y, 2, True)
        B(43, 3, 12, 4, True)
        B(45, 4, 3, 2, True, 0)
        B(50, 4, 3, 2, True, 0)
        L(1, 37, 25, 37)
    elif g == "cargo-balance":
        T("CARGO", 2, 1, wide=2)
        T("BALANCE", 2, 11)
        P([(3, 29), (59, 29), (52, 37), (12, 37)], True)
        for x, y in [(13, 23), (24, 23), (35, 23), (24, 17), (46, 22)]:
            B(x, y, 9, 6)
            L(x + 2, y + 1, x + 6, y + 4)
        B(51, 15, 6, 7, True)
        for x in (0, 15, 31, 47):
            L(x, 39, x + 8, 39)
    elif g == "peg-garden":
        T("PEG", 2, 1, wide=2)
        T("GARDEN", 27, 31)
        for x, y in [(8, 20), (22, 20), (36, 20), (15, 30), (29, 30)]:
            C(x, y, 4, True)
            L(x - 2, y - 1, x + 1, y - 2, 0)
        P([(9, 13), (17, 8), (25, 10), (35, 13)])
        P([(33, 9), (35, 13), (31, 14)])
        L(52, 25, 52, 6)
        P([(52, 14), (46, 9), (45, 4), (51, 8)], True)
        P([(52, 19), (59, 13), (62, 12), (58, 19)], True)
    elif g == "number-vault":
        T("NUMBER", 2, 1)
        T("VAULT", 31, 31)
        B(2, 12, 26, 26, True)
        B(5, 15, 20, 20, False, 0)
        C(15, 25, 6, False, 0)
        L(15, 19, 15, 31, 0)
        L(9, 25, 21, 25, 0)
        for x, value in [(34, "3"), (44, "1"), (54, "4")]:
            B(x, 15, 8, 12)
            T(value, x + 1, 18)
        L(33, 28, 62, 28)
    elif g == "phase-pairs":
        T("PHASE", 1, 2, wide=2)
        T("PAIRS", 34, 31)
        for x, y, v in [(2, 15, "4"), (17, 15, "6"), (39, 13, "3"), (51, 20, "7")]:
            B(x, y, 11, 13)
            T(v, x + 3, y + 3)
        P([(13, 20), (16, 20)])
        L(37, 28, 49, 28)
        B(1, 34, 23, 4, True)
        T("10", 29, 20)
    elif g == "fuse-box":
        T("FUSE", 1, 1, wide=2)
        T("BOX", 45, 30)
        B(2, 12, 31, 26, True)
        for x in (7, 16, 25):
            for y in (17, 27):
                B(x, y, 4, 6, True, 0)
                L(x, y, x + 3, y + 4)
        for y in (15, 23):
            L(34, y, 43, y)
            L(43, y, 43, y + 4)
            L(43, y + 4, 61, y + 4)
        D(57, 4, 4, True)
        P([(58, 0), (54, 5), (58, 5), (55, 9)], False, 0)
    elif g == "sand-rescue":
        T("SAND", 1, 1, wide=2)
        T("RESCUE", 27, 11)
        P([(0, 34), (12, 27), (23, 35), (33, 30), (46, 37), (63, 31)])
        B(1, 15, 14, 4, True)
        L(11, 19, 11, 24)
        L(11, 24, 36, 24)
        L(36, 24, 36, 30)
        for x in (20, 31):
            B(x, 20, 2, 8, True)
        for x, y in [(41, 33), (51, 29), (59, 35)]:
            L(x, y, x, y + 4)
            L(x, y + 2, x - 3, y)
            L(x, y + 1, x + 2, y - 1)
        for x, y in [(7, 27), (3, 30), (17, 38), (29, 37)]:
            c.dot(x, y)
    elif g == "word-foundry":
        T("WORD", 1, 1, wide=2)
        T("FOUNDRY", 20, 31, "slab")
        B(2, 14, 18, 14, True)
        T("A", 8, 18, ink=0)
        B(24, 14, 18, 14)
        T("B", 30, 18)
        B(46, 14, 16, 14)
        T("C", 51, 18)
        L(0, 29, 63, 29)
        for x in range(3, 60, 6):
            c.dot(x, 30)
    elif g == "relic-dive":
        # An asymmetric dungeon entrance; game-specific title packing follows.
        T("RELIC", 1, 1, "slab")
        T("DIVE", 1, 11, "slab", tall=2)
        B(38, 1, 24, 28, True)
        B(43, 7, 14, 22, True, 0)
        for y in (5, 12, 19, 26):
            L(38, y, 41, y, 0)
            L(58, y + 2, 61, y + 2, 0)
        D(50, 17, 5)
        D(50, 17, 2, True)
        for x, y, w in [(32, 27, 28), (28, 29, 32), (24, 31, 37)]:
            L(x, y, x + w, y)
        c.stars([(32, 5), (33, 20)])
    else:
        raise ValueError(f"Missing authored title: {g}")
    for value, x, y, style, wide, tall in c.titles:
        width = (len(value) * 6 - 1) * wide + (2 if style == "speed" else 0)
        c.box(x - 1, y - 1, width + 2, 7 * tall + 2, True, 0)
        c.paint_label(value, x, y, style, wide, tall)
    return c


def put(screen, x, y, value):
    assert x >= 0 and x + len(value) <= 32 and 0 <= y < 24, (x, y, value)
    screen[y * 32 + x : y * 32 + x + len(value)] = [
        64 if ch == " " else ord(ch) - 32 for ch in value
    ]


def title(info):
    canvas = poster(info)
    screen = quads(canvas.p) + [64] * 128
    bank = quad_bank()
    if finish := FINISH_FOR.get(info["id"]):
        bank = finish_bank(bank, finish)
        for value, x, y, style, wide, tall in canvas.titles:
            width = (len(value) * 6 - 1) * wide + (2 if style == "speed" else 0)
            for row in range(y // 2, (y + 7 * tall + 1) // 2):
                for col in range(x // 2, (x + width + 1) // 2):
                    offset = row * 32 + col
                    if 128 < screen[offset] < 144:
                        screen[offset] += 16
    if info["id"] == "chrono-breach":
        put(screen, 10, 22, "SECTOR")
    put(screen, 3, 21, "RETURN / BUTTON : START")
    put(screen, 3, 23, "SPACE : GUIDE   CTRL+C EXIT")
    return bank, screen
