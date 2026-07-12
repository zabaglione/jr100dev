.org $0300

.include "../src/common.inc"

; --- 定数 ----------------------------------------------------------------

DIR_COUNT:      .equ 4
DIR_N:          .equ 0
DIR_E:          .equ 1
DIR_S:          .equ 2
DIR_W:          .equ 3

; Case 1: 中央セル (2,2)
CASE1_X:                .equ 2
CASE1_Y:                .equ 2
CASE1_NORTH_OFFSET:     .equ ((CASE1_Y - 1) * MAZE_CELL_W + CASE1_X)
CASE1_SOUTH_OFFSET:     .equ ((CASE1_Y + 1) * MAZE_CELL_W + CASE1_X)
CASE1_EAST_OFFSET:      .equ (CASE1_Y * MAZE_CELL_W + (CASE1_X + 1))
CASE1_WEST_OFFSET:      .equ (CASE1_Y * MAZE_CELL_W + (CASE1_X - 1))

; Case 2: 左上セル (0,0)
CASE2_X:                .equ 0
CASE2_Y:                .equ 0

; Case 3: 右下セル (MAZE_CELL_W-1, MAZE_CELL_H-1)
CASE3_X:                .equ (MAZE_CELL_W - 1)
CASE3_Y:                .equ (MAZE_CELL_H - 1)
CASE3_NORTH_OFFSET:     .equ ((CASE3_Y - 1) * MAZE_CELL_W + CASE3_X)
CASE3_WEST_OFFSET:      .equ (CASE3_Y * MAZE_CELL_W + (CASE3_X - 1))

; 結果書き込み先
RESULT_CASE1_COUNT:     .equ $0600
RESULT_CASE1_DIR0:      .equ $0601
RESULT_CASE1_DIR1:      .equ $0602
RESULT_CASE1_DIR2:      .equ $0603
RESULT_CASE1_DIR3:      .equ $0604

RESULT_CASE2_COUNT:     .equ $0605
RESULT_CASE2_DIR0:      .equ $0606
RESULT_CASE2_DIR1:      .equ $0607
RESULT_CASE2_DIR2:      .equ $0608
RESULT_CASE2_DIR3:      .equ $0609

RESULT_CASE3_COUNT:     .equ $060A
RESULT_CASE3_DIR0:      .equ $060B
RESULT_CASE3_DIR1:      .equ $060C
RESULT_CASE3_DIR2:      .equ $060D
RESULT_CASE3_DIR3:      .equ $060E

DEBUG_C1_AFTER_N:       .equ $0610
DEBUG_C1_AFTER_E:       .equ $0611
DEBUG_C1_AFTER_S:       .equ $0612
DEBUG_C1_AFTER_W:       .equ $0613
DEBUG_C1_VAL_N:         .equ $0614
DEBUG_C1_VAL_E:         .equ $0615
DEBUG_C1_VAL_S:         .equ $0616
DEBUG_C1_VAL_W:         .equ $0617
DEBUG_C1_VIS_N:         .equ $0618
DEBUG_C1_VIS_S:         .equ $0619
DEBUG_C1_VIS_E:         .equ $061A
DEBUG_C1_VIS_W:         .equ $061B

TMP_BASE:               .equ $0700
TMP_DIR_COUNT:          .equ TMP_BASE
TMP_DIR_BUF:            .equ (TMP_BASE + 1)
CUR_CELL_POS:           .equ (TMP_BASE + 5)
NEXT_CELL_POS:          .equ (TMP_BASE + 7)
CELL_OFFSET_LO:         .equ (TMP_BASE + 9)
CELL_OFFSET_HI:         .equ (TMP_BASE + 10)
TEMP_PTR:               .equ (TMP_BASE + 11)
TEMP_SHIFT:             .equ (TMP_BASE + 13)
TMP_LAST_LOAD:          .equ (TMP_BASE + 14)

VISITED_MAP:            .equ $0800
VISITED_MAP_END:        .equ (VISITED_MAP + MAZE_CELL_W * MAZE_CELL_H)

; --- メイン --------------------------------------------------------------

START:
        JSR CASE1
        JSR CASE2
        JSR CASE3

HALT:
        BRA HALT

; --- ケース定義 ----------------------------------------------------------

