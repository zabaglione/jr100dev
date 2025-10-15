.org $0300

.include "../src/common.inc"
.include "../src/maze_helpers.inc"

RESULT_CUR_WALL_E:      .equ $0600
RESULT_NEXT_WALL_E:     .equ $0601
RESULT_CUR_VIS_E:       .equ $0602
RESULT_NEXT_VIS_E:      .equ $0603
RESULT_CUR_WALL_N:      .equ $0604
RESULT_NEXT_WALL_N:     .equ $0605
RESULT_CUR_VIS_N:       .equ $0606
RESULT_NEXT_VIS_N:      .equ $0607

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

MAZE_CELLS:             .equ $0800
MAZE_CELLS_HI:          .equ ((MAZE_CELLS >> 8) & $00FF)
MAZE_CELLS_LO:          .equ (MAZE_CELLS & $00FF)
VISITED_MAP:            .equ (MAZE_CELLS + MAZE_CELL_W * MAZE_CELL_H)
VISITED_MAP_HI:         .equ ((VISITED_MAP >> 8) & $00FF)
VISITED_MAP_LO:         .equ (VISITED_MAP & $00FF)
VISITED_MAP_END:        .equ (VISITED_MAP + MAZE_CELL_W * MAZE_CELL_H)

CASE1_X:                .equ 1
CASE1_Y:                .equ 1
CASE2_X:                .equ 2
CASE2_Y:                .equ 2

START:
        JSR INIT_MEMORY
        JSR CASE_EAST
        JSR INIT_MEMORY
        JSR CASE_NORTH
HALT:
        BRA HALT

CASE_EAST:
        LDAA #CASE1_X
        STAA CUR_CELL_POS
        LDAA #CASE1_Y
        STAA CUR_CELL_POS+1
        LDAA #CASE1_X + 1
        STAA NEXT_CELL_POS
        LDAA #CASE1_Y
        STAA NEXT_CELL_POS+1
        LDAA #DIR_E
        STAA TMP_CHOICE
        JSR CLEAR_WALLS_BETWEEN
        JSR MARK_CUR_VISITED
        JSR MARK_NEXT_VISITED
        JSR STORE_CUR_CELL_RESULT
        STAA RESULT_CUR_WALL_E
        JSR STORE_NEXT_CELL_RESULT
        STAA RESULT_NEXT_WALL_E
        JSR STORE_CUR_VISITED
        STAA RESULT_CUR_VIS_E
        JSR STORE_NEXT_VISITED
        STAA RESULT_NEXT_VIS_E
        RTS

CASE_NORTH:
        LDAA #CASE2_X
        STAA CUR_CELL_POS
        LDAA #CASE2_Y
        STAA CUR_CELL_POS+1
        LDAA #CASE2_X
        STAA NEXT_CELL_POS
        LDAA #CASE2_Y - 1
        STAA NEXT_CELL_POS+1
        LDAA #DIR_N
        STAA TMP_CHOICE
        JSR CLEAR_WALLS_BETWEEN
        JSR MARK_CUR_VISITED
        JSR MARK_NEXT_VISITED
        JSR STORE_CUR_CELL_RESULT
        STAA RESULT_CUR_WALL_N
        JSR STORE_NEXT_CELL_RESULT
        STAA RESULT_NEXT_WALL_N
        JSR STORE_CUR_VISITED
        STAA RESULT_CUR_VIS_N
        JSR STORE_NEXT_VISITED
        STAA RESULT_NEXT_VIS_N
        RTS

INIT_MEMORY:
        LDX #MAZE_CELLS
        LDAB #$0F
FILL_CELLS:
        STAB 0,X
        INX
        CPX #VISITED_MAP
        BNE FILL_CELLS
        LDX #VISITED_MAP
        CLRB
FILL_VISITED:
        STAB 0,X
        INX
        CPX #VISITED_MAP_END
        BNE FILL_VISITED
        CLR TMP_DIR_COUNT
        CLR TMP_LAST_LOAD
        RTS

