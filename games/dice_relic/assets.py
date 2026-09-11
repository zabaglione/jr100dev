"""Carved dice, original guardians, and long single-voice scores."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "common"))
from art import emit, extended_theme, quad_bank, quads, sound, strings, text_table, word


def dice(value):
    p = [[0] * 12 for _ in range(12)]
    for y in range(12):
        for x in range(12):
            p[y][x] = x in (0, 11) or y in (0, 11)
    if value == 0:
        for x in range(2, 10):
            p[x][x] = p[x][11 - x] = 1
    else:
        dots = {
            1: [(5, 5)],
            2: [(2, 2), (8, 8)],
            3: [(2, 2), (5, 5), (8, 8)],
            4: [(2, 2), (8, 2), (2, 8), (8, 8)],
            5: [(2, 2), (8, 2), (5, 5), (2, 8), (8, 8)],
            6: [(2, 2), (8, 2), (2, 5), (8, 5), (2, 8), (8, 8)],
            7: [(2, 2), (8, 2), (2, 5), (5, 5), (8, 5), (2, 8), (8, 8)],
            8: [(2, 2), (5, 2), (8, 2), (2, 5), (8, 5), (2, 8), (5, 8), (8, 8)],
            9: [(x, y) for y in (2, 5, 8) for x in (2, 5, 8)],
        }[value]
        for x, y in dots:
            for dy in range(2):
                for dx in range(2):
                    p[y + dy][x + dx] = 1
    return quads(p)


def enemy(n):
    p = [[0] * 16 for _ in range(16)]
    for y in range(2, 14):
        for x in range(2, 14):
            width = 3 + (n % 3) + (2 if y in range(7, 10) else 0)
            p[y][x] = abs(x - 7.5) <= width and (y < 11 or x % 4 < 2)
    for x in (5, 10):
        p[5][x] = p[6][x] = 0
    for x in range(5, 11):
        p[9][x] = 0
    for x in (2, 5, 10, 13):
        for y in range(n % 3 + 1):
            p[y][x] = 1
    for y in (4, 8, 12):
        if n & 1:
            p[y][0] = p[y][15] = 1
    if n == 8:
        for x in range(1, 15):
            p[0][x] = 1
    return quads(p)


def generate(output):
    p = [[0] * 64 for _ in range(48)]
    word(p, "DICE", 8)
    word(p, "RELIC", 22)
    for cx, cy in [(12, 17), (51, 17)]:
        for y in range(-5, 6):
            for x in range(-5, 6):
                if abs(x) == 5 or abs(y) == 5:
                    p[cy + y][cx + x] = 1
        for x, y in [(-2, -2), (2, 2), (0, 0)]:
            p[cy + y][cx + x] = 1
    for x in range(5, 59):
        p[33][x] = 1
    screen = quads(p)
    pcg = quad_bank()
    pcg[16 * 8 : 17 * 8] = [0, 0, 0, 255, 0, 255, 0, 0]
    pcg[17 * 8 : 18 * 8] = [129] * 8
    text = (
        emit("TITLE_PCG", quad_bank())
        + emit("TITLE_SCREEN", screen)
        + emit("GAME_PCG", pcg)
    )
    text += "DICE_TABLE:\n    .word " + ",".join(f"DIE_{i}" for i in range(10)) + "\n"
    for i in range(10):
        text += emit(f"DIE_{i}", dice(i))
    text += (
        "MONSTER_TABLE:\n    .word " + ",".join(f"ENEMY_{i}" for i in range(9)) + "\n"
    )
    for i in range(9):
        text += emit(f"ENEMY_{i}", enemy(i))
    enemies = json.loads((ROOT / "enemies.json").read_text())
    text += emit(
        "ENEMY_STATS", [v for e in enemies for v in (e["hp"], e["attack"])]
    ) + strings("ENEMY_NAMES", [e["name"] for e in enemies])
    text += strings("CHOICE_NAMES", ["ATTACK", "GUARD", "HEAL", "REROLL"])
    tables = {
        "TITLE_TEXT": [
            (1, 5, "CARVE YOUR OWN FORTUNE"),
            (19, 5, "THREE DICE. NINE GUARDIANS."),
            (21, 7, "RETURN / PAD : BEGIN"),
            (23, 8, "SPACE : FIELD GUIDE"),
        ],
        "HUD_TEXT": [
            (0, 0, "HP"),
            (0, 10, "SH"),
            (0, 21, "GOLD"),
            (1, 0, "FIGHT"),
            (1, 23, "TURN"),
            (3, 1, "ENEMY"),
            (6, 1, "NEXT"),
            (8, 22, "REROLL"),
            (11, 1, "DIE 1"),
            (11, 11, "DIE 2"),
            (11, 21, "DIE 3"),
            (22, 0, "A/D DIE  W/X ACTION  BUTTON USE"),
            (23, 0, "CTRL+C EXIT"),
        ],
        "SHOP_TEXT": [
            (0, 0, "HP"),
            (0, 10, "SH"),
            (0, 21, "GOLD"),
            (1, 8, "RELIC WORKSHOP"),
            (2, 0, "FORGE +2: 3G  HEAL 6HP: 2G"),
            (4, 0, "I"),
            (6, 0, "II"),
            (8, 0, "III"),
            (11, 1, "DIE 1"),
            (11, 11, "DIE 2"),
            (11, 21, "DIE 3"),
            (22, 0, "A/D DIE  W/X FACE  BUTTON MENU"),
            (23, 0, "NEW FACES STAY FOR ALL BATTLES"),
        ],
        "HELP_TEXT": [
            (1, 10, "DICE RELIC"),
            (3, 1, "ROLL THREE DICE. USE EACH ONCE."),
            (5, 1, "A/D : CHOOSE AN UNUSED DIE"),
            (6, 1, "W/X : ATTACK, GUARD OR HEAL"),
            (7, 1, "BUTTON : APPLY THE SHOWN VALUE"),
            (9, 1, "REROLL ONE UNUSED DIE PER TURN."),
            (10, 1, "ALL THREE USED? ENEMY ATTACKS."),
            (11, 1, "GUARD ABSORBS THAT ATTACK."),
            (12, 1, "EVERY FOURTH ATTACK IS +2."),
            (14, 1, "WIN: HEAL 2 HP AND GAIN 3 GOLD."),
            (15, 1, "FORGE: REPLACE A FACE WITH +2."),
            (16, 1, "FACE VALUES CANNOT EXCEED 9."),
            (18, 1, "WORKSHOP: CHOOSE DIE AND FACE,"),
            (19, 1, "THEN OPEN THE SERVICE MENU."),
            (22, 7, "ANY INPUT : TITLE"),
        ],
        "WIN_TEXT": [
            (5, 7, "FORTUNE REFORGED"),
            (9, 4, "THE FIRST KING HAS FALLEN."),
            (12, 4, "THE RELICS ANSWER TO YOU."),
            (18, 7, "ANY INPUT : TITLE"),
        ],
        "LOST_TEXT": [
            (6, 7, "THE LAST THROW"),
            (10, 3, "THE GUARDIANS KEEP THE GOLD."),
            (16, 5, "RETURN / PAD : BEGIN AGAIN"),
            (19, 7, "SPACE : TITLE"),
        ],
        "SERVICE_TEXT": [
            (20, 1, "FORGE"),
            (20, 9, "HEAL"),
            (20, 17, "NEXT"),
            (20, 25, "BACK"),
        ],
    }
    for name, rows in tables.items():
        text += text_table(name, rows)
    for label, value in {
        "ERROR_TEXT": "UNAVAILABLE / CHECK GOLD OR USE",
        "ROLLING_TEXT": "ROLLING THE RELICS",
    }.items():
        text += emit(label, [*value.encode(), 0])
    text += sound(
        {
            "SFX_ROLL": [2, 6, 9, 1, 16, 1, 11, 1, 20, 1, 13, 1, 25, 2],
            "SFX_HIT": [3, 3, 35, 1, 22, 2, 10, 2],
            "SFX_GUARD": [2, 2, 13, 2, 20, 3],
            "SFX_HEAL": [3, 3, 20, 2, 25, 2, 32, 5],
            "SFX_EMPTY": [2, 1, 5, 4],
            "SFX_DAMAGE": [4, 2, 12, 3, 3, 4],
            "SFX_FORGE": [3, 3, 30, 2, 35, 2, 42, 5],
            "SFX_CLEAR": [4, 5, 13, 3, 17, 3, 20, 3, 25, 3, 32, 10],
            "SFX_DEATH": [5, 4, 20, 5, 15, 5, 10, 5, 3, 10],
        },
        extended_theme(5, (0, 3, 7, 8, 12, 15, 19, 20)),
    )
    text += emit("MUSIC_BATTLE", extended_theme(3, (0, 2, 7, 9, 12, 14, 19, 21)))
    (output / "assets.inc").write_text(text)
    (output / "levels.inc").write_text("")
    (output / "art.json").write_text(
        json.dumps(
            {"title_pcg": quad_bank(), "title_screen": screen, "game_pcg": pcg},
            indent=2,
        )
        + "\n"
    )
