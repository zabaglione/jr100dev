"""Load a nibble-packed 8x8 map followed by its byte-sized stage parameters."""


def loader(source, tail):
    assert 1 <= tail <= 64
    before = "    LDX #128\n    STX COUNT\n    JSR COPY\n"
    assert source.count(before) == 1
    return source.replace(
        before,
        f"""    LDAB #32
N_UNPACK_LEVEL:
    LDX SRC
    LDAA 0,X
    INX
    STX SRC
    STAA N_TMP
    LSRA
    LSRA
    LSRA
    LSRA
    LDX DST
    STAA 0,X
    LDAA N_TMP
    ANDA #15
    STAA 1,X
    INX
    INX
    STX DST
    DECB
    BNE N_UNPACK_LEVEL
    LDX #{tail}
    STX COUNT
    JSR COPY
""",
    )
