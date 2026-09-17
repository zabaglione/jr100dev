"""Lossless static screen compression; reserve RAM for effects, not blanks."""

import re

from art import emit


def pack(data):
    """Pairs of run length and value, terminated by zero. All 256 codes work."""
    result = []
    index = 0
    while index < len(data):
        end = index + 1
        while end < len(data) and data[end] == data[index] and end - index < 255:
            end += 1
        result.extend((end - index, data[index]))
        index = end
    return result + [0]


def compress(source):
    names = ("TITLE_SCREEN", "HUD_SCREEN", "HELP_SCREEN")
    for name in names:
        pattern = name + r":\n(?:    \.byte[^\n]*\n)+"
        found = re.search(pattern, source)
        if not found:
            continue
        data = [int(v, 16) for v in re.findall(r"\$([0-9A-F]{2})", found[0])]
        assert len(data) == 768, name
        source = (
            source[: found.start()] + emit(name, pack(data)) + source[found.end() :]
        )
    # Every static-screen copy follows this one explicit ABI.
    copy = (
        "    STX SRC\n    LDX #FRAMEBUFFER\n    STX DST\n"
        "    LDX #768\n    STX COUNT\n    JSR COPY"
    )
    for name in names:
        source = source.replace(
            f"    LDX #{name}\n" + copy, f"    LDX #{name}\n    JSR UNPACK_SCREEN"
        )
    source = source.replace("N_SCREEN:\n" + copy, "N_SCREEN:\n    JSR UNPACK_SCREEN")
    return source
