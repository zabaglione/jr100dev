"""Build the authored artwork and static instrument panels for native games."""

import json
import random

from art import emit, sound
from artwork import put, title
from depth_panels import decorate
from relief import native_bank


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
    ranked = metadata.get("rankedCampaign", False)
    if ranked:
        put(screen, 0, 21, " " * 32)
        put(screen, 1, 21, "RET PLAY F MAP X LOAD SPACE ?")
        put(screen, 0, 23, " " * 32)
        put(screen, 4, 23, "40 ROOMS / CTRL+C EXIT")
    hud = [64] * 768
    guide = [64] * 768
    decorate(hud, info["id"])
    put(hud, 0, 0, info["title"][:24])
    put(hud, 25, 0, "STG")
    for y, x, value in metadata["hud"]:
        put(hud, x, y, value)
    put(hud, 0, 23, metadata.get("footer", "WASD MOVE  RET USE  SPACE RETRY"))
    put(guide, 0, 0, info["title"])
    for i, value in enumerate(metadata["help"]):
        put(guide, 1, 3 + i * 2, value)
    put(guide, 1, 22, "ANY INPUT : TITLE")
    bank = native_bank(info)
    if ranked:
        # A faceted optional rune (tile 6), plus filled/empty 8x8 rating stars.
        rune = [
            [
                int(
                    28 <= (x - 7) ** 2 + (y - 7) ** 2 <= 42
                    or (x == 7 and 4 <= y <= 10)
                    or (y == 7 and 4 <= x <= 10)
                )
                for x in range(16)
            ]
            for y in range(16)
        ]
        bank[192:224] = [
            sum(rune[y + dy][x + dx] << (7 - dx) for dx in range(8))
            for y in (0, 8)
            for x in (0, 8)
            for dy in range(8)
        ]
        bank[224:240] = [
            16,
            56,
            254,
            124,
            56,
            108,
            198,
            0,
            16,
            40,
            198,
            68,
            40,
            84,
            130,
            0,
        ]
        put(hud, 1, 21, "BEST       F MAP  NOW")
    text = (
        emit("TITLE_PCG", pcg) + emit("TITLE_SCREEN", screen) + emit("GAME_PCG", bank)
    )
    text += emit("HUD_SCREEN", hud) + emit("HELP_SCREEN", guide)
    for label, value in [
        (
            "STATUS_CLEAR",
            "RETURN NEXT  SPACE RETRY  F MAP"
            if ranked
            else "CLEAR - BUTTON FOR NEXT STAGE",
        ),
        ("STATUS_LOSE", "TRY AGAIN - BUTTON TO RESTART"),
        ("STATUS_END", "ALL STAGES CLEAR - THANK YOU"),
    ]:
        text += emit(label, [*value.encode(), 0])
    if ranked:
        for label, value in {
            "SELECT_HEADER": "FORTY CHAMBERS / STAR RECORDS",
            "SELECT_FOOTER": "TOTAL STARS 000 / 120",
            "SELECT_PAR": "STAGE 000 / PAR 000",
            "SELECT_CONTROLS": "WASD SELECT / RETURN PLAY",
            "SELECT_EXIT": "SPACE TITLE / X PASSWORD LOAD",
        }.items():
            text += emit(label, [*value.encode(), 0])
        from password import ALPHABET, TAGS

        text += f"PASSWORD_TAG: .equ {TAGS[metadata['id']]}\n"
        for label, value in {
            "PASSWORD_ALPHABET": ALPHABET,
            "PASSWORD_LABEL": "PW ",
            "PASSWORD_TITLE": "PASSWORD RESTORE",
            "PASSWORD_GAME": info["title"],
            "PASSWORD_HINT": "TYPE LETTERS / RETURN TO LOAD",
            "PASSWORD_FIELD": "____ ____ ____ ____ ____ ____",
            "PASSWORD_LENGTH": "LENGTH 000 / 24",
            "PASSWORD_DELETE": "- / BACKSPACE : ERASE",
            "PASSWORD_CANCEL": "X : CANCEL / SPACES IGNORED",
            "PASSWORD_PAD": "PAD SELECT / BUTTON CHOOSE",
            "PASSWORD_ERROR": "CHECK CODE AND GAME TITLE",
            "PASSWORD_LOAD": "LOAD",
            "PASSWORD_DEL": "DEL",
            "PASSWORD_BACK": "BACK",
        }.items():
            text += emit(label, [*value.encode(), 0])
        text += (
            "PASSWORD_COMMANDS:\n    .word PASSWORD_LOAD,PASSWORD_DEL,PASSWORD_BACK\n"
        )
        text += "PASSWORD_SCREEN:\n"
        for y, x, label in [
            (0, 8, "TITLE"),
            (2, 1, "HINT"),
            (3, 1, "GAME"),
            (6, 3, "FIELD"),
            (7, 10, "LENGTH"),
            (19, 3, "DELETE"),
            (21, 2, "PAD"),
            (23, 2, "CANCEL"),
        ]:
            text += f"    .word FRAMEBUFFER + {y * 32 + x},PASSWORD_{label}\n"
        text += "    .word 0\n"
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
            if ranked:
                assert len(values) == 70 and all(0 <= v < 16 for v in values[:64])
                packed = [values[j] * 16 + values[j + 1] for j in range(0, 64, 2)]
                text += emit(f"N_LEVEL_{i}", packed + values[64:])
            else:
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
