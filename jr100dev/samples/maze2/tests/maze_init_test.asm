        .org $0300

        .include "../src/common.inc"

MAZE_MAP:        .equ $0600
MAZE_MAP_END:    .equ (MAZE_MAP + MAZE_CHAR_W * MAZE_CHAR_H)
ROW_INDEX:       .equ $0500
COL_INDEX:       .equ $0501
CHAR_OFFSET_LO:  .equ $0502
CHAR_OFFSET_HI:  .equ $0503
TEMP_SHIFT:      .equ $0504
TEMP_PTR:        .equ $0505

        JSR TEST_MAZE_INIT
STOP:
        BRA STOP

TEST_MAZE_INIT:
        LDX #MAZE_MAP
FILL_WALLS:
        LDAA #'#'
        STAA 0,X
        INX
        CPX #MAZE_MAP_END
        BNE FILL_WALLS

        LDAA #1
        STAA >ROW_INDEX
ROW_LOOP:
        LDAA >ROW_INDEX
        CMPA #(MAZE_CHAR_H - 1)
        BEQ ROW_DONE
        LDAA #1
        STAA >COL_INDEX
COL_LOOP:
        LDAA >COL_INDEX
        CMPA #(MAZE_CHAR_W - 1)
        BEQ NEXT_ROW
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX >TEMP_PTR
        LDAA #' '
        STAA ,X
        INC >COL_INDEX
        BRA COL_LOOP
NEXT_ROW:
        INC >ROW_INDEX
        BRA ROW_LOOP
ROW_DONE:
        RTS

MAZE_MAP_PTR_FROM_COORD:
        CLRA
        STAA >CHAR_OFFSET_LO
        STAA >CHAR_OFFSET_HI
        LDAA >ROW_INDEX
        BEQ MMPC_ROW_DONE
        STAA >TEMP_SHIFT
MMPC_ROW_LOOP:
        LDAA >CHAR_OFFSET_LO
        ADDA #MAZE_CHAR_W
        STAA >CHAR_OFFSET_LO
        LDAA >CHAR_OFFSET_HI
        ADCA #0
        STAA >CHAR_OFFSET_HI
        DEC >TEMP_SHIFT
        BNE MMPC_ROW_LOOP
MMPC_ROW_DONE:
        LDAA >COL_INDEX
        ADDA >CHAR_OFFSET_LO
        STAA >CHAR_OFFSET_LO
        LDAA #0
        ADCA >CHAR_OFFSET_HI
        STAA >CHAR_OFFSET_HI
        LDAA #((MAZE_MAP >> 8) & $00FF)
        STAA >TEMP_PTR
        LDAA #(MAZE_MAP & $00FF)
        STAA >TEMP_PTR+1
        LDAA >CHAR_OFFSET_LO
        ADDA >TEMP_PTR+1
        STAA >TEMP_PTR+1
        LDAA >CHAR_OFFSET_HI
        ADCA >TEMP_PTR
        STAA >TEMP_PTR
        RTS
