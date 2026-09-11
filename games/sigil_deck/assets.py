"""Original title, eight large PCG monsters, card data and single-voice music."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FONT = {
    "S": ["11111", "10000", "10000", "11111", "00001", "00001", "11111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
}
MONSTERS = [
    [
        "................",
        "......####......",
        ".....######.....",
        "....########....",
        "...##########...",
        "..###..##..###..",
        "..###..##..###..",
        "..############..",
        ".##############.",
        ".####......####.",
        ".#####.##.#####.",
        "..############..",
        "..###.####.###..",
        "...##..##..##...",
        "....#......#....",
        "................",
    ],
    [
        "................",
        "...##########...",
        "..############..",
        "..##..####..##..",
        "..##..####..##..",
        "..############..",
        "...###....###...",
        ".##############.",
        "####.######.####",
        "####.##..##.####",
        "####.######.####",
        ".###.######.###.",
        ".....######.....",
        "....###..###....",
        "...####..####...",
        "................",
    ],
    [
        "................",
        ".#............#.",
        ".###........###.",
        ".#####....#####.",
        "..#####..#####..",
        "..############..",
        "...###.##.###...",
        "....########....",
        "....###..###....",
        "...###.##.###...",
        "..############..",
        "..#####..#####..",
        ".#####....#####.",
        ".###........###.",
        ".#............#.",
        "................",
    ],
    [
        ".........##.....",
        ".....###.###....",
        "....#########...",
        "...###....####..",
        "...##..##..###..",
        "...###....###...",
        "....########....",
        "......####......",
        "....########....",
        "...###....###...",
        "..###......###..",
        ".###...##...###.",
        ".###..####..###.",
        "..############..",
        "...##########...",
        "................",
    ],
    [
        "....##....##....",
        "....###..###....",
        ".....######.....",
        "....########....",
        "...##..##..##...",
        "...##..##..##...",
        "...##########...",
        "....########....",
        ".....######.....",
        "...##########...",
        "..###.####.###..",
        ".###..####..###.",
        "...#..####..#...",
        ".....##..##.....",
        "....##....##....",
        "................",
    ],
    [
        ".......##.......",
        "......####......",
        ".....######.....",
        "....########....",
        "....##....##....",
        "....########....",
        ".....######.....",
        "...##########...",
        "..###.####.###..",
        ".###..####..###.",
        ".###..####..###.",
        "..#..######..#..",
        "....###..###....",
        "....###..###....",
        "...####..####...",
        "................",
    ],
    [
        ".##....##....##.",
        "..##..####..##..",
        "...##########...",
        "....########....",
        "...##########...",
        "..###..##..###..",
        "..###..##..###..",
        "...##########...",
        "....########....",
        "...##########...",
        "..############..",
        ".###..####..###.",
        "####.######.####",
        "##..########..##",
        "..############..",
        "................",
    ],
    [
        "##.....##.....##",
        ".##...####...##.",
        "..############..",
        "...##########...",
        "..###..##..###..",
        ".####..##..####.",
        ".##############.",
        "..############..",
        "...###....###...",
        "..############..",
        ".##############.",
        "####..####..####",
        "###..######..###",
        ".##.########.##.",
        "....########....",
        "...##########...",
    ],
]


def emit(name, data):
    return (
        name
        + ":\n"
        + "\n".join(
            "    .byte " + ",".join(f"${b:02X}" for b in data[i : i + 24])
            for i in range(0, len(data), 24)
        )
        + "\n"
    )


def quads(pixels):
    h, w = len(pixels), len(pixels[0])
    assert h % 2 == w % 2 == 0
    return [
        0x80
        + sum(
            bool(pixels[y + dy][x + dx]) << (dy * 2 + dx)
            for dy in range(2)
            for dx in range(2)
        )
        for y in range(0, h, 2)
        for x in range(0, w, 2)
    ]


def bank():
    data = []
    for code in range(16):
        data += [
            (
                (0xF0 if code & (1 << ((y // 4) * 2)) else 0)
                | (0x0F if code & (2 << ((y // 4) * 2)) else 0)
            )
            for y in range(8)
        ]
    icons = [
        [1, 3, 6, 12, 152, 112, 56, 16],
        [126, 66, 90, 90, 126, 60, 24, 0],
        [12, 24, 56, 126, 28, 24, 48, 0],
        [24, 36, 66, 129, 153, 153, 126, 0],
        [0, 102, 255, 255, 126, 60, 24, 0],
        [24, 60, 126, 219, 219, 126, 60, 24],
        [0, 0, 0, 255, 0, 255, 0, 0],
        [129] * 8,
        [255, 129, 165, 153, 153, 165, 129, 255],
        [0, 24, 60, 126, 255, 0, 0, 0],
        [0, 255, 129, 129, 129, 129, 255, 0],
        [255] * 8,
        [0, 0, 0, 0, 0, 0, 0, 0],
        [24, 60, 126, 255, 126, 60, 24, 0],
        [129, 66, 36, 24, 24, 36, 66, 129],
        [0, 255, 0, 255, 0, 255, 0, 255],
    ]
    return data + [v for glyph in icons for v in glyph]


def title():
    pixels = [[0] * 64 for _ in range(48)]
    # Broken engraved card frame and radiating diamond seals.
    for y in range(5, 34):
        for x in (5, 6, 57, 58):
            pixels[y][x] = 1
    for x in range(7, 57):
        if x % 6 < 4:
            pixels[5][x] = pixels[33][x] = 1
    for cy in (10, 28):
        for dy in range(-4, 5):
            pixels[cy + dy][8 + abs(dy)] = 1
            pixels[cy + dy][55 - abs(dy)] = 1
    for row, word in ((10, "SIGIL"), (22, "DECK")):
        x0 = (64 - (len(word) * 6 - 1)) // 2
        for i, ch in enumerate(word):
            for y, line in enumerate(FONT[ch]):
                for x, b in enumerate(line):
                    if b == "1":
                        pixels[row + y][x0 + i * 6 + x] = 1
    # Central linked sigils.
    for x in range(20, 45):
        if x % 4 == 0:
            pixels[19][x] = 1
    return quads(pixels)


def text_table(name, rows):
    text = name + ":\n"
    for i, (row, col, value) in enumerate(rows):
        assert col + len(value) <= 32, (name, value)
        text += f"    .word FRAMEBUFFER + {row*32+col}, {name}_{i}\n"
    text += "    .word 0\n"
    for i, (_, _, value) in enumerate(rows):
        text += emit(f"{name}_{i}", [*value.encode(), 0])
    return text


def generate(output):
    pcg = bank()
    screen = title()
    text = emit("TITLE_PCG", pcg) + emit("TITLE_SCREEN", screen) + emit("GAME_PCG", pcg)
    for i, lines in enumerate(MONSTERS):
        assert len(lines) == 16 and all(len(row) == 16 for row in lines)
        text += emit(f"MONSTER_{i}", quads([[c == "#" for c in r] for r in lines]))
    text += (
        "MONSTER_TABLE:\n    .word " + ",".join(f"MONSTER_{i}" for i in range(8)) + "\n"
    )
    notes = [
        round(894886.25 / (2 * (130.81278265 * 2 ** (n / 12)))) - 2 for n in range(48)
    ]
    text += "SOUND_NOTES:\n    .word " + ",".join(map(str, notes)) + "\n"
    effects = {
        "SFX_MENU": [1, 2, 25, 2, 32, 2],
        "SFX_SHOT": [3, 3, 40, 1, 22, 2, 10, 2],
        "SFX_SHIELD": [2, 3, 12, 2, 19, 2, 24, 3],
        "SFX_HEAL": [3, 3, 25, 3, 29, 3, 37, 5],
        "SFX_POISON": [3, 3, 35, 2, 34, 2, 18, 5],
        "SFX_HIT": [4, 3, 18, 2, 9, 3, 4, 5],
        "SFX_DEATH": [5, 5, 25, 5, 22, 5, 18, 5, 13, 8, 1, 10],
        "SFX_CLEAR": [4, 6, 25, 4, 29, 4, 32, 4, 37, 8, 41, 4, 44, 12],
        "SFX_EMPTY": [2, 2, 6, 3, 0, 1],
    }
    for name, data in effects.items():
        text += emit(name, data)
    scores = json.loads((ROOT / "music.json").read_text())
    for name, score in scores.items():
        assert len(score["bars"]) == 32
        events = []
        for bar in score["bars"]:
            assert sum(units for _, units in bar) == 8
            for pitch, units in bar:
                duration = units * score["ticks_per_eighth"]
                assert 0 <= pitch <= 48 and 1 <= duration <= 255
                events.extend((pitch, duration))
        text += emit(name, [*events, 255])
    cards = json.loads((ROOT / "cards.json").read_text())
    enemies = json.loads((ROOT / "enemies.json").read_text())
    assert len(cards) == 24 and len(enemies) == 8
    text += emit(
        "CARD_STATS",
        [
            card[k]
            for card in cards
            for k in ("cost", "attack", "block", "special", "value", "exhaust")
        ],
    )
    text += emit(
        "ENEMY_STATS",
        [enemy[k] for enemy in enemies for k in ("hp", "attack", "guard")],
    )
    text += emit("BATTLE_ORDER", [0, 1, 2, 3, 6, 4, 5, 2, 3, 7])
    text += emit("INITIAL_DECK", [0, 0, 0, 0, 1, 1, 1, 3])
    for label, items, key in [
        ("CARD_NAMES", cards, "name"),
        ("CARD_DESCRIPTIONS", cards, "description"),
        ("ENEMY_NAMES", enemies, "name"),
    ]:
        text += (
            label
            + ":\n    .word "
            + ",".join(f"{label}_{i}" for i in range(len(items)))
            + "\n"
        )
        for i, item in enumerate(items):
            text += emit(f"{label}_{i}", [*item[key].encode(), 0])
    tables = {
        "TITLE_TEXT": [
            (1, 7, "A RITUAL IN YOUR HAND"),
            (18, 2, "BUILD A DECK. BREAK THE VOID."),
            (20, 7, "RETURN / PAD : BEGIN"),
            (22, 8, "SPACE : FIELD GUIDE"),
        ],
        "HUD_TEXT": [
            (0, 0, "HP"),
            (0, 10, "SH"),
            (0, 21, "EN"),
            (1, 0, "F"),
            (1, 7, "DRAW"),
            (1, 17, "USED"),
            (1, 26, "X"),
            (3, 1, "ENEMY HP"),
            (5, 1, "SHIELD"),
            (7, 1, "POISON"),
            (9, 1, "WEAK"),
            (3, 22, "STR"),
            (5, 22, "VUL"),
            (7, 22, "ECHO"),
            (9, 22, "THORN"),
            (19, 11, "END TURN"),
            (22, 0, "A/D PICK  RETURN PLAY"),
            (23, 0, "SPACE END  W DECK  CTRL+C EXIT"),
        ],
        "HELP_TEXT": [
            (1, 10, "SIGIL DECK"),
            (3, 1, "TEN BATTLES. BUILD YOUR DECK."),
            (5, 1, "LEFT/RIGHT : SELECT A CARD"),
            (6, 1, "BUTTON : PLAY / CONFIRM"),
            (7, 1, "SPACE : SELECT END TURN"),
            (8, 1, "UP : VIEW YOUR DECK"),
            (10, 1, "ENERGY RETURNS TO 3 EACH TURN."),
            (11, 1, "UNUSED CARDS ARE DISCARDED."),
            (12, 1, "DRAW PILE EMPTY? RECYCLE USED."),
            (13, 1, "EXHAUSTED CARDS STAY OUT."),
            (15, 1, "SHIELD EXPIRES NEXT TURN."),
            (16, 1, "POISON BYPASSES ENEMY SHIELD."),
            (17, 1, "VULNERABLE: +50% ATTACK HIT."),
            (18, 1, "WEAK: ENEMY ATTACK -3."),
            (20, 1, "WIN: PICK A CARD OR REST."),
            (22, 6, "ANY INPUT: TITLE"),
        ],
        "REWARD_TEXT": [
            (3, 7, "A NEW SIGIL AWAITS"),
            (5, 4, "CHOOSE ONE CARD OR REST"),
            (18, 6, "REST: HEAL 10 HP"),
            (20, 2, "EVERY VICTORY ALSO HEALS 4 HP"),
            (22, 1, "LEFT/RIGHT PICK  BUTTON TAKE"),
        ],
        "DEATH_TEXT": [
            (5, 8, "THE RITUAL FAILED"),
            (8, 6, "YOUR SIGILS FALL SILENT"),
            (13, 6, "BUTTON: BEGIN AGAIN"),
            (16, 8, "SPACE: TITLE"),
        ],
        "WIN_TEXT": [
            (4, 6, "THE VOID IS SEALED"),
            (7, 4, "TEN BATTLES. ONE TRUE DECK."),
            (11, 6, "CARDS PLAYED"),
            (14, 6, "FINAL HP"),
            (19, 6, "BUTTON: TITLE"),
        ],
        "DECK_TEXT": [
            (1, 10, "YOUR DECK"),
            (3, 1, "CARDS RETURN EACH BATTLE."),
            (20, 2, "EXHAUST LASTS ONE BATTLE."),
            (22, 5, "ANY INPUT: RETURN"),
        ],
    }
    for name, rows in tables.items():
        text += text_table(name, rows)
    for label, value in [
        ("HIT_TEXT", "NEXT: ATTACK"),
        ("GUARD_TEXT", "NEXT: SHIELD"),
        ("EMPTY_TEXT", "EMPTY SLOT"),
        ("END_TEXT", "DISCARD HAND. ENEMY ACTS."),
        ("COST_TEXT", "EN"),
        ("ATTACK_TEXT", "ATK"),
        ("BLOCK_TEXT", "SH"),
        ("MAGIC_TEXT", "SIG"),
        ("REWARD_DESC", "TAKE THIS CARD INTO YOUR DECK"),
    ]:
        text += emit(label, [*value.encode(), 0])
    (output / "assets.inc").write_text(text)
    (output / "levels.inc").write_text("; Card and encounter data are in assets.inc.\n")
    (output / "art.json").write_text(
        json.dumps(
            {"title_pcg": pcg, "title_screen": screen, "game_pcg": pcg}, indent=2
        )
        + "\n"
    )
