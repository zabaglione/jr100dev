"""Original PCG art, title typography, sound and authored room data."""

import functools
import json
import math
import operator
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from art import extended_theme

FONT = {
    "C": ["11111", "10000", "10000", "10000", "10000", "10000", "11111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "N": ["10001", "11001", "11001", "10101", "10011", "10011", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
}


def emit(name, values):
    return (
        name
        + ":\n"
        + "\n".join(
            "    .byte " + ",".join(f"${v:02X}" for v in values[n : n + 24])
            for n in range(0, len(values), 24)
        )
        + "\n"
    )


def title():
    # Four quadrant bits form 16 exact PCG characters. All logo pixels are 4x4.
    canvas = [[0] * 64 for _ in range(48)]

    def dot(x, y):
        if 0 <= x < 64 and 0 <= y < 48:
            canvas[y][x] = 1

    for angle in range(360):
        if 38 < angle % 90 < 63:
            continue
        a = math.radians(angle)
        dot(round(32 + 21 * math.cos(a)), round(23 + 21 * math.sin(a)))
    for row, word in ((10, "CHRONO"), (23, "BREACH")):
        for y in range(row - 2, row + 10):
            for x in range(5, 60):
                canvas[y][x] = 0
        for n, letter in enumerate(word):
            for y, bits in enumerate(FONT[letter]):
                for x, bit in enumerate(bits):
                    if bit == "1":
                        dot(15 + n * 6 + x, row + y)
    for y in range(18, 22):
        for x in range(14, 51):
            if (x + y) % 9 == 0:
                dot(x, y)
    screen = []
    for y in range(24):
        for x in range(32):
            code = sum(
                canvas[y * 2 + dy][x * 2 + dx] << (dy * 2 + dx)
                for dy in range(2)
                for dx in range(2)
            )
            screen.append(0x80 + code)
    bank = []
    for code in range(32):
        bank += [
            (
                (0xF0 if code & (1 << ((y // 4) * 2)) else 0)
                | (0x0F if code & (2 << ((y // 4) * 2)) else 0)
            )
            for y in range(8)
        ]
    # Four clock hands share the remaining sixteen title characters.
    for direction in range(4):
        pixels = [[False] * 16 for _ in range(16)]
        for a in range(360):
            angle = math.radians(a)
            x, y = round(7.5 + 7 * math.cos(angle)), round(7.5 + 7 * math.sin(angle))
            pixels[y][x] = True
        for n in range(6):
            dx, dy = ((0, -1), (1, 0), (0, 1), (-1, 0))[direction]
            pixels[8 + dy * n][8 + dx * n] = True
        glyphs = sprite(["".join("#" if v else "." for v in row) for row in pixels])
        bank[128 + direction * 32 : 160 + direction * 32] = glyphs
    # Keep menu lettering clear of the large dial's lower arc.
    for y in range(17, 24):
        for x in range(32):
            screen[y * 32 + x] = 0x80
    return bank, screen


def sprite(lines):
    assert len(lines) == 16 and all(len(row) == 16 for row in lines)
    pixels = [[c != "." for c in row] for row in lines]
    return [
        sum(pixels[ty * 8 + y][tx * 8 + x] << (7 - x) for x in range(8))
        for ty, tx in ((0, 0), (0, 1), (1, 0), (1, 1))
        for y in range(8)
    ]


SPRITES = [
    [
        "................",
        "......####......",
        ".....######.....",
        ".....##..##.....",
        ".....######.....",
        "......####......",
        "....########....",
        "...##########...",
        "..###.####.###..",
        "..##..####..##..",
        "......####......",
        ".....######.....",
        ".....##..##.....",
        "....###..###....",
        "....##....##....",
        "................",
    ],
    [
        "................",
        "..##........##..",
        "..###..##..###..",
        "...##########...",
        "....########....",
        "..############..",
        ".####......####.",
        ".###..####..###.",
        ".###..####..###.",
        ".####......####.",
        "..############..",
        "....########....",
        "...##########...",
        "..###......###..",
        "..##........##..",
        "................",
    ],
    [
        "################",
        "#......##......#",
        "#.####.##.####.#",
        "#.####.##.####.#",
        "#......##......#",
        "################",
        "################",
        "#..##......##..#",
        "#..##.####.##..#",
        "#..##.####.##..#",
        "#..##......##..#",
        "################",
        "################",
        "#......##......#",
        "#.####.##.####.#",
        "################",
    ],
    [
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        ".......#........",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    [
        "################",
        "##............##",
        "#..##########..#",
        "#..##......##..#",
        "#..##......##..#",
        "#..##..##..##..#",
        "#..##.####.##..#",
        "#..##########..#",
        "#..##########..#",
        "#..##.####.##..#",
        "#..##..##..##..#",
        "#..##......##..#",
        "#..##......##..#",
        "#..##########..#",
        "##............##",
        "################",
    ],
    [
        "................",
        "................",
        ".......##.......",
        ".......##.......",
        "......####......",
        ".....######.....",
        "....########....",
        "..############..",
        "..############..",
        "....########....",
        ".....######.....",
        "......####......",
        ".......##.......",
        ".......##.......",
        "................",
        "................",
    ],
    [
        "#..............#",
        "................",
        "................",
        "................",
        "................",
        ".......##.......",
        "......####......",
        ".....##..##.....",
        ".....##..##.....",
        "......####......",
        ".......##.......",
        "................",
        "................",
        "................",
        "................",
        "#..............#",
    ],
    [
        "################",
        "#..............#",
        "#.############.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.#..........#.#",
        "#.############.#",
        "#..............#",
        "################",
    ],
]


def generate(output):
    bank, screen = title()
    game_bank = functools.reduce(
        operator.iadd, (sprite(image) for image in SPRITES), []
    )
    game_bank[224:] = (
        [0x88] * 8
        + [0, 0, 0, 0xFF, 0, 0xFF, 0, 0]
        + [0xFF] * 8
        + [0xFF, 0x81, 0x81, 0x81, 0x81, 0x81, 0x81, 0xFF]
    )
    assert len(game_bank) == 256
    text = emit("TITLE_PCG", bank) + emit("TITLE_SCREEN", screen)
    text += emit("GAME_PCG", game_bank)
    walking = SPRITES[0].copy()
    walking[11:] = [
        ".....######.....",
        "....###.###.....",
        "...###..##......",
        "...##....###....",
        "................",
    ]
    shattered = [list(row) for row in SPRITES[0]]
    for y in range(16):
        for x in range(16):
            if (x + y) % 4 < 2:
                shattered[y][x] = "."
    text += emit("PLAYER_WALK", sprite(walking))
    text += emit("PLAYER_SHATTER", sprite(["".join(row) for row in shattered]))
    notes = [
        round(894886.25 / (2 * (130.81278265 * 2 ** (n / 12)))) - 2 for n in range(48)
    ]
    text += "SOUND_NOTES:\n    .word " + ",".join(f"${n:04X}" for n in notes) + "\n"
    effects = {
        "SFX_MOVE": [1, 2, 18, 1, 0, 1],
        "SFX_MENU": [1, 2, 29, 2, 36, 2],
        "SFX_SHOT": [3, 4, 46, 1, 30, 1, 16, 2, 5, 2],
        "SFX_KILL": [4, 4, 20, 2, 32, 2, 39, 3, 44, 4],
        "SFX_DEATH": [5, 5, 28, 4, 24, 5, 18, 6, 11, 8, 3, 12],
        "SFX_CLEAR": [4, 6, 25, 4, 29, 4, 32, 4, 37, 6, 0, 3, 44, 10],
        "SFX_EMPTY": [2, 2, 5, 2, 0, 2],
    }
    for name, values in effects.items():
        text += emit(name, values)
    # Original 32-bar theme with contrasting register and rests.
    text += emit("MUSIC_TITLE", extended_theme(6, (0, 2, 5, 7, 12, 14, 17, 19)))
    (output / "assets.inc").write_text(text)
    rooms = json.loads((Path(__file__).parent / "levels.json").read_text())
    data = (
        "LEVEL_TABLE:\n    .word "
        + ",".join(f"ROOM_{i}" for i in range(len(rooms)))
        + "\n"
    )
    for i, room in enumerate(rooms):
        grid = room["map"]
        assert len(grid) == 10 and all(len(row) == 12 for row in grid), room["name"]
        player = [
            (x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "@"
        ]
        exits = [
            (x, y) for y, row in enumerate(grid) for x, c in enumerate(row) if c == "X"
        ]
        enemies = [
            (x, y, "^v<>".index(c) + 1)
            for y, row in enumerate(grid)
            for x, c in enumerate(row)
            if c in "^v<>"
        ]
        assert len(player) == len(exits) == 1 and 1 <= len(enemies) <= 6
        values = [*player[0], *exits[0], len(enemies), room["ammo"], room["par"]]
        values += [v for enemy in enemies for v in enemy]
        tiles = [1 if c == "#" else 2 if c == "X" else 0 for row in grid for c in row]
        rle = []
        for tile in tiles:
            if rle and rle[-1] == tile and rle[-2] < 255:
                rle[-2] += 1
            else:
                rle.extend((1, tile))
        data += emit(f"ROOM_{i}", values + rle)
        data += emit(f"ROOM_NAME_{i}", list(room["name"].encode()) + [0])
    data += (
        "ROOM_NAMES:\n    .word "
        + ",".join(f"ROOM_NAME_{i}" for i in range(len(rooms)))
        + "\n"
    )
    (output / "levels.inc").write_text(data)
    (output / "art.json").write_text(
        json.dumps(
            {"title_pcg": bank, "title_screen": screen, "game_pcg": game_bank}, indent=2
        )
        + "\n"
    )
