"""Compact, authored PCG art and surrounds for the remaining sample games."""

from artwork import put
from relief import Pixels, sprite


def prepare(bank, hud, game):
    if game == "memory-mosaic":
        # Eight one-character emblems sit inside the common card face.
        icons = [
            [24, 60, 126, 255, 126, 60, 24, 0],
            [102, 255, 255, 126, 60, 24, 0, 0],
            [24, 60, 90, 24, 60, 126, 24, 0],
            [24, 24, 126, 24, 24, 24, 24, 0],
            [24, 24, 60, 60, 126, 126, 24, 0],
            [126, 66, 90, 90, 66, 126, 0, 0],
            [0, 66, 231, 126, 60, 24, 126, 0],
            [60, 102, 195, 129, 195, 102, 60, 0],
        ]
        bank[:64] = [byte for icon in icons for byte in icon]
    elif game == "shadow-archive":
        # Six distinct 8x16 portraits: the hat, glasses and tie are literal clues.
        for face in range(1, 7):
            rows = [0, 24, 60, 126, 66, 90, 66, 60, 24, 126, 219, 153, 153, 126, 66, 0]
            if face & 1:
                rows[0:4] = [60, 60, 60, 126]
            if face & 2:
                rows[4:6] = [126, 90]
            if face & 4:
                rows[9:13] = [102, 90, 90, 153]
            bank[(face - 1) * 16 : face * 16] = rows
    elif game == "orchard-days":
        for slot in (1, 2, 5):
            p = Pixels(contact_shadow=False)
            if slot == 1:
                p.line(1, 13, 14, 13)
                p.ellipse(7, 11, 2, 1, True)
            elif slot == 2:
                p.line(7, 6, 7, 14)
                p.ellipse(4, 6, 3, 2, True)
                p.ellipse(10, 3, 3, 2, True)
                p.line(3, 14, 12, 14)
            else:
                p.poly([(7, 1), (2, 9), (3, 13), (7, 15), (12, 12), (12, 9)], True)
                p.line(5, 8, 4, 11, 0)
            bank[slot * 32 : slot * 32 + 32] = p.pack()
    elif game in ("night-swarm", "star-lance"):
        p = Pixels()
        p.poly([(3, 2), (12, 2), (15, 8), (12, 13), (3, 13), (0, 8)], True)
        p.rect(4, 4, 8, 7, value=0)
        p.line(5, 7, 10, 7)
        p.line(7, 4, 7, 10)
        p.shadow()
        bank[32:64] = p.pack()
    elif game == "compass-rose":
        bank[32:64] = sprite("stone")
    if game == "cargo-balance":
        hud[16 * 32 : 19 * 32] = [64] * (3 * 32)
        for x in (1, 7, 13, 19, 25):
            for y in range(8, 17):
                hud[y * 32 + x] = 26
    # Rebuilt panels leave room for the new histories and card hands.
    if game in ("number-vault", "twenty-one", "shadow-archive", "circuit-works"):
        hud[32 : 23 * 32] = [64] * (22 * 32)

        def line(x, y, n):
            hud[y * 32 + x : y * 32 + x + n] = [13] * n

        if game == "number-vault":
            for y in (7, 9, 21):
                line(1, y, 30)
            for y in range(10, 21):
                hud[y * 32 + 18] = 113
        elif game == "twenty-one":
            put(hud, 2, 2, "PLAYER")
            put(hud, 21, 2, "DEALER")
            for y in range(3, 15):
                hud[y * 32 + 15] = 113
            line(0, 15, 32)
            for y, x, value in [
                (16, 0, "TOTAL"),
                (16, 19, "TOTAL"),
                (18, 0, "COINS"),
                (18, 22, "HAND  /5"),
            ]:
                put(hud, x, y, value)
        elif game == "shadow-archive":
            put(hud, 1, 2, "SIX SUSPECTS")
            line(1, 3, 15)
            for y in range(3, 18):
                hud[y * 32 + 16] = 113
            for y in (9, 15):
                line(1, y, 15)
        else:
            put(hud, 1, 2, "3-INPUT LOGIC")
            put(hud, 17, 2, "A B C W NOW")
            put(hud, 1, 18, "G1>G2>G3")
            put(hud, 1, 20, "TESTS")
            put(hud, 16, 20, "MATCHED    /8")
            for y in range(3, 18):
                hud[y * 32 + 15] = 113
            line(0, 19, 32)
