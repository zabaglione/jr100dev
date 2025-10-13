        .org $0300
        JMP MAIN

        .include "macro.inc"
        .include "ctl.inc"

        .data
VAR8 LOOP_I, 0
VAR8 LAST_KEY, 0

        .code
MAIN:   CLR_VRAM
        BEEP
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        LDX #STD_VRAM_BASE + 32
        PRINT_STR PROMPT

        ; display digits 0-9 using FOR macro
        LDX #STD_VRAM_BASE + 64
FOR_BEGIN DIGITS_TOP, DIGITS_END, LOOP_I, 0, 9
        LDAA LOOP_I
        ADDA #$30
        JSR __STD_TO_VRAM
        STAA ,X
        INX
FOR_END DIGITS_TOP, DIGITS_END, LOOP_I

        ; main input loop
        LDX #STD_VRAM_BASE + 96
        PRINT_STR LABEL

WHILE_BEGIN WAIT_TOP
        SCAN_KEY
        STAA LAST_KEY
        WHILE_IF_ZERO WAIT_END, LAST_KEY

        LDX #STD_VRAM_BASE + 112
        LDAA LAST_KEY
        JSR __STD_TO_VRAM
        STAA ,X

        IF_EQ NOT_SPACE, LAST_KEY, $01
            BEEP
        IF_END NOT_SPACE

        LDX #STD_VRAM_BASE + 96
        PRINT_STR LABEL
        LDX #STD_VRAM_BASE + 112
        LDAA #' '
        JSR __STD_TO_VRAM
        STAA ,X
WHILE_END WAIT_TOP, WAIT_END

        BRA MAIN

TITLE:  .ascii "JR-100 I/O DEMO\0"
PROMPT: .ascii "PRESS KEY TO SHOW CODE\0"
LABEL:  .ascii "LAST CODE: \0"
