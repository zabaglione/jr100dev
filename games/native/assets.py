"""Build the authored artwork and static instrument panels for native games."""

import json
import random

from art import emit, sound
from artwork import put, sprite_bank, title


def theme(info):
    rng = random.Random(info["id"])
    scales = [(0, 2, 5, 7, 9), (0, 3, 5, 7, 10), (0, 2, 4, 7, 11), (0, 4, 7, 9, 12)]
    scale = scales[sum(map(ord, info["id"])) % 4]
    phrases = [[rng.randrange(5) for _ in range(6)] for _ in range(4)]
    events = []
    for section in range(4):
        for bar in range(8):
            phrase = phrases[(bar // 2 + section) % 4]
            for beat, degree in enumerate(phrase):
                pitch = (
                    6
                    + scale[degree]
                    + (12 if section == 1 else 0)
                    + (3 if section == 3 else 0)
                )
                events += [
                    0 if (beat == 5 or (section == 2 and beat % 2)) else pitch,
                    16 if beat < 4 else 32,
                ]
    return events + [255]


def generate(output, metadata, directory):
    library = json.loads((directory.parent / "library.json").read_text())
    info = next(g for g in library["games"] if g["id"] == metadata["id"])
    pcg, screen = title(info)
    hud = [64] * 768
    guide = [64] * 768
    put(hud, 0, 0, info["title"][:24])
    put(hud, 25, 0, "STG")
    for y, x, value in metadata["hud"]:
        put(hud, x, y, value)
    put(hud, 0, 23, metadata.get("footer", "WASD MOVE  RET USE  SPACE RETRY"))
    put(guide, 0, 0, info["title"])
    for i, value in enumerate(metadata["help"]):
        put(guide, 1, 3 + i * 2, value)
    put(guide, 1, 22, "ANY INPUT : TITLE")
    bank = sprite_bank(info)
    text = (
        emit("TITLE_PCG", pcg) + emit("TITLE_SCREEN", screen) + emit("GAME_PCG", bank)
    )
    text += emit("HUD_SCREEN", hud) + emit("HELP_SCREEN", guide)
    for label, value in [
        ("STATUS_CLEAR", "CLEAR - BUTTON FOR NEXT STAGE"),
        ("STATUS_LOSE", "TRY AGAIN - BUTTON TO RESTART"),
        ("STATUS_END", "ALL STAGES CLEAR - THANK YOU"),
    ]:
        text += emit(label, [*value.encode(), 0])
    level_file = directory / "levels.json"
    if level_file.exists():
        levels = json.loads(level_file.read_text())
        assert len(levels) == metadata["levels"]
        text += (
            "N_LEVEL_TABLE:\n    .word "
            + ",".join(f"N_LEVEL_{i}" for i in range(len(levels)))
            + "\n"
        )
        for i, values in enumerate(levels):
            assert len(values) <= 128
            text += emit(f"N_LEVEL_{i}", values + [0] * (128 - len(values)))
    else:
        text += (
            "N_LEVEL_TABLE:\n    .word "
            + ",".join(["N_EMPTY_LEVEL"] * metadata.get("levels", 10))
            + "\n"
        )
        text += emit("N_EMPTY_LEVEL", [0] * 128)
    for name, values in metadata.get("dataTables", {}).items():
        text += emit(name.upper() + "_ARRAY", values)
    text += "SFX_TABLE:\n    .word SFX_MOVE,SFX_USE,SFX_WIN,SFX_LOSE\n"
    shift = sum(map(ord, info["id"])) % 7
    text += sound(
        {
            "SFX_MOVE": [1, 1, 18 + shift, 1],
            "SFX_USE": [2, 2, 25 + shift, 2, 32 + shift, 3],
            "SFX_WIN": [4, 4, 18, 4, 25, 4, 30, 4, 37, 12],
            "SFX_LOSE": [4, 3, 20, 4, 13, 6, 6, 10],
        },
        theme(info),
    )
    (output / "assets.inc").write_text(text)
    (output / "levels.inc").write_text("")
    (output / "art.json").write_text(
        json.dumps({"title_pcg": pcg, "title_screen": screen, "game_pcg": bank}) + "\n"
    )
