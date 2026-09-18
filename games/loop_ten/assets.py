"""Original looping clock, chamber maps and persistent-seal tiles."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "common"))
from art import emit, extended_theme, quad_bank, quads, sound, strings, text_table, word
from relief import replace_sprites


def tile(kind):
    p = [[0] * 16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            if kind == 0:
                v = (
                    x in (0, 15)
                    or y in (0, 15)
                    or (y == 8 and x > 2)
                    or (x == 8 and y < 8)
                )
            elif kind == 1:
                v = (
                    (5 <= x <= 9 and 2 <= y <= 5)
                    or (3 <= x <= 11 and 7 <= y <= 12)
                    or (y == 13 and x in (3, 4, 10, 11))
                )
            elif kind == 2:
                v = x in (1, 4, 11, 14) or y in (1, 14) or (y == 8 and 4 <= x <= 11)
            elif kind == 3:
                v = abs(x - 7) + abs(y - 7) in (5, 6) or (x == 7 and y < 8)
            elif kind == 4:
                v = abs(x - 7) + abs(y - 7) <= 5
            elif kind == 5:
                v = (
                    36 <= (x - 7) ** 2 + (y - 7) ** 2 <= 55
                    or (y == 7 and 7 <= x <= 11)
                    or (x == 7 and 3 <= y <= 7)
                )
            elif kind == 6:
                v = x == y or x + y == 15 or (x in (6, 7, 8, 9) and y in (6, 7, 8, 9))
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
    word(p, "LOOP", 9)
    word(p, "TEN", 23)
    for cx in (10, 53):
        for y in range(10, 29):
            for x in range(cx - 9, cx + 10):
                d = (x - cx) ** 2 + (y - 19) ** 2
                if 64 <= d <= 85:
                    p[y][x] = 1
        for y in range(14, 20):
            p[y][cx] = 1
        for x in range(cx, cx + 5):
            p[19][x] = 1
    screen = quads(p)
    pcg = [b for i in range(8) for b in tile(i)]
    pcg = replace_sprites(
        pcg, {0: "wall-stone", 1: "person", 2: "door", 3: "socket", 4: "gem"}
    )
    pcg[30 * 8 : 31 * 8] = [255] * 8
    text = (
        emit("TITLE_PCG", quad_bank())
        + emit("TITLE_SCREEN", screen)
        + emit("GAME_PCG", pcg)
    )
    rooms = json.loads((ROOT / "rooms.json").read_text())
    text += "ROOM_TABLE:\n    .word " + ",".join(f"ROOM_{i}" for i in range(12)) + "\n"
    for i, room in enumerate(rooms):
        text += emit(f"ROOM_{i}", [v for row in room["map"] for v in row])
    text += strings("ROOM_NAMES", [r["name"] for r in rooms])
    tables = {
        "TITLE_TEXT": [
            (1, 6, "THE DOORS REMEMBER YOU"),
            (18, 5, "TEN SECONDS. TWELVE SEALS."),
            (21, 5, "RETURN / PAD : START LOOP"),
            (23, 7, "SPACE : FIELD GUIDE"),
        ],
        "HUD_TEXT": [
            (0, 0, "TIME"),
            (0, 10, "LOOP"),
            (0, 22, "ROOM"),
        ],
        "HELP_TEXT": [
            (1, 11, "LOOP TEN"),
            (3, 1, "TEN REAL SECONDS PER ATTEMPT."),
            (5, 1, "WASD / PAD : MOVE (HOLD OK)"),
            (6, 1, "RETURN / BUTTON : USE NEARBY"),
            (7, 1, "SPACE : REWIND EARLY"),
            (9, 1, "LIGHT EACH DIAMOND SEAL."),
            (10, 1, "ITS ROOM GATE STAYS OPEN."),
            (11, 1, "THE CLOCK AT THE START TAKES"),
            (12, 1, "YOU TO THE FIRST UNLIT ROOM."),
            (14, 1, "THE TIMER NEVER PAUSES."),
            (15, 1, "SPIKES SEND YOU BACK TO WAKE."),
            (17, 1, "AFTER A REWIND, SEALS REMAIN."),
            (18, 1, "REUSE A LIT SEAL TO REWIND."),
            (19, 1, "LIGHT ALL TWELVE TO ESCAPE."),
            (20, 1, "CTRL+C RETURNS TO BASIC."),
            (22, 7, "ANY INPUT : TITLE"),
        ],
        "WIN_TEXT": [
            (5, 8, "BEYOND THE LOOP"),
            (8, 5, "TWELVE DOORS REMEMBER YOU."),
            (11, 7, "DAWN NO LONGER REPEATS."),
            (14, 11, "LOOPS USED"),
            (20, 7, "ANY INPUT : TITLE"),
        ],
    }
    for name, rows in tables.items():
        text += text_table(name, rows)
    text += sound(
        {
            "SFX_STEP": [1, 1, 15, 1],
            "SFX_EMPTY": [1, 1, 5, 2],
            "SFX_HIT": [4, 3, 18, 2, 8, 3, 2, 6],
            "SFX_REWIND": [3, 4, 32, 2, 25, 2, 18, 2, 11, 3],
            "SFX_ANCHOR": [2, 3, 13, 2, 20, 2, 25, 4],
            "SFX_SEAL": [3, 3, 20, 2, 25, 2, 32, 6],
            "SFX_TICK": [2, 1, 37, 2],
        },
        extended_theme(3, (0, 4, 7, 9, 12, 16, 19, 21)),
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
