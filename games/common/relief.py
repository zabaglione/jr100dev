"""Build-time relief art. Every sprite stays inside its existing 16x16 cell.

Upper-left highlights, a dark right face and a broken contact shadow suggest
height without moving collision cells or spending any extra JR-100 RAM/PCG.
"""

import math


class Pixels:
    def __init__(self, width=16, height=16, *, contact_shadow=True):
        self.p = [[0] * width for _ in range(height)]
        self.contact_shadow = contact_shadow

    def dot(self, x, y, value=1):
        x, y = round(x), round(y)
        if 0 <= y < len(self.p) and 0 <= x < len(self.p[0]):
            self.p[y][x] = int(value)

    def line(self, x, y, u, v, value=1):
        steps = max(abs(u - x), abs(v - y), 1)
        for n in range(steps + 1):
            self.dot(x + (u - x) * n / steps, y + (v - y) * n / steps, value)

    def poly(self, points, fill=False, value=1):
        if fill:
            for y in range(min(p[1] for p in points), max(p[1] for p in points) + 1):
                crossings = []
                for (x1, y1), (x2, y2) in zip(points, points[1:] + points[:1]):
                    if min(y1, y2) <= y < max(y1, y2):
                        crossings.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
                crossings.sort()
                for left, right in zip(crossings[::2], crossings[1::2]):
                    for x in range(math.ceil(left), math.floor(right) + 1):
                        self.dot(x, y, value)
        for a, b in zip(points, points[1:] + points[:1]):
            self.line(*a, *b, value)

    def rect(self, x, y, w, h, fill=False, value=1):
        self.poly(
            [(x, y), (x + w - 1, y), (x + w - 1, y + h - 1), (x, y + h - 1)],
            fill,
            value,
        )

    def ellipse(self, x, y, rx, ry, fill=False, value=1):
        if fill:
            for yy in range(y - ry, y + ry + 1):
                for xx in range(x - rx, x + rx + 1):
                    if (xx - x) ** 2 * ry**2 + (yy - y) ** 2 * rx**2 <= rx**2 * ry**2:
                        self.dot(xx, yy, value)
        for a in range(120):
            self.dot(
                x + rx * math.cos(a * math.pi / 60),
                y + ry * math.sin(a * math.pi / 60),
                value,
            )

    def shadow(self, left=3, right=13, y=15):
        if not self.contact_shadow:
            return
        for x in range(left, right + 1):
            if x % 2:
                self.dot(x, y)

    def pack(self):
        assert len(self.p) == len(self.p[0]) == 16
        return [
            sum(self.p[y + dy][x + dx] << (7 - dx) for dx in range(8))
            for y in (0, 8)
            for x in (0, 8)
            for dy in range(8)
        ]


