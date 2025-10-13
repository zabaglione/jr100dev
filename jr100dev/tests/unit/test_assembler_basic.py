from jr100dev.asm.encoder import Assembler


def assemble(source: str):
    assembler = Assembler(source, filename="test.asm")
    return assembler.assemble()


def test_simple_program():
    source = """
        .org $8000
        START: LDAA #$41
               STAA $6000
               RTS
    """
    result = assemble(source)
    assert result.origin == 0x8000
    assert result.entry_point == 0x8000
    assert result.machine_code == bytes([0x86, 0x41, 0xB7, 0x60, 0x00, 0x39])
    assert result.symbols["START"] == 0x8000


def test_direct_and_extended_addressing():
    source = """
        .org $8000
        LDAA FWD
        LDAA $80
        LDAA >$80
        LDAA $1234
SMALL:  .equ $0020
        LDAA <SMALL
FWD:    .equ $00FF
        LDAA <FWD
        RTS
    """
    result = assemble(source)
    expected = bytes(
        [
            0x96,
            0xFF,  # LDAA FWD -> direct after forward symbol resolution
            0x96,
            0x80,
            0xB6,
            0x00,
            0x80,
            0xB6,
            0x12,
            0x34,
            0x96,
            0x20,
            0x96,
            0xFF,
            0x39,
        ]
    )
    assert result.machine_code == expected
    assert result.symbols["SMALL"] == 0x0020
    assert result.symbols["FWD"] == 0x00FF
