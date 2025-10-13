        .org $0300
        JMP START

        .include "macro.inc"
        .include "ctl.inc"

DRAW_MESSAGE EQU $0400

        .data
VAR8 LOOP_I, 0

        .code
START:
        CLR_VRAM
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        JSR DRAW_MESSAGE

        LDX #STD_VRAM_BASE + 64
FOR_BEGIN LOOP_TOP, LOOP_END, LOOP_I, 0, 5
        LDAA LOOP_I
        ADDA #$30
        JSR __STD_TO_VRAM
        STAA ,X
        INX
FOR_END LOOP_TOP, LOOP_END, LOOP_I

        RTS

TITLE:  .ascii "MULTI FILE DEMO\0"