def shade_figure(pixels):
    """Shade a large solid silhouette without cutting its outline or features."""
    result = [list(map(int, row)) for row in pixels]
    height, width = len(result), len(result[0])
    for y in range(1, height - 1):
        for x in range(width // 2, width - 1):
            if (x + y) % 2 == 0 and all(
                pixels[y + dy][x + dx]
                for dx, dy in ((0, 0), (0, -1), (0, 1), (-1, 0), (1, 0))
            ):
                result[y][x] = 0
    for x in range(3, width - 2, 2):
        if not pixels[height - 2][x]:
            result[height - 1][x] = 1
    return result


def sprite(kind, *, contact_shadow=True):
    c = Pixels(contact_shadow=contact_shadow)
    if kind.startswith("wall-") or kind in ("crate", "cargo", "stone"):
        # The top is a parallelogram; the front and side remain inside the cell.
        c.poly([(0, 3), (3, 0), (15, 0), (12, 3)])
        c.rect(0, 3, 13, 13)
        c.poly([(12, 3), (15, 0), (15, 12), (12, 15)])
        for y in range(4, 13, 3):
            c.line(13, y, 14, y - 1)
        if kind in ("wall-stone", "stone"):
            c.line(1, 9, 11, 9)
            c.line(5, 4, 5, 8)
            c.line(8, 10, 8, 14)
        elif kind == "wall-ice":
            c.line(2, 6, 7, 4)
            c.line(2, 12, 9, 5)
            c.line(5, 13, 10, 8)
        elif kind == "wall-metal":
            c.rect(2, 5, 9, 9)
            c.dot(3, 6)
            c.dot(9, 12)
        elif kind == "wall-sand":
            c.line(2, 7, 10, 7)
            c.line(1, 12, 11, 12)
            c.dot(5, 5)
        elif kind == "wall-glass":
            c.line(2, 12, 9, 5)
            c.line(4, 13, 10, 7)
        elif kind in ("crate", "cargo"):
            c.rect(2, 5, 9, 9)
            c.line(3, 6, 9, 12)
            c.line(9, 6, 3, 12)
        else:
            c.line(2, 5, 10, 5)
    elif kind.startswith("floor"):
        c.dot(7, 8)
        if kind == "floor-ice":
            c.line(10, 4, 12, 2)
        elif kind == "floor-grid":
            c.line(6, 8, 9, 8)
            c.line(8, 6, 8, 9)
        elif kind == "floor-soil":
            c.line(3, 12, 8, 12)
            c.line(6, 4, 10, 4)
        elif kind == "floor-water":
            c.line(1, 9, 5, 9)
            c.line(9, 6, 13, 6)
        elif kind == "floor-metal":
            c.dot(1, 1)
            c.dot(14, 14)
    elif kind == "lamp-off":
        c.poly([(1, 8), (7, 5), (13, 8), (7, 11)])
        c.line(3, 10, 7, 13)
        c.line(7, 13, 11, 10)
    elif kind == "net":
        c.ellipse(7, 4, 6, 2)
        c.poly([(1, 4), (4, 12), (10, 12), (13, 4)])
        for y in (7, 10):
            c.line(4, y, 10, y)
        c.line(5, 6, 6, 12)
        c.line(9, 6, 8, 12)
        c.shadow()
    elif kind in ("gem", "socket", "seal"):
        c.poly([(7, 1), (13, 6), (7, 12), (1, 6)])
        if kind == "gem":
            c.poly([(7, 1), (5, 6), (7, 12), (9, 6)])
            c.line(2, 6, 12, 6)
            c.shadow(4, 13)
        else:
            c.poly([(7, 4), (10, 6), (7, 9), (4, 6)])
            c.poly([(1, 8), (7, 14), (13, 8)])
            if kind == "seal":
                c.line(7, 3, 7, 9)
    elif kind in ("orb", "token-white", "token-black", "token-cross", "peg"):
        if kind == "peg":
            c.ellipse(7, 5, 4, 3, True)
            c.rect(5, 6, 5, 6, True)
            c.line(9, 7, 9, 11, 0)
            c.ellipse(7, 12, 5, 2)
        else:
            c.ellipse(7, 7, 6, 5, kind != "token-black")
            c.ellipse(7, 9, 6, 5)
            if kind in ("orb", "token-white"):
                c.line(10, 5, 11, 8, 0)
                c.line(9, 10, 11, 8, 0)
                c.line(3, 4, 5, 3, 0)
            if kind == "token-cross":
                c.line(4, 4, 10, 10, 0)
                c.line(10, 4, 4, 10, 0)
        c.shadow()
    elif kind in (
        "person",
        "robot",
        "guard",
        "knight",
        "snake",
        "ship",
        "lander",
        "train",
    ):
        c.shadow()
        if kind in ("person", "robot", "guard", "knight"):
            c.rect(5, 1, 6, 4, True)
            c.rect(4, 6, 8, 5, True)
            c.line(3, 7, 3, 10)
            c.line(12, 7, 12, 10)
            c.line(5, 11, 4, 13)
            c.line(10, 11, 11, 13)
            c.line(10, 7, 10, 10, 0)
            if kind == "robot":
                c.rect(3, 1, 10, 4, True)
                c.line(5, 3, 10, 3, 0)
                c.rect(6, 7, 3, 2, False, 0)
            elif kind == "guard":
                c.line(4, 0, 11, 0)
                c.line(5, 3, 10, 3, 0)
            elif kind == "knight":
                c.line(13, 2, 13, 11)
                c.line(11, 8, 15, 8)
        elif kind == "snake":
            c.ellipse(7, 7, 6, 5, True)
            c.rect(4, 4, 2, 2, True, 0)
            c.rect(9, 4, 2, 2, True, 0)
            c.line(5, 9, 9, 9, 0)
        elif kind in ("ship", "lander"):
            if kind == "ship":
                c.poly(
                    [
                        (7, 0),
                        (10, 7),
                        (14, 12),
                        (9, 11),
                        (7, 8),
                        (5, 11),
                        (0, 12),
                        (4, 7),
                    ],
                    True,
                )
                c.line(7, 3, 7, 7, 0)
                c.line(3, 10, 5, 8, 0)
            else:
                c.poly([(5, 1), (10, 1), (12, 5), (10, 9), (4, 9), (2, 5)])
                c.rect(5, 3, 5, 3, True)
                c.line(4, 9, 1, 13)
                c.line(10, 9, 14, 13)
                c.line(0, 13, 3, 13)
                c.line(12, 13, 15, 13)
        else:
            c.poly([(1, 4), (4, 1), (14, 1), (14, 10), (11, 13), (1, 13)])
            c.line(1, 4, 11, 4)
            c.line(11, 4, 14, 1)
            c.line(11, 4, 11, 13)
            c.rect(3, 6, 6, 4)
            c.dot(3, 12)
            c.dot(9, 12)
    elif kind in ("foe", "shield", "swarm"):
        if kind == "swarm":
            c.ellipse(7, 6, 4, 4, True)
            for y in (3, 7, 10):
                c.line(3, 6, 0, y)
                c.line(11, 6, 15, y)
        elif kind == "shield":
            c.poly([(2, 1), (12, 1), (12, 8), (7, 13), (2, 8)])
            c.line(7, 2, 7, 11)
            c.line(9, 3, 11, 3)
            c.line(10, 4, 10, 8)
        else:
            c.poly([(3, 2), (11, 2), (13, 6), (11, 11), (3, 11), (1, 6)], True)
            c.rect(4, 5, 2, 2, True, 0)
            c.rect(9, 5, 2, 2, True, 0)
            c.line(5, 9, 9, 9, 0)
            for x in (3, 6, 10, 12):
                c.line(x, 10, x, 13)
        c.shadow()
    elif kind in ("door", "bridge", "switch", "pit"):
        if kind == "pit":
            c.poly([(3, 4), (15, 4), (11, 12), (0, 12)])
            c.line(4, 6, 11, 6)
            c.line(11, 6, 10, 9)
        elif kind == "bridge":
            c.poly([(3, 1), (13, 1), (11, 12), (1, 12)])
            for y in (4, 7, 10):
                c.line(3, y, 11, y)
            c.line(1, 14, 11, 14)
        else:
            c.poly([(1, 4), (4, 1), (14, 1), (14, 12), (11, 15), (1, 15)])
            c.rect(1, 4, 11, 12)
            c.line(11, 4, 14, 1)
            if kind == "switch":
                c.rect(4, 7, 5, 6)
                c.line(5, 9, 8, 6)
            else:
                c.line(5, 5, 5, 14)
                c.line(8, 5, 8, 14)
    elif kind in ("frame", "card", "keycap", "card-back"):
        # The top row may be overwritten by a ROM number: the lower/right
        # bevel is sufficient to keep the tile legible in all occupied states.
        c.rect(0, 0, 14, 13)
        c.line(2, 14, 15, 14)
        c.line(15, 2, 15, 14)
        c.dot(14, 13)
        if kind == "card-back":
            c.poly([(6, 3), (10, 6), (6, 10), (2, 6)])
            c.line(6, 3, 6, 10)
        elif kind == "card":
            c.line(2, 3, 4, 3)
            c.line(9, 10, 11, 10)
    elif kind in ("mirror-up", "mirror-down"):
        # The actual reflective diagonal stays unmistakable; only its stand
        # and a parallel dark-side rim add depth.
        if kind == "mirror-up":
            c.line(1, 13, 13, 1)
            c.line(3, 13, 14, 2)
        else:
            c.line(1, 1, 13, 13)
            c.line(1, 3, 12, 14)
        c.shadow(5, 11)
    elif kind in ("tree", "fruit", "flask", "fish", "flame", "ribbon"):
        c.shadow()
        if kind in ("tree", "fruit"):
            c.ellipse(7, 5, 5, 4, True)
            c.rect(6, 7, 3, 6, True)
            c.line(8, 8, 8, 12, 0)
            c.line(4, 3, 6, 2, 0)
            if kind == "fruit":
                for x, y in ((5, 5), (9, 4), (8, 7)):
                    c.dot(x, y, 0)
        elif kind == "flask":
            c.rect(5, 1, 5, 3)
            c.poly([(5, 4), (2, 10), (3, 13), (11, 13), (13, 10), (9, 4)])
            c.line(3, 9, 11, 9)
            c.line(4, 11, 10, 11)
            c.dot(4, 8)
        elif kind == "fish":
            c.ellipse(9, 7, 5, 3, True)
            c.poly([(4, 7), (0, 3), (0, 11)], True)
            c.dot(11, 6, 0)
            c.line(6, 8, 9, 8, 0)
        elif kind == "flame":
            c.poly(
                [(6, 1), (10, 6), (11, 3), (13, 9), (10, 13), (4, 13), (1, 9), (4, 5)],
                True,
            )
            c.poly([(7, 7), (9, 11), (6, 12), (5, 10)], True, 0)
        else:
            c.ellipse(7, 7, 6, 5, True)
            c.line(3, 4, 8, 3, 0)
            c.line(10, 6, 11, 9, 0)
    else:
        raise ValueError(kind)
    return c.pack()


# Explicit art direction per title, rather than choosing sprites by genre.
NATIVE = {
    "iron-script": {0: "floor-metal", 1: "wall-metal", 2: "robot", 3: "socket"},
    "chain-suit": {},  # Authored suit symbols and reusable full-card borders.
    "quiet-route": {
        0: "floor",
        1: "wall-stone",
        2: "person",
        3: "gem",
        5: "guard",
        6: "door",
    },
    "circuit-works": {6: "switch"},
    "hearth-zero": {3: "flame"},
    "night-swarm": {0: "floor", 2: "ship", 5: "swarm"},
    "lumen-cross": {0: "lamp-off", 3: "gem"},
    "magnet-vault": {
        0: "floor-metal",
        1: "wall-metal",
        2: "robot",
        3: "socket",
        4: "crate",
    },
    "frost-steps": {0: "floor-ice", 1: "wall-ice", 2: "person", 3: "gem"},
    "prism-trace": {},  # A deduplicated atlas combines mirrors and light paths.
    "tide-bridge": {
        0: "floor-water",
        1: "floor-water",
        2: "person",
        3: "bridge",
        4: "bridge",
        6: "door",
    },
    "glyph-shift": {
        0: "floor",
        1: "wall-stone",
        2: "person",
        3: "socket",
        4: "crate",
        5: "foe",
    },
    "gravity-well": {0: "floor-metal", 1: "wall-metal", 3: "socket", 4: "orb"},
    "seed-merge": {7: "frame"},
    "orbit-draft": {7: "frame"},
    "five-forge": {0: "floor-grid", 2: "token-black", 5: "token-cross"},
    "corner-crown": {
        0: "floor-grid",
        2: "token-white",
        5: "token-black",
        6: "token-white",
    },
    "stone-balance": {4: "stone"},
    "memory-mosaic": {4: "card-back", 7: "card"},
    "twenty-one": {7: "card"},
    "orbit-dodge": {2: "ship", 3: "gem", 5: "orb", 7: "socket"},
    "gate-runner": {1: "wall-metal", 2: "ship", 6: "pit"},
    "brick-pulse": {},
    "star-lance": {2: "ship", 5: "foe"},
    "ribbon-snake": {0: "floor", 2: "snake", 3: "gem", 4: "ribbon"},
    "lunar-touchdown": {2: "lander"},
    "echo-parry": {2: "knight", 5: "shield", 6: "shield"},
    "pendulum-port": {2: "person", 3: "socket", 6: "switch"},
    "ruin-lexicon": {},
    "shadow-archive": {2: "person"},
    "compass-rose": {0: "floor-soil", 2: "person", 4: "wall-sand"},
    "mirror-relic": {0: "floor", 1: "wall-glass", 2: "person", 3: "gem", 6: "door"},
    "orchard-days": {0: "floor-soil", 3: "fruit", 4: "tree"},
    "tidal-nets": {0: "floor-water", 3: "fish", 4: "net"},
    "potion-path": {0: "floor-grid", 3: "socket", 4: "flask"},
    "auction-house": {3: "gem", 4: "crate"},
    "metro-weave": {2: "train", 6: "switch"},
    "cargo-balance": {4: "cargo"},
    "peg-garden": {0: "socket", 1: "stone", 4: "peg"},
    "number-vault": {7: "keycap"},
    "phase-pairs": {},  # Authored numeral cards use the complete bank.
    "fuse-box": {4: "switch", 6: "frame", 7: "frame"},
    "sand-rescue": {
        0: "floor-soil",
        1: "wall-sand",
        3: "tree",
        4: "floor-water",
        6: "door",
    },
    "word-foundry": {},
}


def replace_sprites(bank, replacements):
    bank = list(bank)
    assert len(bank) == 256
    for slot, kind in replacements.items():
        assert 0 <= slot < 8
        bank[slot * 32 : (slot + 1) * 32] = sprite(kind)
    return bank


def native_bank(info):
    defaults = ("floor", "wall-stone", "person", "gem", "crate", "foe", "door", "frame")
    bank = [byte for kind in defaults for byte in sprite(kind)]
    bank = replace_sprites(bank, NATIVE[info["id"]])
    if info["id"] == "frost-steps":
        for slot, kind in ((2, "person"), (3, "gem")):
            bank[slot * 32 : (slot + 1) * 32] = sprite(kind, contact_shadow=False)
    return bank
