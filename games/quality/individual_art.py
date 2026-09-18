"""Authored scenery and intermediate poses for the second individual review."""

from art import emit
from artwork import put
from relief import Pixels, sprite
from title_styles import ROM_QUADS


def prepare(bank, hud, metadata):
    if not metadata.get("secondReview"):
        return ""
    game = metadata["id"]
    extra = ""

    def line(x, y, length, code=0x0D):
        for i in range(length):
            hud[y * 32 + x + i] = code

    def upright(x, y, length, code=0x71):
        for i in range(length):
            hud[(y + i) * 32 + x] = code

    def clear_scene():
        hud[32 : 23 * 32] = [64] * (22 * 32)

    def bake(canvas, top, bottom):
        for y in range(top, bottom):
            for x in range(32):
                quad = sum(
                    canvas.p[y * 2 + dy][x * 2 + dx] << (dy * 2 + dx)
                    for dy in range(2)
                    for dx in range(2)
                )
                if quad:
                    hud[y * 32 + x] = ROM_QUADS[quad]

    if game in ("orbit-dodge", "lunar-touchdown", "pendulum-port", "orchard-days"):
        clear_scene()
        p = Pixels(64, 48, contact_shadow=False)
        if game == "orbit-dodge":
            p.ellipse(31, 21, 27, 15)
            p.ellipse(31, 21, 14, 8)
            p.ellipse(31, 21, 3, 3, True)
            p.line(29, 19, 31, 19, 0)
            bake(p, 3, 20)
            node = Pixels(contact_shadow=False)
            node.ellipse(7, 7, 2, 2)
            bank[224:256] = node.pack()
            target = Pixels(contact_shadow=False)
            target.ellipse(7, 7, 5, 5)
            target.line(7, 0, 7, 4)
            target.line(7, 10, 7, 15)
            target.line(0, 7, 4, 7)
            target.line(10, 7, 15, 7)
            bank[32:64] = target.pack()
        elif game == "lunar-touchdown":
            p.ellipse(51, 12, 9, 7, True)
            p.ellipse(48, 11, 8, 7, True, 0)
            for x, y in ((4, 10), (18, 6), (33, 12), (59, 25), (13, 26)):
                p.dot(x, y)
            p.poly(
                [
                    (0, 47),
                    (0, 45),
                    (6, 44),
                    (13, 47),
                    (20, 45),
                    (28, 46),
                    (35, 44),
                    (44, 47),
                    (55, 44),
                    (63, 46),
                    (63, 47),
                ],
                True,
            )
            bake(p, 3, 24)
        elif game == "pendulum-port":
            p.poly([(0, 26), (5, 27), (5, 39), (2, 43), (0, 42)], True)
            p.poly([(63, 24), (59, 28), (59, 37), (61, 41), (63, 40)], True)
            for x in range(0, 60, 9):
                p.line(x, 45, x + 5, 45)
                p.line(x + 2, 47, x + 6, 47)
            bake(p, 3, 24)
            put(hud, 1, 20, "ROPES")
            put(hud, 17, 20, "PORTS")
        else:
            for y in (6, 32):
                p.line(1, y, 30, y)
            for x in (0, 31, 35):
                p.line(x, 6, x, 32)
            p.line(2, 33, 32, 33)
            bake(p, 3, 17)
            line(18, 15, 13)
    elif game == "echo-parry":
        hud[2 * 32 : 18 * 32] = [64] * (16 * 32)
        p = Pixels(64, 48, contact_shadow=False)
        for x in (0, 58):
            p.poly([(x, 10), (x + 5, 7), (x + 5, 29), (x, 31)], True)
            p.line(x + 2, 11, x + 2, 29, 0)
        p.poly([(4, 33), (10, 30), (53, 30), (59, 33), (58, 35), (5, 35)])
        for x in (13, 25, 38, 50):
            p.line(x, 31, x - 2, 34)
        bake(p, 3, 18)
    elif game == "star-lance":
        # Sparse far-field stars leave missiles and enemy silhouettes readable.
        for x, y in ((1, 2), (12, 2), (25, 2), (5, 12), (18, 11), (28, 13)):
            hud[y * 32 + x] = 0x0E
        line(0, 14, 32)
    elif game == "tidal-nets":
        clear_scene()
        for y in (5, 8, 11, 16):
            for x in range(y % 3, 30, 4):
                line(x, y, 2)
        put(hud, 1, 19, "FISH")
        put(hud, 19, 19, "CASTS")
    elif game == "twenty-one":
        put(hud, 22, 18, "HAND  /7")
        suits = [
            [24, 60, 126, 255, 126, 24, 60, 0],
            [0, 102, 255, 255, 126, 60, 24, 0],
            [24, 60, 126, 255, 126, 60, 24, 0],
            [24, 60, 24, 102, 255, 102, 24, 60],
        ]
        bank[:32] = [b for rows in suits for b in rows]
    elif game == "circuit-works":
        for y in (3, 7, 11, 15):
            line(3, y, 10)
        for y in (4, 8, 12):
            upright(3, y, 3)
            upright(13, y, 3)
    elif game == "ruin-lexicon":
        for y in (3, 7, 11, 15, 19):
            line(1, y, 16)
        upright(0, 3, 17)
        upright(17, 3, 17)
        for y in (3, 7, 11, 15):
            line(23, y, 5)
            line(23, y + 3, 5)
            upright(23, y + 1, 2)
            upright(27, y + 1, 2)
    elif game == "word-foundry":
        for y in (7, 10, 13, 16):
            for x in (1, 9, 17, 25):
                line(x, y, 6)
                line(x + 1, y + 2, 5)
        line(0, 18, 32)
    elif game == "number-vault":
        for x in (0, 31):
            upright(x, 2, 5)
        line(0, 2, 32)
        poses = []
        for width in (14, 8, 2):
            p = Pixels(contact_shadow=False)
            p.rect(1, 0, width, 16, True)
            if width > 2:
                p.rect(2, 1, width - 2, 14, value=0)
                p.ellipse(1 + width // 2, 8, 2, 2)
            poses.extend(p.pack())
        bank[192:224] = poses[:32]
        extra += emit("FACE_6_FRAMES", poses)
    elif game == "lumen-cross":
        poses = []
        for width in (14, 8, 2, 8, 14):
            p = Pixels(contact_shadow=False)
            x = (16 - width) // 2
            p.rect(x, 1, width, 13, len(poses) >= 96)
            p.line(x + 1, 15, x + width - 1, 15)
            poses.extend(p.pack())
        bank[192:224] = poses[:32]
        extra += emit("FLIP_FRAMES", poses)
        bank[96:128] = sprite("lamp-off")
        bank[96:128] = [v ^ 255 for v in bank[96:128]]
    elif game == "hearth-zero":
        poses = [*sprite("flame")]
        p = Pixels()
        p.poly([(2, 12), (5, 4), (7, 8), (10, 0), (14, 10), (12, 14), (4, 14)], True)
        p.poly([(6, 13), (8, 8), (11, 13)], True, 0)
        p.shadow()
        poses += p.pack()
        extra += emit("FACE_3_FRAMES", poses)
    elif game in (
        "quiet-route",
        "night-swarm",
        "ribbon-snake",
        "compass-rose",
        "mirror-relic",
        "potion-path",
    ):
        left = 1 if game == "ribbon-snake" else 0
        line(left, 2, 17, 0x6E)
        line(left, 19, 17, 0x6E)
        for y in range(3, 19):
            hud[y * 32 + 17] = 0x7F if y % 2 else 0x71
        if game == "night-swarm":
            p = Pixels(contact_shadow=False)
            p.ellipse(7, 7, 6, 6)
            p.ellipse(7, 7, 3, 3)
            bank[192:224] = p.pack()
            p = Pixels(contact_shadow=False)
            p.line(6, 2, 6, 12)
            p.line(9, 3, 9, 13)
            bank[224:256] = p.pack()
        if game == "potion-path":
            p = Pixels(contact_shadow=False)
            p.rect(0, 0, 16, 16)
            p.line(3, 3, 12, 12)
            p.line(12, 3, 3, 12)
            bank[32:64] = p.pack()
    elif game == "stone-balance":
        for y in (7, 12, 17):
            line(2, y, 28, 0x6E)
    elif game == "memory-mosaic":
        for y in (3, 7, 11, 15):
            for x in (1, 5, 9, 13):
                line(x, y, 3)
                upright(x + 3, y + 1, 3)
    elif game == "shadow-archive":
        for x in (1, 6, 11):
            for y in (3, 9):
                line(x, y, 4)
        line(18, 4, 13)
    elif game == "auction-house":
        for y in (2, 7, 11, 15):
            line(18, y, 13)
        line(0, 18, 32)
    elif game == "cargo-balance":
        # Crane rail and suspension; cargo and hull lean are drawn by rules.
        line(1, 6, 25, 0x6E)
        upright(0, 6, 11)
        upright(26, 6, 11)
    return extra
