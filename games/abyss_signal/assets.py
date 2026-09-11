"""Original sonar tiles and five full-screen underwater discoveries."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "common"))
from art import emit, extended_theme, quad_bank, quads, sound, strings, text_table, word
from relief import Pixels


def line(p, x0, y0, x1, y1):
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(steps + 1):
        x = round(x0 + (x1 - x0) * i / steps)
        y = round(y0 + (y1 - y0) * i / steps)
        if 0 <= y < len(p) and 0 <= x < len(p[0]):
            p[y][x] = 1


def ring(p, cx, cy, r):
    for y in range(len(p)):
        for x in range(len(p[0])):
            if r * r - r <= (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r:
                p[y][x] = 1


def sprite(kind):
    p = [[0] * 16 for _ in range(16)]
    if kind == 0:
        for a in [
            (2, 6, 12, 6),
            (1, 7, 13, 7),
            (1, 10, 13, 10),
            (2, 11, 12, 11),
            (0, 8, 0, 9),
            (14, 8, 15, 8),
            (14, 9, 15, 9),
            (7, 3, 7, 5),
            (7, 3, 10, 3),
            (6, 8, 9, 8),
            (6, 9, 9, 9),
        ]:
            line(p, *a)
    elif kind == 1:
        for a in [
            (3, 0, 12, 0),
            (0, 4, 3, 0),
            (0, 4, 1, 13),
            (1, 13, 9, 15),
            (9, 15, 15, 11),
            (15, 11, 12, 0),
            (3, 7, 10, 4),
            (5, 12, 12, 9),
        ]:
            line(p, *a)
    elif kind == 2:
        ring(p, 7, 7, 6)
        for a in [(3, 7, 11, 7), (7, 3, 7, 11), (0, 0, 2, 0), (15, 13, 15, 15)]:
            line(p, *a)
    elif kind == 3:
        for y in range(4, 12):
            for x in range(2, 13):
                p[y][x] = abs(y - 8) + abs(x - 7) // 2 < 5
        p[7][10] = p[8][10] = 0
        for a in [(0, 4, 2, 7), (0, 12, 2, 9), (6, 2, 9, 4), (5, 13, 9, 11)]:
            line(p, *a)
    elif kind == 4:
        for y in range(1, 16, 4):
            for x in range(1, 16, 4):
                p[y][x] = 1
    elif kind == 5:
        for a in [
            (0, 4, 4, 2),
            (4, 2, 8, 4),
            (8, 4, 12, 2),
            (12, 2, 15, 4),
            (0, 10, 4, 8),
            (4, 8, 7, 10),
        ]:
            line(p, *a)
    else:
        ring(p, 7, 7, 6)
        ring(p, 7, 7, 3)
    if kind == 1:
        # Preserve the irregular rock silhouette; facets suggest its shaded side.
        for y in range(3, 12, 2):
            line(p, 11, y, 13, y + 1)
    if kind == 0:
        line(p, 3, 12, 12, 12)
        p[13][4] = p[13][8] = p[13][12] = 1
    return [
        sum(p[y + dy][x + dx] << (7 - dx) for dx in range(8))
        for y in (0, 8)
        for x in (0, 8)
        for dy in range(8)
    ]


def title():
    p = [[0] * 64 for _ in range(48)]
    word(p, "ABYSS", 8)
    word(p, "SIGNAL", 19)
    for x in range(4, 60):
        if x % 5:
            p[4][x] = 1
        p[29 + (x % 7 == 0)][x] = 1
    ring(p, 31, 36, 5)
    line(p, 31, 36, 35, 32)
    for x in (6, 56):
        line(p, x, 7, x, 27)
        line(p, x - 2, 14, x + 2, 14)
    return quads(p)


def photo(index):
    p = [[0] * 64 for _ in range(36)]
    # A sparse receding seabed sits behind the original discovery silhouettes.
    ground = Pixels(64, 36)
    for end in (0, 16, 47, 63):
        ground.line(31 + (end - 31) // 3, 26, end, 35)
    ground.line(0, 30, 63, 30)
    ground.line(0, 34, 63, 34)
    p = ground.p
    # Sparse particles, layered seabed, and unique authored silhouettes.
    for x in range(64):
        p[32 + (x * 7 % 3)][x] = 1
        if x % 3 == 0:
            p[35][x] = 1
    for x, y in [(4, 4), (11, 11), (55, 6), (59, 19), (6, 24), (49, 2)]:
        p[y][x] = 1
    if index == 0:
        for a in [
            (23, 30, 27, 14),
            (27, 14, 37, 14),
            (37, 14, 41, 30),
            (27, 18, 37, 18),
            (25, 24, 39, 24),
            (27, 14, 39, 30),
            (37, 14, 23, 30),
            (31, 13, 31, 7),
            (20, 4, 25, 11),
            (25, 11, 37, 11),
            (37, 11, 43, 4),
            (20, 4, 43, 4),
            (23, 6, 39, 6),
        ]:
            line(p, *a)
    elif index == 1:
        for a in [
            (14, 31, 14, 8),
            (14, 8, 25, 3),
            (25, 3, 42, 3),
            (42, 3, 50, 10),
            (50, 10, 50, 31),
            (18, 31, 18, 10),
            (18, 10, 26, 7),
            (26, 7, 39, 7),
            (39, 7, 45, 12),
            (45, 12, 45, 31),
            (14, 26, 18, 26),
            (45, 24, 50, 24),
            (14, 17, 18, 17),
            (45, 19, 50, 19),
        ]:
            line(p, *a)
        for x, y in [(29, 5), (33, 7), (38, 4), (32, 28), (38, 29)]:
            line(p, x, y, x + 2, y + 2)
    elif index == 2:
        for x, y, h in [
            (10, 31, 13),
            (22, 31, 24),
            (34, 31, 17),
            (47, 31, 26),
            (56, 31, 12),
        ]:
            for a in [
                (x, y, x - 4, y - h + 5),
                (x - 4, y - h + 5, x, y - h),
                (x, y - h, x + 4, y - h + 5),
                (x + 4, y - h + 5, x, y),
                (x, y - h, x, y),
                (x - 4, y - h + 5, x + 4, y - h + 5),
            ]:
                line(p, *a)
    elif index == 3:
        for x, y in [(10, 16), (26, 11), (44, 18)]:
            for a in [
                (x, y, x + 9, y),
                (x, y, x - 3, y - 6),
                (x - 3, y - 6, x + 12, y - 6),
                (x + 12, y - 6, x + 9, y),
                (x + 4, y, x + 4, 31),
                (x, y + 2, x + 8, y + 2),
            ]:
                line(p, *a)
        for a in [
            (4, 30, 58, 30),
            (5, 32, 59, 32),
            (38, 8, 38, 20),
            (38, 8, 41, 5),
            (41, 5, 41, 16),
        ]:
            line(p, *a)
    else:
        ring(p, 32, 16, 11)
        ring(p, 32, 16, 13)
        for a in [
            (32, 0, 32, 2),
            (32, 30, 32, 32),
            (15, 16, 17, 16),
            (47, 16, 49, 16),
            (19, 3, 22, 6),
            (42, 26, 45, 29),
            (19, 29, 22, 26),
            (42, 6, 45, 3),
        ]:
            line(p, *a)
        for a in [(26, 30, 26, 33), (38, 30, 38, 33)]:
            line(p, *a)
    return quads(p)


def rle(data):
    result = []
    for value in data:
        if result and result[-1] == value and result[-2] < 255:
            result[-2] += 1
        else:
            result += [1, value]
    return [*result, 0]


def generate(output):
    world = json.loads((ROOT / "world.json").read_text())
    text = emit("TITLE_PCG", quad_bank()) + emit("TITLE_SCREEN", title())
    pcg = (
        [b for k in range(7) for b in sprite(k)]
        + [0, 0, 255, 0, 255, 0, 0, 0]
        + [129] * 8
        + [255] * 8
        + [0, 102, 255, 255, 126, 60, 24, 0]
    )
    assert len(pcg) == 256
    text += emit("GAME_PCG", pcg)
    text += "PHOTO_TABLE:\n    .word " + ",".join(f"PHOTO_{i}" for i in range(5)) + "\n"
    for i in range(5):
        text += emit(f"PHOTO_{i}", rle(photo(i)))
    text += emit("WORLD_MAP", [v for row in world["map"] for v in row])
    text += (
        emit("SITE_X", [site["x"] for site in world["sites"]])
        + emit("SITE_Y", [site["y"] for site in world["sites"]])
        + emit("BIT_MASKS", [1, 2, 4, 8, 16])
    )
    text += strings(
        "SITE_NAMES", [site["name"] for site in world["sites"]] + ["SURFACE BASE"]
    )
    text += strings(
        "BEARING_NAMES", ["HERE", "N", "S", "?", "W", "NW", "SW", "?", "E", "NE", "SE"]
    )
    text += strings(
        "MENU_NAMES",
        ["SONAR PING", "RECORD SITE", "QUIET MODE", "WAIT", "RESTART", "TITLE"],
    )
    tables = {
        "TITLE_TEXT": [
            (1, 7, "DEEP SURVEY / NO. 01"),
            (21, 5, "RETURN / PAD : DIVE"),
            (23, 7, "SPACE : FIELD GUIDE"),
        ],
        "HUD_TEXT": [
            (0, 0, "O2"),
            (0, 23, "HULL"),
            (2, 22, "ABYSS"),
            (3, 22, "SIGNAL"),
            (5, 22, "DEPTH"),
            (7, 25, "X10 M"),
            (8, 22, "RANGE"),
            (10, 22, "BEARING"),
            (12, 22, "SAMPLES"),
            (13, 26, "/005"),
            (15, 22, "ENGINE"),
            (18, 22, "SONAR"),
            (21, 0, "TO:"),
            (22, 0, "WASD MOVE  F PING  X WAIT"),
            (23, 0, "BUTTON MENU  CTRL+C EXIT"),
        ],
        "HELP_TEXT": [
            (1, 9, "ABYSS SIGNAL"),
            (3, 1, "SURVEY FIVE SITES. RETURN HOME."),
            (5, 1, "WASD / PAD : MOVE ONE CELL"),
            (6, 1, "RETURN / BUTTON : OPEN PANEL"),
            (7, 1, "F : SONAR   X : WAIT"),
            (9, 1, "RECORD FROM AN ADJACENT CELL."),
            (10, 1, "ROCK IMPACTS DAMAGE THE HULL."),
            (11, 1, "CURRENTS PUSH AND COST 1 O2."),
            (13, 1, "EACH MOVE / WAIT COSTS 1 O2."),
            (14, 1, "QUIET: COST 2, SLOWER PURSUER."),
            (15, 1, "SONAR / RECORD COST 2 O2."),
            (17, 1, "SONAR REVEALS FOR SIX ACTIONS."),
            (18, 1, "ITS NOISE ATTRACTS THE HUNTER."),
            (20, 1, "PANELS AND PHOTOS PAUSE TIME."),
            (22, 7, "ANY INPUT : TITLE"),
        ],
        "LOST_TEXT": [
            (6, 8, "CONNECTION LOST"),
            (9, 5, "THE ABYSS KEEPS ITS SECRETS"),
            (12, 8, "RECORDS SALVAGED"),
            (16, 5, "RETURN / PAD : TRY AGAIN"),
            (18, 9, "SPACE : TITLE"),
        ],
        "WIN_TEXT": [
            (5, 7, "SURVEY COMPLETE"),
            (8, 4, "FIVE SIGNALS. ONE WAY HOME."),
            (11, 7, "ALL RECORDS RECOVERED"),
            (15, 8, "OXYGEN REMAINING"),
            (20, 6, "ANY INPUT : TITLE"),
        ],
        "PHOTO_TEXT": [(22, 3, "ARCHIVE SAVED / BUTTON RETURN")],
    }
    for name, rows in tables.items():
        text += text_table(name, rows)
    for name, value in {
        "CRUISE_TEXT": "CRUISE",
        "QUIET_TEXT": "SILENT",
        "READY_TEXT": "READY",
        "ACTIVE_TEXT": "ACTIVE",
        "NONE_TEXT": "NO SITE IN RECORDING RANGE",
        "MENU_TEXT": "CONTROL PANEL",
        "CONTACT_TEXT": "CONTACT",
        "CLEAR_TEXT": "CLEAR",
    }.items():
        text += emit(name, [*value.encode(), 0])
    text += sound(
        {
            "SFX_WARNING": [3, 2, 25, 2, 13, 2],
            "SFX_MENU": [1, 1, 21, 2],
            "SFX_MOVE": [1, 1, 9, 1],
            "SFX_HIT": [4, 3, 17, 2, 8, 4, 1, 5],
            "SFX_SONAR": [2, 3, 37, 3, 0, 6, 37, 2],
            "SFX_CURRENT": [2, 2, 13, 2, 20, 2],
            "SFX_RECORD": [3, 4, 20, 3, 25, 3, 29, 3, 32, 8],
            "SFX_EMPTY": [2, 1, 5, 4],
            "SFX_CLEAR": [4, 5, 13, 5, 20, 5, 25, 5, 29, 5, 37, 12],
            "SFX_DEATH": [5, 4, 13, 6, 8, 6, 4, 6, 1, 12],
        },
        extended_theme(1, (0, 7, 10, 12, 14, 19, 22, 24)),
    )
    (output / "assets.inc").write_text(text)
    (output / "levels.inc").write_text("")
    (output / "art.json").write_text(
        json.dumps(
            {"title_pcg": quad_bank(), "title_screen": title(), "game_pcg": pcg},
            indent=2,
        )
        + "\n"
    )
