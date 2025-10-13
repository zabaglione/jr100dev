        .org $0300
        JMP START

        .include "macro.inc"
        .include "ctl.inc"
        .include "common.inc"
        .include "maze_symbols.inc"

MAZE_GENERATE_ADDR .equ $0700

START:
        JSR MAZE_GENERATE_ADDR
        RTS
