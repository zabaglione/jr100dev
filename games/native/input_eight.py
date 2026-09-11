"""Opt-in QWE/AD/ZXC and native diagonal gamepad actions."""


def apply_eight_way(source):
    source = source.replace(
        "    CMPA #4\n    BEQ INPUT_NORTH",
        """    CMPA #6
    BEQ INPUT_NW
    CMPA #5
    BEQ INPUT_NE
    CMPA #10
    BEQ INPUT_SW
    CMPA #9
    BEQ INPUT_SE
    CMPA #4
    BEQ INPUT_NORTH""",
    )
    start = source.index("INPUT_KEYS:\n")
    end = source.index("INPUT_NORTH:\n", start)
    source = source[:start] + """INPUT_KEYS:
    LDAA KEYS + 2
    BITA #1
    BNE INPUT_NW
    BITA #4
    BNE INPUT_NE
    BITA #2
    BNE INPUT_NORTH
    LDAA KEYS
    BITA #4
    BNE INPUT_SW
    BITA #16
    BNE INPUT_SE
    BITA #8
    BNE INPUT_SOUTH
    LDAA KEYS + 1
    BITA #1
    BNE INPUT_WEST
    BITA #4
    BNE INPUT_EAST
    BRA INPUT_EDGE
INPUT_NW:
    LDAB #9
    BRA INPUT_EDGE
INPUT_NE:
    LDAB #10
    BRA INPUT_EDGE
INPUT_SW:
    LDAB #11
    BRA INPUT_EDGE
INPUT_SE:
    LDAB #12
    BRA INPUT_EDGE
""" + source[end:]
    return source
