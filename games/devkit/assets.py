"""Build PCG, screens and sound entirely from a new game's own assets."""

import json

from art import emit, quad_bank, quads, sound, word
from devkit.project import read_json


def put(screen, x, y, value):
    assert 0 <= x and x + len(value) <= 32 and 0 <= y < 24, "Static text exceeds the screen"
    screen[y * 32 + x:y * 32 + x + len(value)] = [64 if c == " " else ord(c) - 32 for c in value]


def generate(output, metadata, directory):
    art = read_json(directory / metadata["artSource"])
    bank = [sum((sprite[y + dy][x + dx] == "#") << (7 - dx) for dx in range(8))
            for sprite in art["sprites"] for y in (0, 8) for x in (0, 8) for dy in range(8)]
    pixels = [[0] * 64 for _ in range(48)]
    for i, line in enumerate(art["logo"]):
        word(pixels, line, 4 + 9 * i)
    title = quads(pixels)
    put(title, (32-len(art["tagline"])) // 2, 17, art["tagline"])
    put(title, 5, 20, "RETURN OR BUTTON: PLAY")
    put(title, 1, 22, "DIRECTION: HELP / CTRL+C: EXIT")
    hud, guide = [64] * 768, [64] * 768
    put(hud, 0, 0, metadata["title"])
    put(hud, 25, 0, "STG")
    for y, x, value in metadata["hud"]:
        put(hud, x, y, value)
    put(guide, 0, 0, metadata["title"])
    for i, value in enumerate(metadata["help"]):
        put(guide, 1, 3 + 2*i, value)
    put(guide, 1, 21, "SPACE: RESTART / CTRL+C: EXIT")
    put(guide, 1, 23, "ANY INPUT: TITLE")
    pcg = quad_bank()
    source = emit("TITLE_PCG", pcg) + emit("TITLE_SCREEN", title) + emit("GAME_PCG", bank)
    source += emit("HUD_SCREEN", hud) + emit("HELP_SCREEN", guide)
    for name, value in (("CLEAR", "CLEAR - RETURN FOR NEXT STAGE"), ("LOSE", "TRY AGAIN - RETURN TO RESTART"), ("END", "ALL STAGES CLEAR - THANK YOU")):
        source += emit("STATUS_" + name, [*value.encode("ascii"), 0])
    levels = read_json(directory / "levels.json")
    source += "N_LEVEL_TABLE:\n    .word " + ",".join(f"N_LEVEL_{i}" for i in range(len(levels))) + "\n"
    for i, values in enumerate(levels):
        source += emit(f"N_LEVEL_{i}", values + [0] * (128-len(values)))
    for name, values in metadata.get("dataTables", {}).items():
        source += emit(name.upper() + "_ARRAY", values)
    source += "SFX_TABLE:\n    .word SFX_MOVE,SFX_USE,SFX_WIN,SFX_LOSE\n"
    source += sound(art["effects"], art["music"])
    (output / "assets.inc").write_text(source)
    (output / "levels.inc").write_text("")
    (output / "art.json").write_text(json.dumps({"title_pcg": pcg, "title_screen": title, "game_pcg": bank}) + "\n")
