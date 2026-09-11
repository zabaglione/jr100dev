"""Small original bitmap alphabet and assembler asset helpers."""

FONT_ROWS = {
    "A": "0E11111F111111",
    "B": "1E11111E11111E",
    "C": "0F10101010100F",
    "D": "1E11111111111E",
    "E": "1F10101E10101F",
    "F": "1F10101E101010",
    "G": "0F10101711110F",
    "H": "1111111F111111",
    "I": "1F04040404041F",
    "J": "0702020212120C",
    "K": "11121418141211",
    "L": "1010101010101F",
    "M": "111B1515111111",
    "N": "11191915131311",
    "O": "0E11111111110E",
    "P": "1E11111E101010",
    "Q": "0E11111115120D",
    "R": "1E11111E141211",
    "S": "0F10100E01011E",
    "T": "1F040404040404",
    "U": "1111111111110E",
    "V": "11111111110A04",
    "W": "11111115151B11",
    "X": "11110A040A1111",
    "Y": "11110A04040404",
    "Z": "1F01020408101F",
    "0": "0E11131519110E",
    "1": "040C040404040E",
    "2": "0E11010204081F",
    "3": "1E01010601011E",
    "4": "02060A121F0202",
    "5": "1F10101E01011E",
    "6": "0E10101E11110E",
    "7": "1F010204080808",
    "8": "0E11110E11110E",
    "9": "0E11110F01010E",
    " ": "00000000000000",
}


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
    return [
        0x80
        + sum(
            bool(pixels[y + dy][x + dx]) << (dy * 2 + dx)
            for dy in range(2)
            for dx in range(2)
        )
        for y in range(0, len(pixels), 2)
        for x in range(0, len(pixels[0]), 2)
    ]


def quad_bank():
    return [
        (
            (0xF0 if code & (1 << (y // 4 * 2)) else 0)
            | (0x0F if code & (2 << (y // 4 * 2)) else 0)
        )
        for code in range(16)
        for y in range(8)
    ] + [0] * 128


def word(pixels, text, y, x=None):
    x = (len(pixels[0]) - len(text) * 6 + 1) // 2 if x is None else x
    for i, ch in enumerate(text):
        bits = bytes.fromhex(FONT_ROWS[ch])
        for dy, bits_row in enumerate(bits):
            for dx in range(5):
                if bits_row & (16 >> dx):
                    pixels[y + dy][x + i * 6 + dx] = 1


def text_table(name, rows):
    result = name + ":\n"
    for i, (y, x, value) in enumerate(rows):
        assert x + len(value) <= 32, (name, value)
        result += f"    .word FRAMEBUFFER + {y*32+x}, {name}_{i}\n"
    result += "    .word 0\n"
    for i, (_, _, value) in enumerate(rows):
        result += emit(f"{name}_{i}", [*value.encode(), 0])
    return result


def strings(name, values):
    result = (
        name
        + ":\n    .word "
        + ",".join(f"{name}_{i}" for i in range(len(values)))
        + "\n"
    )
    return result + "".join(
        emit(f"{name}_{i}", [*v.encode(), 0]) for i, v in enumerate(values)
    )


def sound(effects, melody):
    notes = [
        round(894886.25 / (2 * (130.81278265 * 2 ** (n / 12)))) - 2 for n in range(48)
    ]
    return (
        "SOUND_NOTES:\n    .word "
        + ",".join(map(str, notes))
        + "\n"
        + "".join(emit(k, v) for k, v in effects.items())
        + emit("MUSIC_TITLE", melody)
    )


def extended_theme(root, scale=(0, 3, 7, 10, 12, 15, 19, 22)):
    """32 original bars with contrasting register, rhythm and silence."""
    phrases = [
        [(0, 3), (2, 1), (4, 2), (-1, 2)],
        [(3, 2), (2, 2), (1, 2), (-1, 2)],
        [(1, 3), (3, 1), (5, 2), (-1, 2)],
        [(4, 2), (3, 2), (1, 2), (-1, 2)],
        [(0, 2), (1, 2), (3, 2), (4, 2)],
        [(5, 3), (4, 1), (2, 2), (-1, 2)],
        [(3, 2), (2, 2), (1, 2), (0, 2)],
        [(2, 4), (-1, 4)],
    ]
    result = []
    for section in range(4):
        for bar in range(8):
            for degree, units in phrases[(bar + section * 2) % 8]:
                if degree < 0:
                    pitch = 0
                else:
                    shift = 1 if section in (1, 3) else 0
                    pitch = root + scale[min(degree + shift, 7)]
                    if section == 2:
                        pitch = max(1, pitch - 12)
                result.extend((pitch, units * 12))
    return [*result, 255]
