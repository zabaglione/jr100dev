.org $0300

.include "../src/common.inc"
.include "../src/maze_helpers.inc"

RESULT_CUR_CHAR:        .equ $3800
RESULT_CUR_REF:         .equ $3801
RESULT_PASS_E_CUR:      .equ $3802
RESULT_PASS_E_WALL:     .equ $3803
RESULT_PASS_E_NEXT:     .equ $3804
RESULT_PASS_E_REF:      .equ $3805
RESULT_PASS_N_CUR:      .equ $3806
RESULT_PASS_N_WALL:     .equ $3807
RESULT_PASS_N_NEXT:     .equ $3808
RESULT_PASS_N_REF:      .equ $3809

TMP_BASE:               .equ $0700
TMP_DIR_COUNT:          .equ TMP_BASE
TMP_DIR_BUF:            .equ (TMP_BASE + 1)
TMP_CHOICE:             .equ (TMP_BASE + 5)
CUR_CELL_POS:           .equ (TMP_BASE + 6)
NEXT_CELL_POS:          .equ (TMP_BASE + 8)
CELL_OFFSET_LO:         .equ (TMP_BASE + 10)
CELL_OFFSET_HI:         .equ (TMP_BASE + 11)
TEMP_PTR:               .equ (TMP_BASE + 12)
TEMP_SHIFT:             .equ (TMP_BASE + 14)
TMP_MASK:               .equ (TMP_BASE + 15)
TMP_LAST_LOAD:          .equ (TMP_BASE + 16)
ROW_INDEX:             .equ (TMP_BASE + 17)
COL_INDEX:             .equ (TMP_BASE + 18)
CHAR_OFFSET_LO:         .equ (TMP_BASE + 19)
CHAR_OFFSET_HI:         .equ (TMP_BASE + 20)
READ_CELL_POS:          .equ (TMP_BASE + 21)

MAZE_MAP:               .equ MAZE_MAP_ADDR
MAZE_MAP_HI:            .equ ((MAZE_MAP >> 8) & $00FF)
MAZE_MAP_LO:            .equ (MAZE_MAP & $00FF)

CASE_CUR_X:             .equ 1
CASE_CUR_Y:             .equ 2
CASE_E_X:               .equ 1
CASE_E_Y:               .equ 1
CASE_N_X:               .equ 2
CASE_N_Y:               .equ 2

START:
        JSR INIT_MAP
        JSR CASE_CUR
        JSR INIT_MAP
        JSR CASE_PASS_E
        JSR INIT_MAP
        JSR CASE_PASS_N
HALT:
        BRA HALT

CASE_CUR:
        LDAA #CASE_CUR_X
        STAA >CUR_CELL_POS
        LDAA #CASE_CUR_Y
        STAA >CUR_CELL_POS+1
        JSR CARVE_CUR_CELL
        LDAA #CASE_CUR_X
        STAA >READ_CELL_POS
        LDAA #CASE_CUR_Y
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_CUR_CHAR
        LDAA #4
        STAA >READ_CELL_POS
        LDAA #3
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_CUR_REF
        RTS

CASE_PASS_E:
        LDAA #CASE_E_X
        STAA >CUR_CELL_POS
        LDAA #CASE_E_Y
        STAA >CUR_CELL_POS+1
        LDAA #CASE_E_X + 1
        STAA >NEXT_CELL_POS
        LDAA #CASE_E_Y
        STAA >NEXT_CELL_POS+1
        LDAA #DIR_E
        STAA >TMP_CHOICE
        JSR CARVE_CUR_CELL
        JSR CARVE_PASSAGE
        LDAA #CASE_E_X
        STAA >READ_CELL_POS
        LDAA #CASE_E_Y
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_PASS_E_CUR
        LDAA #CASE_E_Y
        JSR SET_ROW_FOR_Y
        LDAA #CASE_E_X
        JSR SET_COL_FOR_X
        LDAA >COL_INDEX
        INCA
        STAA >COL_INDEX
        JSR BUILD_CHAR_FROM_RC
        JSR LOAD_CHAR_FROM_PTR
        STAA >RESULT_PASS_E_WALL
        LDAA #CASE_E_Y
        JSR SET_ROW_FOR_Y
        LDAA #CASE_E_X + 1
        JSR SET_COL_FOR_X
        JSR BUILD_CHAR_FROM_RC
        JSR LOAD_CHAR_FROM_PTR
        STAA >RESULT_PASS_E_NEXT
        LDAA #4
        STAA >READ_CELL_POS
        LDAA #4
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_PASS_E_REF
        RTS

