"""Large station signs: each owns four PCG characters and two lighting poses."""

from art import FONT_ROWS, emit
from relief import Pixels


def station(char, lit):
    sign = Pixels(contact_shadow=False)
    sign.rect(0, 0, 16, 16, fill=lit)
    rows = bytes.fromhex(FONT_ROWS[char])
    for y, row in enumerate(rows):
        for x in range(5):
            if row & (1 << (4 - x)):
                sign.rect(3 + x * 2, 1 + y * 2, 2, 2, fill=True, value=not lit)
    return sign.pack()


def prepare(bank):
    frames = ""
    for tile, char in enumerate("ABC", 3):
        off, on = station(char, False), station(char, True)
        bank[tile * 32 : tile * 32 + 32] = off
        frames += emit(f"FACE_{tile}_FRAMES", off + on)
    return frames
