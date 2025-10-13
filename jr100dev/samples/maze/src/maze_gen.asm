        .org $0700

        .include "macro.inc"
        .include "ctl.inc"
        .include "common.inc"
        .include "maze_helpers.inc"
        .include "maze_symbols.inc"


; --- Helper routines ---------------------------------------------------

STACK_PUSH:
        LDD STACK_POS
        STD STACK_TOP
        LDAA CUR_CELL_POS+1
        STAA STACK_Y, D
        LDAA CUR_CELL_POS
        STAA STACK_X, D
        INCB
        STAB STACK_POS
        LDAA STACK_TOP
        INCA
        STAA STACK_TOP
        RTS

STACK_POP:
        LDAA STACK_TOP
        BEQ STACK_EMPTY
        DECA
        STAA STACK_TOP
        LDX STACK_Y
        LDAA STACK_TOP
        STAA STACK_POS
        RTS
STACK_EMPTY:
        RTS

MAZE_INIT:
        ; Fill entire map with '#'
        LDX #0
MAZE_FILL_LOOP:
        CPX #MAZE_CHAR_W * MAZE_CHAR_H
        BEQ MAZE_FILL_DONE
        LDAA #'#'
        STAA MAZE_MAP,X
        INX
        BRA MAZE_FILL_LOOP
MAZE_FILL_DONE:
        ; Clear interior cells
        LDAA #1
        STAA ROW_INDEX
ROW_LOOP:
        LDAA ROW_INDEX
        CMPA #MAZE_CHAR_H - 1
        BHS ROW_END
        LDAB #MAZE_CHAR_W
        MUL
        ADDD #MAZE_MAP + 1
        STD TEMP_PTR
        LDX TEMP_PTR
        LDAA #1
        STAA COL_INDEX
COL_LOOP:
        LDAA COL_INDEX
        CMPA #MAZE_CHAR_W - 1
        BHS NEXT_ROW
        LDAA #' '
        STAA 0,X
        INX
        INC COL_INDEX
        BRA COL_LOOP
NEXT_ROW:
        LDAA ROW_INDEX
        INCA
        STAA ROW_INDEX
        BRA ROW_LOOP
ROW_END:
        ; ensure start and goal cells open
        LDAA #PLAYER_START_Y
        LDAB #MAZE_CHAR_W
        MUL
        ADDD #MAZE_MAP + PLAYER_START_X
        STD TEMP_PTR
        LDX TEMP_PTR
        LDAA #' '
        STAA 0,X

        LDAA #GOAL_Y
        LDAB #MAZE_CHAR_W
        MUL
        ADDD #MAZE_MAP + GOAL_X
        STD TEMP_PTR
        LDX TEMP_PTR
        LDAA #' '
        STAA 0,X

        RTS

MAZE_GENERATE:
        JSR MAZE_INIT
        RTS