CASE1:
        JSR CLEAR_STATE
        LDX #(VISITED_MAP + CASE1_NORTH_OFFSET)
        LDAA #1
        STAA 0,X
        LDX #(VISITED_MAP + CASE1_SOUTH_OFFSET)
        STAA 0,X
        LDAA VISITED_MAP + CASE1_NORTH_OFFSET
        STAA DEBUG_C1_VIS_N
        LDAA VISITED_MAP + CASE1_SOUTH_OFFSET
        STAA DEBUG_C1_VIS_S
        LDAA VISITED_MAP + CASE1_EAST_OFFSET
        STAA DEBUG_C1_VIS_E
        LDAA VISITED_MAP + CASE1_WEST_OFFSET
        STAA DEBUG_C1_VIS_W
        LDAA #CASE1_X
        STAA CUR_CELL_POS
        LDAA #CASE1_Y
        STAA CUR_CELL_POS+1
        CLR TMP_DIR_COUNT
        JSR CHECK_NORTH
        LDAA TMP_LAST_LOAD
        STAA DEBUG_C1_VAL_N
        LDAA TMP_DIR_COUNT
        STAA DEBUG_C1_AFTER_N
        JSR CHECK_EAST
        LDAA TMP_LAST_LOAD
        STAA DEBUG_C1_VAL_E
        LDAA TMP_DIR_COUNT
        STAA DEBUG_C1_AFTER_E
        JSR CHECK_SOUTH
        LDAA TMP_LAST_LOAD
        STAA DEBUG_C1_VAL_S
        LDAA TMP_DIR_COUNT
        STAA DEBUG_C1_AFTER_S
        JSR CHECK_WEST
        LDAA TMP_LAST_LOAD
        STAA DEBUG_C1_VAL_W
        LDAA TMP_DIR_COUNT
        STAA DEBUG_C1_AFTER_W
        JSR STORE_CASE1_RESULT
        RTS

CASE2:
        JSR CLEAR_STATE
        CLRA
        STAA CUR_CELL_POS
        STAA CUR_CELL_POS+1
        CLR TMP_DIR_COUNT
        JSR CHECK_NORTH
        JSR CHECK_EAST
        JSR CHECK_SOUTH
        JSR CHECK_WEST
        JSR STORE_CASE2_RESULT
        RTS

CASE3:
        JSR CLEAR_STATE
        LDX #(VISITED_MAP + CASE3_NORTH_OFFSET)
        LDAA #1
        STAA 0,X
        LDX #(VISITED_MAP + CASE3_WEST_OFFSET)
        STAA 0,X
        LDAA #CASE3_X
        STAA CUR_CELL_POS
        LDAA #CASE3_Y
        STAA CUR_CELL_POS+1
        CLR TMP_DIR_COUNT
        JSR CHECK_NORTH
        JSR CHECK_EAST
        JSR CHECK_SOUTH
        JSR CHECK_WEST
        JSR STORE_CASE3_RESULT
        RTS

; --- 結果保存 ------------------------------------------------------------

STORE_CASE1_RESULT:
        LDAA TMP_DIR_COUNT
        STAA RESULT_CASE1_COUNT
        LDAA TMP_DIR_BUF
        STAA RESULT_CASE1_DIR0
        LDAA TMP_DIR_BUF+1
        STAA RESULT_CASE1_DIR1
        LDAA TMP_DIR_BUF+2
        STAA RESULT_CASE1_DIR2
        LDAA TMP_DIR_BUF+3
        STAA RESULT_CASE1_DIR3
        RTS

STORE_CASE2_RESULT:
        LDAA TMP_DIR_COUNT
        STAA RESULT_CASE2_COUNT
        LDAA TMP_DIR_BUF
        STAA RESULT_CASE2_DIR0
        LDAA TMP_DIR_BUF+1
        STAA RESULT_CASE2_DIR1
        LDAA TMP_DIR_BUF+2
        STAA RESULT_CASE2_DIR2
        LDAA TMP_DIR_BUF+3
        STAA RESULT_CASE2_DIR3
        RTS

STORE_CASE3_RESULT:
        LDAA TMP_DIR_COUNT
        STAA RESULT_CASE3_COUNT
        LDAA TMP_DIR_BUF
        STAA RESULT_CASE3_DIR0
        LDAA TMP_DIR_BUF+1
        STAA RESULT_CASE3_DIR1
        LDAA TMP_DIR_BUF+2
        STAA RESULT_CASE3_DIR2
        LDAA TMP_DIR_BUF+3
        STAA RESULT_CASE3_DIR3
        RTS

; --- 初期化 --------------------------------------------------------------

CLEAR_STATE:
        LDX #VISITED_MAP
        CLRA