CASE_PASS_N:
        LDAA #CASE_N_X
        STAA >CUR_CELL_POS
        LDAA #CASE_N_Y
        STAA >CUR_CELL_POS+1
        LDAA #CASE_N_X
        STAA >NEXT_CELL_POS
        LDAA #CASE_N_Y - 1
        STAA >NEXT_CELL_POS+1
        LDAA #DIR_N
        STAA >TMP_CHOICE
        JSR CARVE_CUR_CELL
        JSR CARVE_PASSAGE
        LDAA #CASE_N_X
        STAA >READ_CELL_POS
        LDAA #CASE_N_Y
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_PASS_N_CUR
        LDAA #CASE_N_Y
        JSR SET_ROW_FOR_Y
        DECA
        STAA >ROW_INDEX
        LDAA #CASE_N_X
        JSR SET_COL_FOR_X
        JSR BUILD_CHAR_FROM_RC
        JSR LOAD_CHAR_FROM_PTR
        STAA >RESULT_PASS_N_WALL
        LDAA #CASE_N_X
        STAA >READ_CELL_POS
        LDAA #CASE_N_Y - 1
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_PASS_N_NEXT
        LDAA #4
        STAA >READ_CELL_POS
        LDAA #4
        STAA >READ_CELL_POS+1
        JSR READ_CELL_CHAR
        STAA >RESULT_PASS_N_REF
        RTS

INIT_MAP:
        LDX #MAZE_MAP
        LDAA #'#'
FILL_MAP:
        STAA 0,X
        INX
        CPX #(MAZE_MAP + MAZE_CHAR_W * MAZE_CHAR_H)
        BNE FILL_MAP
        RTS

READ_CELL_CHAR:
        LDX #READ_CELL_POS
        JSR BUILD_CHAR_POINTER
        JSR LOAD_CHAR_FROM_PTR
        RTS

LOAD_CHAR_FROM_PTR:
        LDX TEMP_PTR
        LDAA 0,X
        RTS

SET_ROW_FOR_Y:
        ASLA
        INCA
        STAA >ROW_INDEX
        RTS

SET_COL_FOR_X:
        ASLA
        INCA
        STAA >COL_INDEX
        RTS

CARVE_CUR_CELL:
        LDX #CUR_CELL_POS
        JSR BUILD_CHAR_POINTER
        JSR WRITE_SPACE_AT_PTR
        RTS

CARVE_PASSAGE:
        LDX #CUR_CELL_POS
        JSR BUILD_CHAR_POINTER
        LDAA >ROW_INDEX
        STAA >CHAR_OFFSET_LO
        LDAA >COL_INDEX
        STAA >CHAR_OFFSET_HI
        LDAA TMP_CHOICE
        CMPA #DIR_N
        BEQ PASSAGE_N
        CMPA #DIR_E
        BEQ PASSAGE_E
        CMPA #DIR_S
        BEQ PASSAGE_S
        LDAA >CHAR_OFFSET_HI
        DECA
        STAA >CHAR_OFFSET_HI
        BRA PASSAGE_COMMON
PASSAGE_N:
        LDAA >CHAR_OFFSET_LO
        DECA
        STAA >CHAR_OFFSET_LO
        BRA PASSAGE_COMMON
PASSAGE_E:
        LDAA >CHAR_OFFSET_HI
        INCA
        STAA >CHAR_OFFSET_HI
        BRA PASSAGE_COMMON
PASSAGE_S:
        LDAA >CHAR_OFFSET_LO
        INCA
        STAA >CHAR_OFFSET_LO
PASSAGE_COMMON:
        LDAA >CHAR_OFFSET_LO
        STAA >ROW_INDEX
        LDAA >CHAR_OFFSET_HI
        STAA >COL_INDEX
        JSR BUILD_CHAR_FROM_RC
        JSR WRITE_SPACE_AT_PTR
        LDX #NEXT_CELL_POS
        JSR BUILD_CHAR_POINTER
        JSR WRITE_SPACE_AT_PTR
        RTS

BUILD_CHAR_POINTER:
        LDAA 0,X
        ASLA
        INCA
        STAA >COL_INDEX
        LDAA 1,X
        ASLA
        INCA
        STAA >ROW_INDEX
        JSR BUILD_CHAR_FROM_RC
        RTS

BUILD_CHAR_FROM_RC:
        CLRA
        STAA >CHAR_OFFSET_LO
        STAA >CHAR_OFFSET_HI
        LDAA >ROW_INDEX
        BEQ CHAR_ROW_DONE
        STAA TEMP_SHIFT
CHAR_ROW_LOOP:
        LDAA >CHAR_OFFSET_LO
        ADDA #MAZE_CHAR_W
        STAA >CHAR_OFFSET_LO
        LDAA >CHAR_OFFSET_HI
        ADCA #0
        STAA >CHAR_OFFSET_HI
        DEC TEMP_SHIFT
        BNE CHAR_ROW_LOOP
CHAR_ROW_DONE:
        LDAA >COL_INDEX
        ADDA >CHAR_OFFSET_LO
        STAA >CHAR_OFFSET_LO
        LDAA #0
        ADCA >CHAR_OFFSET_HI
        STAA >CHAR_OFFSET_HI
        LDX #MAZE_MAP
        STX TEMP_PTR
        LDAA >CHAR_OFFSET_LO
        ADDA TEMP_PTR+1
        STAA TEMP_PTR+1
        LDAA >CHAR_OFFSET_HI
        ADCA TEMP_PTR
        STAA TEMP_PTR
        RTS

WRITE_SPACE_AT_PTR:
        LDX TEMP_PTR
        LDAA #' '
        STAA 0,X
        RTS
