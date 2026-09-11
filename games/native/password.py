"""Compact, checked progress codes for forty-stage games (not authentication).

Two-bit ratings; omit leading pairs of three stars and trailing uncleared pairs.
The game-specific CRC initial value binds codes to a particular campaign.
"""

ALPHABET = "ACDEFGHJKMNPQRTW"
TAGS = {
    "frost-steps": 0x41,
    "magnet-vault": 0x62,
    "glyph-shift": 0x83,
    "gravity-well": 0xA4,
}
KEYS = [
    (1, 0),
    (0, 4),
    (1, 2),
    (2, 2),
    (1, 3),
    (1, 4),
    (6, 0),
    (6, 1),
    (6, 2),
    (7, 3),
    (7, 2),
    (5, 4),
    (2, 0),
    (2, 3),
    (2, 4),
    (2, 1),
]


def crc(values, tag):
    result = tag
    for value in values:
        result ^= value << 4
        for _ in range(4):
            result = ((result << 1) ^ (7 if result & 128 else 0)) & 255
    return result


def encode(level, ratings, tag):
    assert 0 <= level < 40 and len(ratings) == 40 and all(0 <= v <= 3 for v in ratings)
    pairs = [ratings[i] * 4 + ratings[i + 1] for i in range(0, 40, 2)]
    prefix = 0
    while prefix < 20 and pairs[prefix] == 15:
        prefix += 1
    end = 20
    while end > prefix and pairs[end - 1] == 0:
        end -= 1
    header = level | (128 + (64 if prefix >= 16 else 0) if prefix else 0)
    values = [header >> 4, header & 15]
    if prefix:
        values.append(prefix & 15)
    values += pairs[prefix:end]
    check = crc(values, tag)
    values += [check >> 4, check & 15]
    assert 4 <= len(values) <= 24
    return "".join(ALPHABET[i] for i in values)


def decode(code, tag):
    code = code.replace(" ", "").upper()
    if not 4 <= len(code) <= 24 or any(c not in ALPHABET for c in code):
        raise ValueError("Invalid password")
    values = [ALPHABET.index(c) for c in code]
    if crc(values, tag):
        raise ValueError("Invalid password")
    header = values[0] * 16 + values[1]
    level = header & 63
    prefix, offset = 0, 2
    if header & 128:
        if len(values) < 5:
            raise ValueError("Invalid password")
        prefix = (16 if header & 64 else 0) + values[2]
        offset = 3
        if not 1 <= prefix <= 20:
            raise ValueError("Invalid password")
    elif header & 64:
        raise ValueError("Invalid password")
    body = values[offset:-2]
    if level >= 40 or prefix + len(body) > 20:
        raise ValueError("Invalid password")
    ratings = [3] * (prefix * 2)
    for value in body:
        ratings += [value >> 2, value & 3]
    ratings += [0] * (40 - len(ratings))
    return level, bytes(ratings)


def input_hook(source):
    """Use literal keys inside password entry, retaining the platform edge filter."""
    anchor = "    BEQ EXIT_GAME\n    CLRB\n"
    assert source.count(anchor) == 1
    source = source.replace(
        anchor,
        "    BEQ EXIT_GAME\n    LDAA MODE\n    CMPA #7\n    BEQ P_POLL_KEYS\n    CLRB\n",
    )
    keys = """\nP_POLL_KEYS:
    CLRB
    LDAA KEYS + 8
    BITA #8
    BNE INPUT_CONFIRM
    BITA #16
    BNE INPUT_BACK
    LDAA KEYS
    BITA #8
    BNE INPUT_WAIT
"""
    for i, (row, bit) in enumerate(KEYS):
        keys += f"    LDAA KEYS + {row}\n    BITA #{1 << bit}\n    BEQ P_KEY_{i}\n    LDAB #{16 + i}\n    JMP INPUT_EDGE\nP_KEY_{i}:\n"
    keys += """    LDAA $CC02
    CMPA #$FF
    BEQ INPUT_EDGE
    BITA #16
    BEQ P_PAD_DIR
    LDAB #9
    JMP INPUT_EDGE
P_PAD_DIR:
    ANDA #15
    CMPA #4
    BEQ INPUT_NORTH
    CMPA #8
    BEQ INPUT_SOUTH
    CMPA #2
    BEQ INPUT_WEST
    CMPA #1
    BEQ INPUT_EAST
    JMP INPUT_EDGE
"""
    return source + keys