CLEAR_VISITED_LOOP:
        STAA 0,X
        INX
        CPX #VISITED_MAP_END
        BNE CLEAR_VISITED_LOOP
        CLR TMP_DIR_COUNT
        LDAA #$EE
        STAA TMP_DIR_BUF
        STAA TMP_DIR_BUF+1
        STAA TMP_DIR_BUF+2
        STAA TMP_DIR_BUF+3
        CLR TMP_LAST_LOAD
        RTS

; --- 近傍探索ロジック (maze_gen.asm より抜粋) ---------------------------

FIND_NEIGHBORS:
        CLR TMP_DIR_COUNT
        JSR CHECK_NORTH
        JSR CHECK_EAST
        JSR CHECK_SOUTH
        JSR CHECK_WEST
        RTS

CHECK_NORTH:
        LDAA CUR_CELL_POS+1
        BEQ CHECK_NORTH_END
        DECA
        STAA NEXT_CELL_POS+1
        LDAA CUR_CELL_POS
        STAA NEXT_CELL_POS
        JSR LOAD_NEXT_VISITED
        BNE CHECK_NORTH_END
        LDAA #DIR_N
        JSR ADD_DIRECTION
CHECK_NORTH_END:
        RTS

CHECK_EAST:
        LDAA CUR_CELL_POS
        CMPA #MAZE_CELL_W - 1
        BCC CHECK_EAST_END
        INCA
        STAA NEXT_CELL_POS
        LDAA CUR_CELL_POS+1
        STAA NEXT_CELL_POS+1
        JSR LOAD_NEXT_VISITED
        BNE CHECK_EAST_END
        LDAA #DIR_E
        JSR ADD_DIRECTION
CHECK_EAST_END:
        RTS

CHECK_SOUTH:
        LDAA CUR_CELL_POS+1
        CMPA #MAZE_CELL_H - 1
        BCC CHECK_SOUTH_END
        INCA
        STAA NEXT_CELL_POS+1
        LDAA CUR_CELL_POS
        STAA NEXT_CELL_POS
        JSR LOAD_NEXT_VISITED
        BNE CHECK_SOUTH_END
        LDAA #DIR_S
        JSR ADD_DIRECTION
CHECK_SOUTH_END:
        RTS

CHECK_WEST:
        LDAA CUR_CELL_POS
        BEQ CHECK_WEST_END
        DECA
        STAA NEXT_CELL_POS
        LDAA CUR_CELL_POS+1
        STAA NEXT_CELL_POS+1
        JSR LOAD_NEXT_VISITED
        BNE CHECK_WEST_END
        LDAA #DIR_W
        JSR ADD_DIRECTION
CHECK_WEST_END:
        RTS

ADD_DIRECTION:
        LDAB TMP_DIR_COUNT
        CMPB #DIR_COUNT
        BCC ADD_DIRECTION_END
        LDX #TMP_DIR_BUF
ADD_DIR_PTR_LOOP:
        TSTB
        BEQ ADD_DIR_STORE
        INX
        DECB
        BRA ADD_DIR_PTR_LOOP
ADD_DIR_STORE:
        STAA 0,X
        INC TMP_DIR_COUNT
ADD_DIRECTION_END:
        RTS

LOAD_NEXT_VISITED:
        LDX #NEXT_CELL_POS
        JSR BUILD_CELL_OFFSET
        LDX #VISITED_MAP
        STX TEMP_PTR
        LDAA CELL_OFFSET_LO
        ADDA TEMP_PTR+1
        STAA TEMP_PTR+1
        LDAA CELL_OFFSET_HI
        ADCA TEMP_PTR
        STAA TEMP_PTR
        LDX TEMP_PTR
        LDAA 0,X
        STAA TMP_LAST_LOAD
        RTS

BUILD_CELL_OFFSET:
        CLRA
        STAA CELL_OFFSET_LO
        STAA CELL_OFFSET_HI
        LDAA 1,X
        BEQ CELL_ROW_DONE
        STAA TEMP_SHIFT
CELL_ROW_LOOP:
        LDAA CELL_OFFSET_LO
        ADDA #MAZE_CELL_W
        STAA CELL_OFFSET_LO
        LDAA CELL_OFFSET_HI
        ADCA #0
        STAA CELL_OFFSET_HI
        DEC TEMP_SHIFT
        BNE CELL_ROW_LOOP
CELL_ROW_DONE:
        LDAA 0,X
        ADDA CELL_OFFSET_LO
        STAA CELL_OFFSET_LO
        LDAA #0
        ADCA CELL_OFFSET_HI
        STAA CELL_OFFSET_HI
        RTS
