"""Bake perspective scenery and instrument housings into the existing HUD.

Only ROM characters are added, so the 768-byte background and all 32 PCG slots
keep their original size. Coordinates are authored around each game's controls.
"""

from artwork import put


def decorate(screen, game):
    def text(x, y, value):
        put(screen, x, y, value)
        # JR-100's ROM is not ASCII past '_': '\\' would render as yen and
        # '|' as a triangle. Use its actual full-cell line-drawing characters.
        for i, ch in enumerate(value):
            if ch in "/\\|~":
                screen[y * 32 + x + i] = {"/": 0x5F, "\\": 0x7F, "|": 0x71, "~": 0x0D}[
                    ch
                ]

    def hline(x, y, width, char="_"):
        text(x, y, char * width)

    def panel(x, y, w, h):
        text(x, y, "/" + "-" * (w - 2) + "+")
        for yy in range(y + 1, y + h - 1):
            text(x, yy, "|")
            text(x + w - 1, yy, "|")
        text(x, y + h - 1, "+" + "_" * (w - 2) + "/")
        if y + h < 23:
            text(x + 1, y + h, "_" * (w - 1))

    def board(left, top, width, height):
        # A shallow front apron and diagonal right edge sit outside all cells.
        hline(left, top - 1, width)
        for y in range(top, top + height):
            text(left + width, y, "|")
        text(left, top + height, "\\" + "_" * (width - 1) + "/")

    def instruments(x=18):
        # Open left edge leaves room for a game's moving pointer and labels.
        hline(x, 2, 31 - x)
        for y in range(3, 19):
            text(31, y, ":")
        hline(x, 19, 32 - x)

    grid_games = {
        "iron-script",
        "quiet-route",
        "night-swarm",
        "magnet-vault",
        "frost-steps",
        "glyph-shift",
        "gravity-well",
        "five-forge",
        "corner-crown",
        "ribbon-snake",
        "compass-rose",
        "mirror-relic",
        "potion-path",
        "sand-rescue",
    }
    if game in grid_games:
        board(1 if game in ("magnet-vault", "ribbon-snake") else 0, 3, 16, 16)
        instruments()
        # Metal control racks, an ice compass and stone tablets have distinct
        # divider positions, all clear of numbers, runes and rule switches.
        dividers = {
            "iron-script": (8, 12),
            "quiet-route": (8, 13),
            "night-swarm": (9, 14),
            "magnet-vault": (7, 11),
            "frost-steps": (10, 18),
            "glyph-shift": (7, 11),
            "gravity-well": (9, 18),
            "five-forge": (10,),
            "corner-crown": (10,),
            "ribbon-snake": (10,),
            "compass-rose": (10, 15),
            "mirror-relic": (10,),
            "potion-path": (),
            "sand-rescue": (13,),
        }
        for y in dividers[game]:
            hline(19, y, 11, "-")
    elif game in ("lumen-cross", "peg-garden"):
        board(1, 4, 16, 14)
        instruments()
        hline(19, 10, 11, "-")
    elif game == "prism-trace":
        board(2, 4, 14, 14)
        instruments()
    elif game == "tide-bridge":
        board(2, 5, 12, 12)
        for y in (3, 19):
            text(1, y, "~   ~    ~    ~")
        instruments()
    elif game in (
        "seed-merge",
        "memory-mosaic",
        "phase-pairs",
        "orchard-days",
        "orbit-draft",
    ):
        width = 21 if game == "seed-merge" else 16
        board(1, 4, width, 15 if game == "orchard-days" else 14)
        instruments(23 if game == "seed-merge" else 18)
        if game == "seed-merge":
            for row in range(4):
                for column in range(4):
                    panel(column * 5, 4 + row * 4, 5, 3)
        if game == "orchard-days":
            for y in (7, 11, 15):
                hline(2, y, 12, "-")
    elif game == "chain-suit":
        panel(0, 3, 31, 10)
        panel(0, 14, 11, 5)
        panel(12, 14, 10, 5)
        panel(23, 14, 9, 5)
    elif game == "twenty-one":
        panel(2, 4, 11, 7)
        panel(19, 4, 12, 7)
        text(0, 12, "\\_____________  ______________/")
        text(3, 18, "\\________________________/")
    elif game == "stone-balance":
        for y in (3, 8, 13):
            panel(1, y, 30, 4)
    elif game == "circuit-works":
        panel(1, 3, 13, 14)
        panel(17, 4, 15, 14)
        for y in (6, 10, 14):
            text(7, y, "--")
    elif game == "hearth-zero":
        panel(0, 3, 13, 16)
        # Recessed hearth: lintel, angled jambs and a low ash shelf.
        text(2, 5, "\\_______/")
        for y in range(6, 16):
            text(2, y, "|")
            text(10, y, "|")
        panel(12, 3, 20, 14)
    elif game == "orbit-dodge":
        # An elliptical orbital rim: near side doubled, far side sparse.
        text(9, 3, "....       ....")
        text(3, 7, "/")
        text(29, 7, "\\")
        text(2, 13, "\\")
        text(30, 13, "/")
        text(8, 19, "\\______________/")
        text(10, 20, "____________")
    elif game == "gate-runner":
        # Three lanes converge toward the horizon. The player's collision lane
        # remains logical 0..2; only the drawing coordinates are projected.
        text(11, 3, "__________")
        for row in range(4, 20):
            spread = (row - 3) * 2 // 3
            left, right = 11 - spread, 20 + spread
            text(left, row, "/")
            text(right, row, "\\")
            if row % 2:
                text(14 - spread // 3, row, "/")
                text(17 + spread // 3, row, "\\")
        panel(0, 20, 32, 3)
    elif game == "brick-pulse":
        # Its flat arena frame is authored in the same PCG bank as the sprites.
        pass
    elif game == "star-lance":
        for x, y in ((6, 2), (24, 2), (3, 11), (12, 12), (29, 10), (7, 18), (22, 21)):
            text(x, y, ".")
        hline(0, 14, 32, "-")
        hline(0, 16, 32)
    elif game == "lunar-touchdown":
        text(0, 2, "   .       +     .")
        text(1, 18, "/\\       /\\")
        text(0, 19, "/  \\_____/  \\__")
        text(0, 21, "_  __  ___   ___    _")
        panel(21, 2, 11, 13)
    elif game == "echo-parry":
        text(4, 8, "/                      \\")
        text(2, 16, "/__________________________\\")
        text(2, 17, "\\__________________________/")
        for x in (3, 9, 22, 28):
            text(x, 15, "/" if x < 16 else "\\")
        panel(0, 18, 32, 4)
    elif game == "pendulum-port":
        text(10, 2, "/__________\\")
        text(12, 5, "|    |")
        text(0, 19, "\\______________________________/")
        text(2, 21, "__  ___  ____  ___  ___  __")
    elif game == "ruin-lexicon":
        panel(1, 3, 15, 16)
        panel(18, 3, 13, 15)
        for y in (7, 11, 15):
            hline(3, y, 11, "-")
    elif game == "shadow-archive":
        panel(0, 3, 17, 14)
        panel(17, 3, 15, 16)
        for y in (9, 15):
            hline(2, y, 13)
    elif game == "tidal-nets":
        text(0, 5, "  __     ___      ___      __")
        for y, pattern in (
            (6, "~     ~     ~      ~     ~"),
            (12, "  ~~~~    ~~~~     ~~~~    ~~~"),
            (16, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"),
        ):
            text(0, y, pattern)
        hline(0, 18, 32)
    elif game == "auction-house":
        panel(17, 3, 15, 16)
        text(2, 11, "/___________/")
        text(1, 12, "/___________/|")
        text(1, 13, "|___________|/")
        text(3, 14, "|       |")
    elif game == "metro-weave":
        for y in (7, 12, 17):
            text(8, y, "\\____________________/")
            if y < 17:
                text(9, y + 1, "| .  .  .  .  .  . |")
        hline(1, 21, 30)
    elif game == "cargo-balance":
        text(0, 16, "/______________________________/")
        text(0, 17, "\\______________________________|")
        text(1, 18, "\\____________________________/")
        text(0, 21, "~~     ~~~~~    ~~~~~     ~~~~~")
    elif game == "number-vault":
        panel(1, 4, 31, 7)
        panel(1, 12, 15, 5)
        panel(17, 12, 15, 5)
    elif game == "fuse-box":
        board(4, 4, 16, 16)
        instruments(21)
    elif game == "word-foundry":
        # Letter keys have individual bevels below their three-character faces.
        for y in (8, 11, 14, 17):
            for x in (2, 10, 18, 26):
                text(x, y + 1, "___/")
                text(x + 3, y, "|")
        text(1, 19, "\\____________________________/")
    else:
        raise ValueError(game)