STORE_CUR_CELL_RESULT:
        LDX #CUR_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_CELL_PTR
        LDX TEMP_PTR
        LDAA 0,X
        RTS

STORE_NEXT_CELL_RESULT:
        LDX #NEXT_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_CELL_PTR
        LDX TEMP_PTR
        LDAA 0,X
        RTS

STORE_CUR_VISITED:
        LDX #CUR_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_VIS_PTR
        LDX TEMP_PTR
        LDAA 0,X
        RTS

STORE_NEXT_VISITED:
        LDX #NEXT_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_VIS_PTR
        LDX TEMP_PTR
        LDAA 0,X
        RTS

LOAD_CELL_PTR:
        LDAA #MAZE_CELLS_LO
        ADDA CELL_OFFSET_LO
        STAA TEMP_PTR+1
        LDAA #MAZE_CELLS_HI
        ADCA CELL_OFFSET_HI
        STAA TEMP_PTR
        RTS

LOAD_VIS_PTR:
        LDAA #VISITED_MAP_LO
        ADDA CELL_OFFSET_LO
        STAA TEMP_PTR+1
        LDAA #VISITED_MAP_HI
        ADCA CELL_OFFSET_HI
        STAA TEMP_PTR
        RTS

CLEAR_WALLS_BETWEEN:
        LDAA TMP_CHOICE
        CMPA #DIR_N
        BEQ CLEAR_N
        CMPA #DIR_E
        BEQ CLEAR_E
        CMPA #DIR_S
        BEQ CLEAR_S
        LDAA #WALL_W
        JSR CLEAR_CUR_WALL
        LDAA #WALL_E
        JSR CLEAR_NEXT_WALL
        RTS
CLEAR_N:
        LDAA #WALL_N
        JSR CLEAR_CUR_WALL
        LDAA #WALL_S
        JSR CLEAR_NEXT_WALL
        RTS
CLEAR_E:
        LDAA #WALL_E
        JSR CLEAR_CUR_WALL
        LDAA #WALL_W
        JSR CLEAR_NEXT_WALL
        RTS
CLEAR_S:
        LDAA #WALL_S
        JSR CLEAR_CUR_WALL
        LDAA #WALL_N
        JSR CLEAR_NEXT_WALL
        RTS

CLEAR_CUR_WALL:
        STAA TMP_MASK
        LDX #CUR_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_CELL_PTR
        LDX TEMP_PTR
        LDAA TMP_MASK
        COMA
        STAA TMP_MASK
        LDAA 0,X
        ANDA TMP_MASK
        STAA 0,X
        RTS

CLEAR_NEXT_WALL:
        STAA TMP_MASK
        LDX #NEXT_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_CELL_PTR
        LDX TEMP_PTR
        LDAA TMP_MASK
        COMA
        STAA TMP_MASK
        LDAA 0,X
        ANDA TMP_MASK
        STAA 0,X
        RTS

MARK_CUR_VISITED:
        LDX #CUR_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_VIS_PTR
        LDX TEMP_PTR
        LDAA #1
        STAA 0,X
        RTS

MARK_NEXT_VISITED:
        LDX #NEXT_CELL_POS
        JSR BUILD_CELL_OFFSET
        JSR LOAD_VIS_PTR
        LDX TEMP_PTR
        LDAA #1
        STAA 0,X
        RTS

BUILD_CELL_OFFSET:
        CLRA
        STAA CELL_OFFSET_LO
        STAA CELL_OFFSET_HI
        LDAA 1,X
        BEQ ADD_X
        STAA TEMP_SHIFT
ROW_LOOP:
        LDAA CELL_OFFSET_LO
        ADDA #MAZE_CELL_W
        STAA CELL_OFFSET_LO
        LDAA CELL_OFFSET_HI
        ADCA #0
        STAA CELL_OFFSET_HI
        DEC TEMP_SHIFT
        BNE ROW_LOOP
ADD_X:
        LDAA 0,X
        ADDA CELL_OFFSET_LO
        STAA CELL_OFFSET_LO
        LDAA #0
        ADCA CELL_OFFSET_HI
        STAA CELL_OFFSET_HI
        RTS
