        .org $0300
        JMP MAIN

        .include "macro.inc"
        .include "ctl.inc"

        .data
VAR8 COUNT, 0

        .code
MAIN:   CLR_VRAM
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        LDX #STD_VRAM_BASE + 32
        PRINT_STR PROMPT

        LDX #STD_VRAM_BASE + 64
FOR_BEGIN LOOP_TOP, LOOP_END, COUNT, 0, 9
        LDAA COUNT
        ADDA #$30
        JSR __STD_TO_VRAM
        STAA ,X
        INX
FOR_END LOOP_TOP, LOOP_END, COUNT

WAIT_KEY:
        SCAN_KEY
        BEQ WAIT_KEY
        CMPA #$01
        BNE RESET
        BEEP
RESET:
        CLR COUNT
        BRA MAIN

TITLE:  .ascii "FOR LOOP DEMO\0"
PROMPT: .ascii "COUNTING 0-9\0"
