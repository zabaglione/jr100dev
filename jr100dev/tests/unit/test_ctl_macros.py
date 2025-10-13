from jr100dev.asm.encoder import Assembler


def assemble(source: str):
    asm = Assembler(source, filename="ctl_demo.asm")
    return asm.assemble()


def test_for_macro_compiles_and_loops():
    src = """
        .org $0300
        JMP START
        .include "macro.inc"
        .include "ctl.inc"

        .data
VAR8 COUNT, 0
VAR8 LAST_KEY, 0

        .code
START:
        LDX #STD_VRAM_BASE
FOR_BEGIN LOOP_TOP, LOOP_END, COUNT, 0, 3
        LDAA COUNT
        ADDA #$30
        JSR __STD_TO_VRAM
        STAA ,X
        INX
FOR_END LOOP_TOP, LOOP_END, COUNT
        SCAN_KEY
        STAA LAST_KEY
        IF_EQ AFTER_IF, LAST_KEY, $01
            BEEP
        IF_END AFTER_IF
        RTS
    """
    result = assemble(src)
    assert len(result.machine_code) > 0
    # BRA opcode (0x20) and INC opcode (0x7C) should appear in the loop expansion
    assert 0x20 in result.machine_code
    assert 0x7C in result.machine_code


def test_while_macro_compiles():
    src = """
        .org $0300
        JMP MAIN
        .include "macro.inc"
        .include "ctl.inc"

        .data
VAR8 FLAG, 0

        .code
MAIN:
        WHILE_BEGIN LOOP_TOP
            WHILE_IF_ZERO LOOP_END, FLAG
            DEC8 FLAG
        WHILE_END LOOP_TOP, LOOP_END
        RTS
    """
    result = assemble(src)
    assert len(result.machine_code) > 0
    assert 0x20 in result.machine_code


def test_add16_sub16_macros():
    src = """
        .org $0300
        JMP MAIN
        .include "macro.inc"
        .include "ctl.inc"

        .data
VAR16 PTR, $C100
VAR16 STEP, $0004

        .code
MAIN:
        ADD16 PTR, PTR+1, STEP, STEP+1
        SUB16 PTR, PTR+1, #$04, #$00
        RTS
    """
    result = assemble(src)
    code = result.machine_code
    assert 0x0C in code  # CLC present
    assert 0x0D in code  # SEC present
