"""Original blade emblem, 32 PCG tiles, and thirty fixed puzzle boards."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "common"))
from art import emit, extended_theme, quad_bank, quads, sound, strings, text_table, word
from relief import replace_sprites


def tiles(kind):
    p = [[0] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if kind == 0:
                v = x in (0, 15) or y in (0, 15) or (x + y) % 11 == 0
            elif kind == 1:
                v = (
                    2 <= x <= 13
                    and 2 <= y <= 13
                    and not (y in (6, 7) and x in (4, 5, 10, 11))
                ) and (y <= 10 or 5 <= x <= 10)
            elif kind == 2:
                v = (
                    (4 <= x <= 7 and 2 <= y <= 5)
                    or (3 <= x <= 8 and 7 <= y <= 12)
                    or (x + y == 16 and x >= 8)
                    or (7 <= x <= 11 and y == 8)
                    or (1 <= x <= 4 and y == 7)
                )
            elif kind == 3:
                v = abs(x - 7) + abs(y - 7) in (6, 7) or (x == 7 and y in (6, 7, 8))
            elif kind == 4:
                v = abs(x - 7) + abs(y - 7) <= 2
            elif kind == 5:
                v = (
                    (x in (0, 15) and y in (0, 1, 2, 13, 14, 15))
                    or (y in (0, 15) and x in (0, 1, 2, 13, 14, 15))
                    or (
                        2 <= x <= 13
                        and 2 <= y <= 13
                        and not (y in (6, 7) and x in (4, 5, 10, 11))
                        and (y <= 10 or 5 <= x <= 10)
                    )
                )
            elif kind == 6:
                v = x in (0, 15) and y in (0, 15)
            else:
                v = y in (2, 4)
            p[y][x] = v
    return [
        sum(p[y + dy][x + dx] << (7 - dx) for dx in range(8))
        for y in (0, 8)
        for x in (0, 8)
        for dy in range(8)
    ]


def generate(output):
    p = [[0] * 64 for _ in range(48)]
    word(p, "TRACE", 9)
    word(p, "BLADE", 22)
    for x in range(5, 60):
        p[20 - x // 16][x] = 1
        if x > 20:
            p[21 - x // 16][x] = 1
    for y in range(6, 32):
        p[y][3] = p[y][60] = 1
    screen = quads(p)
    pcg = [b for i in range(8) for b in tiles(i)]
    pcg = replace_sprites(pcg, {0: "wall-stone", 3: "socket"})
    text = (
        emit("TITLE_PCG", quad_bank())
        + emit("TITLE_SCREEN", screen)
        + emit("GAME_PCG", pcg)
    )
    levels = json.loads((ROOT / "levels.json").read_text())
    text += (
        "LEVEL_TABLE:\n    .word " + ",".join(f"LEVEL_{i}" for i in range(30)) + "\n"
    )
    for i, level in enumerate(levels):
        text += emit(f"LEVEL_{i}", [v for row in level["map"] for v in row])
    for name, rows in {
        "TITLE_TEXT": [
            (2, 7, "ONE LINE. EVERY TARGET."),
            (19, 6, "PLAN THE PERFECT STRIKE"),
            (21, 5, "RETURN / PAD : UNSHEATHE"),
            (23, 8, "SPACE : FIELD GUIDE"),
        ],
        "HELP_TEXT": [
            (1, 10, "TRACE BLADE"),
            (3, 1, "THIRTY CHAMBERS. ONE STROKE."),
            (5, 1, "WASD / PAD : EXTEND YOUR PATH"),
            (6, 1, "SPACE : UNDO THE LAST STEP"),
            (7, 1, "RETURN / BUTTON : OPEN MENU"),
            (8, 1, "F : EXECUTE YOUR STRIKE"),
            (10, 1, "MARK EVERY TARGET AND END ON"),
            (11, 1, "THE DIAMOND GATE. THEN CUT."),
            (13, 1, "NEVER CROSS YOUR OWN PATH."),
            (14, 1, "WALLS CANNOT BE CROSSED."),
            (16, 1, "THE MENU ALSO HAS UNDO, RESET"),
            (17, 1, "AND RETURN TO THE TITLE."),
            (20, 1, "THINK AS LONG AS YOU NEED."),
            (22, 6, "ANY INPUT : TITLE"),
        ],
        "HUD_TEXT": [
            (0, 0, "TRACE BLADE"),
            (0, 22, "CUT"),
            (2, 25, "TARGET"),
            (5, 25, "MARKED"),
            (8, 25, "PATH"),
            (11, 25, "COMBO"),
        ],
        "WIN_TEXT": [
            (5, 7, "THE LAST BLADE"),
            (9, 5, "THIRTY CHAMBERS SILENCED"),
            (12, 5, "NO WASTED MOTION REMAINS."),
            (18, 7, "ANY INPUT : TITLE"),
        ],
    }.items():
        text += text_table(name, rows)
    text += strings("MENU_NAMES", ["CUT", "UNDO", "RESET", "TITLE", "BACK"])
    for label, value in {
        "CLEAR_TEXT": "SECTOR CLEAR / BUTTON NEXT",
        "ERROR_TEXT": "CHECK PATH AND ALL TARGETS",
        "EXEC_TEXT": "STRIKE IN MOTION",
    }.items():
        text += emit(label, [*value.encode(), 0])
    text += sound(
        {
            "SFX_STEP": [1, 1, 25, 1],
            "SFX_UNDO": [1, 2, 20, 1, 13, 2],
            "SFX_EMPTY": [2, 1, 6, 3],
            "SFX_CUT": [3, 3, 42, 1, 30, 1, 18, 2],
        },
        extended_theme(3),
    )
    (output / "assets.inc").write_text(text)
    (output / "levels.inc").write_text("")
    (output / "art.json").write_text(
        json.dumps(
            {"title_pcg": quad_bank(), "title_screen": screen, "game_pcg": pcg},
            indent=2,
        )
        + "\n"
    )
