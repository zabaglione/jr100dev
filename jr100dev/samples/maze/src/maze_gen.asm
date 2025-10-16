        .org $2000
        .include "macro.inc"
        .include "ctl.inc"
        .include "common.inc"
        .include "scroll.inc"
        .include "maze_helpers.inc"
        .code

; 迷路サンプルのメインロジック。
; プリセット迷路をロードして描画し、プレイヤー移動・スクロール・ゴール判定を処理する。
; 旧来の壁伸ばし法で使用していたワーク領域も残しており、必要に応じてロジックを拡張できる構成。

MENU_ROW_TITLE1:   .equ 2
MENU_ROW_TITLE2:   .equ 4
MENU_ROW_FOOTER:   .equ 10
MENU_BLINK_PERIOD: .equ 250   ; WAIT_2MS ループ×250で 1 ティック
MENU_COL_OPTION:   .equ 6

; --- 初期化 -------------------------------------------------------------

MAZE_INIT:
        ; --- マップ (#) 初期化 ---
        LDAA CUR_CHAR_H
        STAA ROW_INDEX
        LDX #MAZE_MAP
MI_MAP_ROW_LOOP:
        LDAA ROW_INDEX
        BEQ MI_CELLS
        DEC ROW_INDEX
        LDAA CUR_CHAR_W
        STAA COL_INDEX
MI_MAP_COL_LOOP:
        LDAA #'#'
        STAA ,X
        INX
        DEC COL_INDEX
        BNE MI_MAP_COL_LOOP
        BRA MI_MAP_ROW_LOOP

        ; --- セル属性 ($0F) 初期化 ---
MI_CELLS:
        LDAA CUR_CELL_H
        STAA ROW_INDEX
        LDX #MAZE_CELLS
MI_CELL_ROW_LOOP:
        LDAA ROW_INDEX
        BEQ MI_VISITED
        DEC ROW_INDEX
        LDAA CUR_CELL_W
        STAA COL_INDEX
MI_CELL_COL_LOOP:
        LDAA #$0F
        STAA ,X
        INX
        DEC COL_INDEX
        BNE MI_CELL_COL_LOOP
        BRA MI_CELL_ROW_LOOP

        ; --- 訪問フラグ初期化 ---
MI_VISITED:
        LDAA CUR_CELL_H
        STAA ROW_INDEX
        LDX #VISITED_MAP
MI_VISITED_ROW_LOOP:
        LDAA ROW_INDEX
        BEQ MI_DONE
        DEC ROW_INDEX
        LDAA CUR_CELL_W
        STAA COL_INDEX
        CLRA
MI_VISITED_COL_LOOP:
        STAA ,X
        INX
        DEC COL_INDEX
        BNE MI_VISITED_COL_LOOP
        BRA MI_VISITED_ROW_LOOP

MI_DONE:
        RTS


; --- スタック操作 -------------------------------------------------------

STACK_RESET:
        LDX #STACK_BASE
        STX STACK_PTR
        RTS

STACK_PUSH_CUR:
        LDX STACK_PTR
        LDAA CUR_CELL_POS
        STAA 0,X
        INX
        LDAA CUR_CELL_POS+1
        STAA 0,X
        INX
        STX STACK_PTR
        RTS

STACK_PUSH_NEXT:
        LDX STACK_PTR
        LDAA NEXT_CELL_POS
        STAA 0,X
        INX
        LDAA NEXT_CELL_POS+1
        STAA 0,X
        INX
        STX STACK_PTR
        RTS

STACK_PEEK_CUR:
        LDX STACK_PTR
        CPX #STACK_BASE
        BEQ STACK_PEEK_EMPTY
        DEX
        LDAA 0,X
        STAA CUR_CELL_POS+1
        DEX
        LDAA 0,X
        STAA CUR_CELL_POS
        CLC
        RTS
STACK_PEEK_EMPTY:
        SEC
        RTS

STACK_POP_TO_CUR:
        LDX STACK_PTR
        CPX #STACK_BASE
        BEQ STACK_POP_EMPTY
        DEX
        DEX
        STX STACK_PTR
        LDAA 1,X
        STAA CUR_CELL_POS+1
        LDAA 0,X
        STAA CUR_CELL_POS
        CLC
        RTS
STACK_POP_EMPTY:
        SEC
        RTS


; --- 近傍探索 -----------------------------------------------------------

FIND_NEIGHBORS:
        CLR TMP_DIR_COUNT
        CLR TMP_DIR_MASK

        ; 北を確認
        LDAA CUR_CELL_POS+1
        BEQ FN_SKIP_N
        DECA
        STAA NEXT_CELL_POS+1
        LDAA CUR_CELL_POS
        STAA NEXT_CELL_POS
        LDAA #DIR_N
        JSR FN_CHECK_STORE
FN_SKIP_N:
        ; 東を確認
        LDAA CUR_CELL_POS
        CMPA CUR_CELL_MAX_X
        BEQ FN_SKIP_E
        INCA
        STAA NEXT_CELL_POS
        LDAA CUR_CELL_POS+1
        STAA NEXT_CELL_POS+1
        LDAA #DIR_E
        JSR FN_CHECK_STORE
FN_SKIP_E:
        ; 南を確認
        LDAA CUR_CELL_POS+1
        CMPA CUR_CELL_MAX_Y
        BEQ FN_SKIP_S
        INCA
        STAA NEXT_CELL_POS+1
        LDAA CUR_CELL_POS
        STAA NEXT_CELL_POS
        LDAA #DIR_S
        JSR FN_CHECK_STORE
FN_SKIP_S:
        ; 西を確認
        LDAA CUR_CELL_POS
        BEQ FN_DONE
        DECA
        STAA NEXT_CELL_POS
        LDAA CUR_CELL_POS+1
        STAA NEXT_CELL_POS+1
        LDAA #DIR_W
        JSR FN_CHECK_STORE
FN_DONE:
        RTS

FN_CHECK_STORE:
        PSHA
        LDX #NEXT_CELL_POS
        JSR LOAD_VISITED_PTR
        LDAA 0,X
        BITA #CELL_VISITED_FLAG
        BNE FN_CHECK_SKIP
        PULA
        STAA TMP_CHOICE
        LDAB TMP_DIR_COUNT
        LDX #TMP_DIR_BUF
FN_BUF_ADV_LOOP:
        TSTB
        BEQ FN_BUF_STORE
        DECB
        INX
        BRA FN_BUF_ADV_LOOP
FN_BUF_STORE:
        LDAA TMP_CHOICE
        STAA 0,X
        INC TMP_DIR_COUNT
        LDAA TMP_CHOICE
        CMPA #DIR_N
        BEQ FN_MASK_N
        CMPA #DIR_E
        BEQ FN_MASK_E
        CMPA #DIR_S
        BEQ FN_MASK_S
        ; DIR_W
        LDAA TMP_DIR_MASK
        ORAA #DIR_BIT_W
        BRA FN_MASK_DONE
FN_MASK_N:
        LDAA TMP_DIR_MASK
        ORAA #DIR_BIT_N
        BRA FN_MASK_DONE
FN_MASK_E:
        LDAA TMP_DIR_MASK
        ORAA #DIR_BIT_E
        BRA FN_MASK_DONE
FN_MASK_S:
        LDAA TMP_DIR_MASK
        ORAA #DIR_BIT_S
FN_MASK_DONE:
        STAA TMP_DIR_MASK
        RTS
FN_CHECK_SKIP:
        PULA
        RTS

; --- 路の選択と掘削 ----------------------------------------------------

CHOOSE_AND_ADVANCE:
        LDAA TMP_DIR_COUNT
        STAA DEBUG_DIR_COUNT
        BEQ CA_DONE
        LDAA RNG_SEED
        ASLA
        ASLA
        ADDA RNG_SEED
        ADDA #$01
        STAA RNG_SEED
        LDAA RNG_SEED
CA_NORMALISE:
        CMPA TMP_DIR_COUNT
        BCS CA_INDEX_READY
        SUBA TMP_DIR_COUNT
        BRA CA_NORMALISE
CA_INDEX_READY:
        TAB
        LDX #TMP_DIR_BUF
CA_ADVANCE_LOOP:
        TSTB
        BEQ CA_SELECT
        DECB
        INX
        BRA CA_ADVANCE_LOOP
CA_SELECT:
        LDAA 0,X
        STAA TMP_CHOICE
        JSR SET_NEXT_FROM_DIRECTION
        JSR CLEAR_WALLS_BETWEEN
        JSR MARK_NEXT_VISITED
        JSR CARVE_PASSAGE
        JSR STACK_PUSH_NEXT
        LDAA NEXT_CELL_POS
        STAA CUR_CELL_POS
        LDAA NEXT_CELL_POS+1
        STAA CUR_CELL_POS+1
        JSR MARK_CUR_VISITED
        JSR CARVE_CUR_CELL
CA_DONE:
        RTS

SET_NEXT_FROM_DIRECTION:
        LDAA CUR_CELL_POS
        STAA NEXT_CELL_POS
        LDAA CUR_CELL_POS+1
        STAA NEXT_CELL_POS+1
        LDAA TMP_CHOICE
        CMPA #DIR_N
        BEQ SET_DIR_N
        CMPA #DIR_E
        BEQ SET_DIR_E
        CMPA #DIR_S
        BEQ SET_DIR_S
        ; DIR_W
        LDAA NEXT_CELL_POS
        DECA
        STAA NEXT_CELL_POS
        RTS
SET_DIR_N:
        LDAA NEXT_CELL_POS+1
        DECA
        STAA NEXT_CELL_POS+1
        RTS
SET_DIR_E:
        LDAA NEXT_CELL_POS
        INCA
        STAA NEXT_CELL_POS
        RTS
SET_DIR_S:
        LDAA NEXT_CELL_POS+1
        INCA
        STAA NEXT_CELL_POS+1
        RTS

CLEAR_WALLS_BETWEEN:
        LDAA TMP_CHOICE
        CMPA #DIR_N
        BEQ CLEAR_N
        CMPA #DIR_E
        BEQ CLEAR_E
        CMPA #DIR_S
        BEQ CLEAR_S
        ; DIR_W
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
        JSR LOAD_CELL_PTR
        LDAA TMP_MASK
        COMA
        STAA TMP_MASK
        LDAA 0,X
        ANDA TMP_MASK
        STAA 0,X
        RTS

MARK_CUR_VISITED:
        LDX #CUR_CELL_POS
        JSR LOAD_VISITED_PTR
        LDAA TEMP_PTR
        STAA DEBUG_NEXT_VISITED
        STX DEBUG_VISIT_PTR
        LDAA 0,X
        ORAA #CELL_VISITED_FLAG
        STAA DEBUG_VISIT_VAL
        STAA 0,X
        RTS

MARK_NEXT_VISITED:
        LDX #NEXT_CELL_POS
        JSR LOAD_VISITED_PTR
        STX DEBUG_VISIT_PTR
        LDAA 0,X
        ORAA #CELL_VISITED_FLAG
        STAA DEBUG_VISIT_VAL
        STAA 0,X
        RTS

LOAD_VISITED_PTR:
        JSR BUILD_CELL_OFFSET
        LDX #VISITED_MAP
        LDAA #>VISITED_MAP
        STAA DEBUG_ROW_VAL
        LDAA #<VISITED_MAP
        STAA DEBUG_COL_VAL
        STX TEMP_PTR
        ADD16 TEMP_PTR+1, TEMP_PTR, CELL_OFFSET_LO, CELL_OFFSET_HI
        LDAA TEMP_PTR
        STAA DEBUG_VISIT_PTR
        LDAA TEMP_PTR+1
        STAA DEBUG_VISIT_PTR+1
        LDX TEMP_PTR
        RTS

LOAD_CELL_PTR:
        JSR BUILD_CELL_OFFSET
        LDX #MAZE_CELLS
        STX TEMP_PTR
        ADD16 TEMP_PTR+1, TEMP_PTR, CELL_OFFSET_LO, CELL_OFFSET_HI
        LDX TEMP_PTR
        RTS

CLEAR_NEXT_WALL:
        STAA TMP_MASK
        LDX #NEXT_CELL_POS
        JSR LOAD_CELL_PTR
        LDAA TMP_MASK
        COMA
        STAA TMP_MASK
        LDAA 0,X
        ANDA TMP_MASK
        STAA 0,X
        RTS



; --- 文字マップ操作 ----------------------------------------------------

CARVE_CUR_CELL:
        LDX #CUR_CELL_POS
        JSR BUILD_CHAR_POINTER
        JSR WRITE_SPACE_AT_PTR
        RTS

CARVE_PASSAGE:
        LDX #CUR_CELL_POS
        JSR BUILD_CHAR_POINTER
        LDAA ROW_INDEX
        STAA CHAR_OFFSET_LO
        LDAA COL_INDEX
        STAA CHAR_OFFSET_HI      ; 一時退避に利用
        LDAA TMP_CHOICE
        CMPA #DIR_N
        BEQ PASSAGE_N
        CMPA #DIR_E
        BEQ PASSAGE_E
        CMPA #DIR_S
        BEQ PASSAGE_S
        ; DIR_W
        LDAA CHAR_OFFSET_HI
        DECA
        STAA CHAR_OFFSET_HI
        BRA PASSAGE_COMMON
PASSAGE_N:
        LDAA CHAR_OFFSET_LO
        DECA
        STAA CHAR_OFFSET_LO
        BRA PASSAGE_COMMON
PASSAGE_E:
        LDAA CHAR_OFFSET_HI
        INCA
        STAA CHAR_OFFSET_HI
        BRA PASSAGE_COMMON
PASSAGE_S:
        LDAA CHAR_OFFSET_LO
        INCA
        STAA CHAR_OFFSET_LO

PASSAGE_COMMON:
        LDAA CHAR_OFFSET_LO
        STAA ROW_INDEX
        LDAA CHAR_OFFSET_HI
        STAA COL_INDEX
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
        STAA COL_INDEX
        LDAA 1,X
        ASLA
        INCA
        STAA ROW_INDEX
        JSR BUILD_CHAR_FROM_RC
        RTS

BUILD_CHAR_FROM_RC:
        ; 行・列からマップ先頭へのオフセット（row * width + col）を算出する。
        CLRA
        STAA CHAR_OFFSET_LO
        STAA CHAR_OFFSET_HI
        LDAA ROW_INDEX
        BEQ BCR_ROW_DONE
        STAA TEMP_SHIFT
BCR_ROW_LOOP:
        LDAA CHAR_OFFSET_LO
        ADDA CUR_CHAR_W
        STAA CHAR_OFFSET_LO
        LDAA CHAR_OFFSET_HI
        ADCA #0
        STAA CHAR_OFFSET_HI
        DEC TEMP_SHIFT
        BNE BCR_ROW_LOOP
BCR_ROW_DONE:
        LDAA COL_INDEX
        ADDA CHAR_OFFSET_LO
        STAA CHAR_OFFSET_LO
        LDAA CHAR_OFFSET_HI
        ADCA #0
        STAA CHAR_OFFSET_HI
        ; MAZE_MAP 基準アドレスにオフセットを加算して最終ポインタを得る。
        LDX #MAZE_MAP
        STX TEMP_PTR
        CLC
        LDAA TEMP_PTR+1
        ADDA CHAR_OFFSET_LO
        STAA TEMP_PTR+1
        LDAA TEMP_PTR
        ADCA CHAR_OFFSET_HI
        STAA TEMP_PTR
        RTS

; プリセットマップにスタート・ゴールの空間を確保する。
MAZE_OPEN_START_GOAL:
        LDAA #PLAYER_START_Y
        STAA ROW_INDEX
        LDAA #PLAYER_START_X
        STAA COL_INDEX
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX TEMP_PTR
        LDAA #' '
        STAA ,X

        LDAA GOAL_Y_CUR
        STAA ROW_INDEX
        LDAA GOAL_X_CUR
        STAA COL_INDEX
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX TEMP_PTR
        LDAA #'G'
        STAA ,X
        RTS

WRITE_SPACE_AT_PTR:
        LDX TEMP_PTR
        LDAA #' '
        STAA 0,X
        RTS


; --- オフセット計算 -----------------------------------------------------

BUILD_CELL_OFFSET:
        CLRA
        STAA CELL_OFFSET_LO
        STAA CELL_OFFSET_HI
        LDAA 1,X
        BEQ CELL_ROW_DONE
        STAA TEMP_SHIFT
CELL_ROW_LOOP:
        LDAA CELL_OFFSET_LO
        ADDA CUR_CELL_W
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


; --- エントリ -----------------------------------------------------------

MAZE_GENERATE:
        JSR MAZE_INIT
        JSR STACK_RESET

        ; 開始セルを (0,0) に設定し、訪問済みとしてマークする。
        CLRA
        STAA CUR_CELL_POS
        STAA CUR_CELL_POS+1
        JSR MARK_CUR_VISITED
        JSR CARVE_CUR_CELL
        JSR STACK_PUSH_CUR

MG_GROW_LOOP:
        JSR FIND_NEIGHBORS
        LDAA TMP_DIR_COUNT
        BEQ MG_BACKTRACK
        JSR CHOOSE_AND_ADVANCE
        LDAA NEXT_CELL_POS
        STAA CUR_CELL_POS
        LDAA NEXT_CELL_POS+1
        STAA CUR_CELL_POS+1
        JSR MARK_CUR_VISITED
        JSR CARVE_CUR_CELL
        BRA MG_GROW_LOOP

MG_BACKTRACK:
        JSR STACK_POP_TO_CUR
        BCS MG_DONE
        JSR MARK_CUR_VISITED
        JSR CARVE_CUR_CELL
        BRA MG_GROW_LOOP

MG_DONE:
        JSR MAZE_OPEN_START_GOAL
        RTS

; タイトルメニューを表示し、レベル選択を行う。
MAZE_TITLE_MENU:
        CLR_VRAM
        CLRA
        STAA MENU_BLINK_COUNT
        LDAA #1
        STAA MENU_BLINK_STATE
        STAA MENU_WAIT_RELEASE
        STAA MENU_LAST_INPUT
        LDAA #1
        STAA MENU_REDRAW
        STAA MENU_HILITE_DIRTY
MTM_LOOP:
        JSR MAZE_MENU_DRAW
        JSR WAIT_2MS
        JSR MAZE_MENU_POLL
        BEQ MTM_LOOP
        RTS

; メニュー描画のメインルーチン。必要に応じて静的要素やハイライトを更新する。
MAZE_MENU_DRAW:
        LDAA MENU_REDRAW
        BEQ MMD_SKIP_STATIC
        JSR MAZE_MENU_DRAW_STATIC
        CLRA
        STAA MENU_REDRAW
        LDAA #1
        STAA MENU_HILITE_DIRTY
MMD_SKIP_STATIC:
        LDAA MENU_BLINK_COUNT
        INCA
        STAA MENU_BLINK_COUNT
        CMPA #MENU_BLINK_PERIOD
        BCC MMD_CHECK_HILITE
        CLRA
        STAA MENU_BLINK_COUNT
        LDAA MENU_BLINK_STATE
        EORA #1
        STAA MENU_BLINK_STATE
        LDAA #1
        STAA MENU_HILITE_DIRTY
MMD_CHECK_HILITE:
        LDAA MENU_HILITE_DIRTY
        BEQ MMD_DONE
        JSR MAZE_MENU_DRAW_OPTIONS
        CLRA
        STAA MENU_HILITE_DIRTY
MMD_DONE:
        RTS

MAZE_MENU_DRAW_STATIC:
        ; タイトル行
        LDAA #MENU_ROW_TITLE1
        JSR MAZE_MENU_ROW_PTR
        STX STD_VRAM_PTR
        LDX #MENU_TITLE_LINE1
        JSR __STD_PRINT_STR

        LDAA #MENU_ROW_TITLE2
        JSR MAZE_MENU_ROW_PTR
        STX STD_VRAM_PTR
        LDX #MENU_TITLE_LINE2
        JSR __STD_PRINT_STR

        LDAA #MENU_ROW_FOOTER
        JSR MAZE_MENU_ROW_PTR
        STX STD_VRAM_PTR
        LDX #MENU_FOOTER
        JSR __STD_PRINT_STR

        ; 選択肢は毎回描画する（ハイライト更新も同じ処理を使用）
        JSR MAZE_MENU_DRAW_OPTIONS
        RTS

MAZE_MENU_DRAW_OPTIONS:
        CLRA
        STAA TMP_CHOICE
MDO_LOOP:
        LDAA TMP_CHOICE
        CMPA #MENU_OPTION_COUNT
        BCS MDO_CONT
        RTS
MDO_CONT:
        JSR MAZE_MENU_DRAW_OPTION
        LDAA TMP_CHOICE
        INCA
        STAA TMP_CHOICE
        BRA MDO_LOOP

; index (TMP_CHOICE) で指定された選択肢を描画し、ハイライト状態を反映する。
MAZE_MENU_DRAW_OPTION:
        LDAA TMP_CHOICE
        BEQ MDO_OPTION_EASY
        CMPA #1
        BEQ MDO_OPTION_NORMAL
        LDX #MENU_OPTION_HARD
        LDAA #8
        BRA MDO_OPTION_COMMON
MDO_OPTION_EASY:
        LDX #MENU_OPTION_EASY
        LDAA #6
        BRA MDO_OPTION_COMMON
MDO_OPTION_NORMAL:
        LDX #MENU_OPTION_NORMAL
        LDAA #7
MDO_OPTION_COMMON:
        STX SCR_PTR_SRC
        STAA ROW_INDEX
        LDAA ROW_INDEX
        JSR MAZE_MENU_ROW_PTR
        STX SCR_PTR_DST
        STX STD_VRAM_PTR
        LDAA #MENU_COL_OPTION
        JSR MAZE_MENU_ADVANCE_COL

        LDX SCR_PTR_SRC
        JSR __STD_PRINT_STR

        LDAA MENU_SELECTED
        CMPA TMP_CHOICE
        BNE MDO_CLEAR
        LDAA MENU_BLINK_STATE
        BEQ MDO_CLEAR
        JSR MAZE_MENU_INVERT_LINE
        RTS
MDO_CLEAR:
        JSR MAZE_MENU_CLEAR_LINE
        RTS

; A=行番号を受け取り、X に VRAM 上の先頭アドレスを返す。
MAZE_MENU_ROW_PTR:
        STAA CHAR_OFFSET_LO
        CLRA
        STAA CHAR_OFFSET_HI
        LDAA #5
        STAA TEMP_SHIFT
MMRP_SHIFT:
        LDAA TEMP_SHIFT
        BEQ MMRP_ADD
        ASL CHAR_OFFSET_LO
        ROL CHAR_OFFSET_HI
        DEC TEMP_SHIFT
        BRA MMRP_SHIFT
MMRP_ADD:
        LDX #STD_VRAM_BASE
        STX TEMP_PTR
        ADD16 TEMP_PTR+1, TEMP_PTR, CHAR_OFFSET_LO, CHAR_OFFSET_HI
        LDX TEMP_PTR
        RTS

; 行開始位置から指定列数だけ進める。
MAZE_MENU_ADVANCE_COL:
        STAA TEMP_SHIFT
        LDX SCR_PTR_DST
MMAC_LOOP:
        LDAA TEMP_SHIFT
        BEQ MMAC_STORE
        INX
        DEC TEMP_SHIFT
        BRA MMAC_LOOP
MMAC_STORE:
        STX SCR_PTR_DST
        STX STD_VRAM_PTR
        RTS

; 文字列長に合わせて反転表示をクリアする。
MAZE_MENU_CLEAR_LINE:
        LDX SCR_PTR_SRC
MMCL_LOOP:
        LDAA ,X
        BEQ MMCL_DONE
        INX
        STX SCR_PTR_SRC
        LDX SCR_PTR_DST
        LDAA ,X
        ANDA #$7F
        STAA ,X
        INX
        STX SCR_PTR_DST
        BRA MMCL_LOOP
MMCL_DONE:
        RTS

; 文字列長に合わせて反転表示をセットする。
MAZE_MENU_INVERT_LINE:
        LDX SCR_PTR_SRC
MMINV_LOOP:
        LDAA ,X
        BEQ MMINV_DONE
        INX
        STX SCR_PTR_SRC
        LDX SCR_PTR_DST
        LDAA ,X
        ORAA #$80
        STAA ,X
        INX
        STX SCR_PTR_DST
        BRA MMINV_LOOP
MMINV_DONE:
        RTS

; メニュー入力を処理し、A=1 でゲーム開始を通知する。0 の場合は継続。
MAZE_MENU_POLL:
        JSR MAZE_READ_KEYS
        STAA MENU_LAST_INPUT
        LDAA MENU_WAIT_RELEASE
        BEQ MMP_READY
        LDAA MENU_LAST_INPUT
        BEQ MMP_RELEASED
        CLRA
        RTS
MMP_RELEASED:
        CLRA
        STAA MENU_WAIT_RELEASE
        STAA MENU_LAST_INPUT
        CLRA
        RTS
MMP_READY:
        LDAA MENU_LAST_INPUT
        BEQ MMP_NONE
        BITA #KEY_FLAG_UP
        BEQ MMP_CHECK_DOWN
        JSR MAZE_MENU_SELECT_UP
        LDAA #1
        STAA MENU_WAIT_RELEASE
        CLRA
        RTS
MMP_CHECK_DOWN:
        LDAA MENU_LAST_INPUT
        BITA #KEY_FLAG_DOWN
        BEQ MMP_CHECK_START
        JSR MAZE_MENU_SELECT_DOWN
        LDAA #1
        STAA MENU_WAIT_RELEASE
        CLRA
        RTS
MMP_CHECK_START:
        LDAA MENU_LAST_INPUT
        BITA #KEY_FLAG_ACTION
        BEQ MMP_NONE
        LDAA MENU_SELECTED
        JSR MAZE_APPLY_LEVEL
        LDAA #1
        STAA MENU_WAIT_RELEASE
        LDAA #1
        RTS
MMP_NONE:
        CLRA
        RTS

MAZE_MENU_SELECT_UP:
        LDAA MENU_SELECTED
        BEQ MMSU_WRAP
        DECA
        BRA MMSU_STORE
MMSU_WRAP:
        LDAA #MENU_OPTION_COUNT - 1
MMSU_STORE:
        STAA MENU_SELECTED
        CLRA
        STAA MENU_BLINK_COUNT
        LDAA #1
        STAA MENU_BLINK_STATE
        STAA MENU_HILITE_DIRTY
        RTS

MAZE_MENU_SELECT_DOWN:
        LDAA MENU_SELECTED
        INCA
        CMPA #MENU_OPTION_COUNT
        BCS MMSD_STORE
        LDAA #0
MMSD_STORE:
        STAA MENU_SELECTED
        CLRA
        STAA MENU_BLINK_COUNT
        LDAA #1
        STAA MENU_BLINK_STATE
        STAA MENU_HILITE_DIRTY
        RTS

; 選択されたレベルに応じてランタイムパラメータを更新する。
MAZE_APPLY_LEVEL:
        STAA CURRENT_LEVEL_INDEX
        LDX #MAZE_LEVEL_PARAMS
        LDAA CURRENT_LEVEL_INDEX
        BEQ MAL_READ
MAL_OFFSET_LOOP:
        INX
        INX
        INX
        INX
        INX
        DECA
        BNE MAL_OFFSET_LOOP
MAL_READ:
        LDAA 0,X
        STAA CUR_CHAR_W
        LDAA 1,X
        STAA CUR_CHAR_H
        LDAA 2,X
        STAA VIEW_CHAR_W
        LDAA 3,X
        STAA VIEW_CHAR_H
        LDAA 4,X
        STAA SCROLL_MARGIN_CUR

        ; セル数 = (幅 - 1) / 2
        LDAA CUR_CHAR_W
        DECA
        LSRA
        STAA CUR_CELL_W
        LDAA CUR_CHAR_H
        DECA
        LSRA
        STAA CUR_CELL_H

        ; マップ総バイト数
        CLRA
        STAA CUR_MAP_SIZE
        STAA CUR_MAP_SIZE+1
        LDAA CUR_CHAR_H
        STAA TMP_MASK
MAL_MAPSIZE_LOOP:
        LDAA TMP_MASK
        BEQ MAL_MAPSIZE_DONE
        DEC TMP_MASK
        LDAA CUR_MAP_SIZE+1
        ADDA CUR_CHAR_W
        STAA CUR_MAP_SIZE+1
        LDAA CUR_MAP_SIZE
        ADCA #0
        STAA CUR_MAP_SIZE
        BRA MAL_MAPSIZE_LOOP
MAL_MAPSIZE_DONE:

        ; セル総数
        CLRA
        STAA CUR_CELL_COUNT
        STAA CUR_CELL_COUNT+1
        LDAA CUR_CELL_H
        STAA TMP_MASK
MAL_CELLCOUNT_LOOP:
        LDAA TMP_MASK
        BEQ MAL_CELLCOUNT_DONE
        DEC TMP_MASK
        LDAA CUR_CELL_COUNT+1
        ADDA CUR_CELL_W
        STAA CUR_CELL_COUNT+1
        LDAA CUR_CELL_COUNT
        ADCA #0
        STAA CUR_CELL_COUNT
        BRA MAL_CELLCOUNT_LOOP
MAL_CELLCOUNT_DONE:

        ; セル最大インデックス
        LDAA CUR_CELL_W
        BEQ MAL_CELLX_ZERO
        DECA
        BRA MAL_CELLX_STORE
MAL_CELLX_ZERO:
        CLRA
MAL_CELLX_STORE:
        STAA CUR_CELL_MAX_X
        LDAA CUR_CELL_H
        BEQ MAL_CELLY_ZERO
        DECA
        BRA MAL_CELLY_STORE
MAL_CELLY_ZERO:
        CLRA
MAL_CELLY_STORE:
        STAA CUR_CELL_MAX_Y

        ; マップ最大インデックスとゴール座標
        LDAA CUR_CHAR_W
        DECA
        STAA CUR_CHAR_MAX_X
        DECA
        STAA GOAL_X_CUR
        LDAA CUR_CHAR_H
        DECA
        STAA CUR_CHAR_MAX_Y
        DECA
        STAA GOAL_Y_CUR

        ; ビュー半径
        LDAA VIEW_CHAR_W
        LSRA
        STAA VIEW_HALF_W
        LDAA VIEW_CHAR_H
        LSRA
        STAA VIEW_HALF_H

        ; スクロール制御値
        LDAA CUR_CHAR_W
        SUBA VIEW_CHAR_W
        BPL MAL_STORE_MAX_X
        CLRA
MAL_STORE_MAX_X:
        STAA MAX_VIEW_X_CUR
        LDAA CUR_CHAR_H
        SUBA VIEW_CHAR_H
        BPL MAL_STORE_MAX_Y
        CLRA
MAL_STORE_MAX_Y:
        STAA MAX_VIEW_Y_CUR

        LDAA VIEW_CHAR_W
        DECA
        SUBA SCROLL_MARGIN_CUR
        BPL MAL_STORE_RIGHT
        CLRA
MAL_STORE_RIGHT:
        STAA SCROLL_RIGHT_BOUND_CUR
        LDAA VIEW_CHAR_H
        DECA
        SUBA SCROLL_MARGIN_CUR
        BPL MAL_STORE_BOTTOM
        CLRA
MAL_STORE_BOTTOM:
        STAA SCROLL_BOTTOM_BOUND_CUR

        ; ゴール行はマップ高さ - 2 に設定済み
        RTS

; ゲーム本体。生成→プレイ→リスタートのループを回す。
MAZE_MAIN:
        JSR MAZE_TITLE_MENU
MAZE_GAME_RESTART:
        JSR MAZE_GENERATE
MAZE_GAME_LOOP:
        JSR MAZE_RUN
        CMPA #MAZE_EXIT_TITLE
        BEQ MAZE_MAIN
        CMPA #MAZE_EXIT_RESTART
        BEQ MAZE_GAME_RESTART
        BRA MAZE_GAME_LOOP


; --- ランタイム初期化・描画 --------------------------------------------

; プレイヤー位置やカウンタ、入力設定を初期化する。
MAZE_INIT_STATE:
        LDAA #PLAYER_START_X
        STAA PLAYER_X
        LDAA #PLAYER_START_Y
        STAA PLAYER_Y
        CLRA
        STAA STATUS_FLAGS
        STAA INPUT_FLAGS
        STAA MOVE_COUNT_LO
        STAA MOVE_COUNT_HI
        JSR MAZE_CONFIGURE_INPUT
        JSR MAZE_CENTER_VIEW
        JSR MAZE_FORMAT_STEPS
        RTS

; VIA ポートをキーボード読み取り用に初期化する。
MAZE_CONFIGURE_INPUT:
        LDAA #$0F
        STAA STD_VIA_DDRA
        CLRA
        STAA STD_VIA_DDRB
        STAA STD_VIA_ORA
        RTS

; プレイヤーを画面中央に近づけるようビュー原点を調整する。
MAZE_CENTER_VIEW:
        LDAA PLAYER_X
        SUBA VIEW_HALF_W
        BPL MVX_CLAMP
        CLRA
MVX_CLAMP:
        CMPA MAX_VIEW_X_CUR
        BLS MVX_STORE
        LDAA MAX_VIEW_X_CUR
MVX_STORE:
        STAA VIEW_ORIGIN_X
        STAA TARGET_VIEW_X
        LDAA PLAYER_Y
        SUBA VIEW_HALF_H
        BPL MVY_CLAMP
        CLRA
MVY_CLAMP:
        CMPA MAX_VIEW_Y_CUR
        BLS MVY_STORE
        LDAA MAX_VIEW_Y_CUR
MVY_STORE:
        STAA VIEW_ORIGIN_Y
        STAA TARGET_VIEW_Y
        JSR MAZE_UPDATE_PLAYER_DRAW
        RTS

MAZE_UPDATE_PLAYER_DRAW:
        LDAA PLAYER_X
        SUBA VIEW_ORIGIN_X
        BPL MUPD_STORE_X
        CLRA
MUPD_STORE_X:
        STAA PLAYER_DRAW_X
        LDAA PLAYER_Y
        SUBA VIEW_ORIGIN_Y
        BPL MUPD_STORE_Y
        CLRA
MUPD_STORE_Y:
        STAA PLAYER_DRAW_Y
        RTS

; 現在のビュー原点から 11x11 の地形を VRAM に転写する。
MAZE_RENDER_VIEW:
        LDAA #0
        STAA ROW_INDEX
        LDX #STD_VRAM_BASE
        STX SCR_PTR_DST
MAZE_ROW_LOOP:
        LDAA ROW_INDEX
        CMPA VIEW_CHAR_H
        BNE MAZE_ROW_PROCESS
        RTS
MAZE_ROW_PROCESS:
        LDAA ROW_INDEX
        STAA TMP_MASK
        LDAA VIEW_ORIGIN_Y
        ADDA TMP_MASK
        STAA ROW_INDEX
        LDAA VIEW_ORIGIN_X
        STAA COL_INDEX
        JSR BUILD_CHAR_FROM_RC
        LDX TEMP_PTR
        STX SCR_PTR_SRC
        LDAA TMP_MASK
        STAA ROW_INDEX
        ; dest offset for row (32 chars width => <<5)
        LDAA ROW_INDEX
        STAA CHAR_OFFSET_LO
        CLRA
        STAA CHAR_OFFSET_HI
        LDAA #5
        STAA TEMP_SHIFT
MAZE_DEST_SHIFT:
        LDAA TEMP_SHIFT
        BEQ MAZE_DEST_SHIFT_DONE
        ASL CHAR_OFFSET_LO
        ROL CHAR_OFFSET_HI
        DEC TEMP_SHIFT
        BRA MAZE_DEST_SHIFT
MAZE_DEST_SHIFT_DONE:
        LDX #STD_VRAM_BASE
        STX SCR_PTR_DST
        ADD16 SCR_PTR_DST+1, SCR_PTR_DST, CHAR_OFFSET_LO, CHAR_OFFSET_HI
        LDAA #0
        STAA COL_INDEX
MAZE_COL_LOOP:
        LDAA COL_INDEX
        CMPA VIEW_CHAR_W
        BEQ MAZE_NEXT_ROW
        LDX SCR_PTR_SRC
        LDAA ,X
        INX
        STX SCR_PTR_SRC
        CMPA #'#'
        BEQ MAZE_STORE_HASH
        CMPA #'G'
        BEQ MAZE_STORE_GOAL
        LDAA #$40
        BRA MAZE_STORE_CHAR
MAZE_STORE_HASH:
        LDAA #$03
        BRA MAZE_STORE_CHAR
MAZE_STORE_GOAL:
        JSR __STD_TO_VRAM
MAZE_STORE_CHAR:
        LDX SCR_PTR_DST
        STAA ,X
        INX
        STX SCR_PTR_DST
        INC COL_INDEX
        BRA MAZE_COL_LOOP
MAZE_NEXT_ROW:
        INC ROW_INDEX
        JMP MAZE_ROW_LOOP

; プレイヤーの見かけ位置を算出して VRAM 上に '@' を描画する。
MAZE_DRAW_PLAYER:
        LDAA PLAYER_DRAW_Y
        STAA ROW_INDEX
        LDAA PLAYER_DRAW_X
        STAA COL_INDEX
        JSR MAZE_VRAM_PTR_FROM_RC
        LDX TEMP_PTR
        LDAA #PLAYER_GLYPH
        JSR __STD_TO_VRAM
        STAA ,X
        RTS

; ROW_INDEX / COL_INDEX から計算した VRAM ポインタを TEMP_PTR に格納する。
MAZE_VRAM_PTR_FROM_RC:
        LDAA ROW_INDEX
        STAA CHAR_OFFSET_LO
        CLRA
        STAA CHAR_OFFSET_HI
        LDAA #5
        STAA TEMP_SHIFT
MVP_SHIFT:
        LDAA TEMP_SHIFT
        BEQ MVP_SHIFT_DONE
        ASL CHAR_OFFSET_LO
        ROL CHAR_OFFSET_HI
        DEC TEMP_SHIFT
        BRA MVP_SHIFT
MVP_SHIFT_DONE:
        LDAA COL_INDEX
        ADDA CHAR_OFFSET_LO
        STAA CHAR_OFFSET_LO
        LDAA #0
        ADCA CHAR_OFFSET_HI
        STAA CHAR_OFFSET_HI
        LDX #STD_VRAM_BASE
        STX TEMP_PTR
        ADD16 TEMP_PTR+1, TEMP_PTR, CHAR_OFFSET_LO, CHAR_OFFSET_HI
        RTS

; 現在の入力状態を読み込み、フラグに反映する。
MAZE_POLL_INPUT:
        JSR MAZE_READ_KEYS
        STAA INPUT_FLAGS
        RTS

; キーボード行を順番にスキャンし、移動・アクションの各ビットを立てる。
MAZE_READ_KEYS:
        PSHB
        CLRB
        ; buttons (Z / X)
        CLRA
        STAA STD_VIA_ORA
        LDAA STD_VIA_ORB
        BITA #$04
        BNE MRK_AFTER_BTN
        ORAB #KEY_FLAG_ACTION
MRK_AFTER_BTN:
        ; up (I key)
        LDAA #5
        STAA STD_VIA_ORA
        LDAA STD_VIA_ORB
        BITA #$04
        BNE MRK_ROW6
        ORAB #KEY_FLAG_UP
MRK_ROW6:
        ; left / right (J / K)
        LDAA #6
        STAA STD_VIA_ORA
        LDAA STD_VIA_ORB
        BITA #$02
        BNE MRK_K
        ORAB #KEY_FLAG_LEFT
MRK_K:
        BITA #$04
        BNE MRK_ROW7
        ORAB #KEY_FLAG_RIGHT
MRK_ROW7:
        ; down (M)
        LDAA #7
        STAA STD_VIA_ORA
        LDAA STD_VIA_ORB
        BITA #$08
        BNE MRK_DONE_SCAN
        ORAB #KEY_FLAG_DOWN
MRK_DONE_SCAN:
        CLRA
        STAA STD_VIA_ORA
        TBA
        PULB
        RTS

; 1 回のゲームサイクルを実行するメインループ。
MAZE_RUN:
MAZE_RUN_START:
        JSR MAZE_INIT_STATE
        CLR_VRAM
        JSR MAZE_RENDER_VIEW
        JSR MAZE_DRAW_OVERLAY
        JSR MAZE_DRAW_PLAYER
MAZE_RUNTIME_LOOP:
        JSR MAZE_POLL_INPUT
        LDAA INPUT_FLAGS
        BEQ MAZE_RUNTIME_LOOP
        JSR MAZE_PROCESS_INPUT
        CMPA #MAZE_EXIT_CONTINUE
        BEQ MAZE_RUNTIME_LOOP
        RTS

; 入力内容に応じてゲーム状態を更新する。ゴール後は再スタート待ちのみ。
MAZE_PROCESS_INPUT:
        LDAA STATUS_FLAGS
        BITA #STATUS_GOAL_FLAG
        BEQ MPI_HANDLE_MOVE
        LDAA #MAZE_EXIT_TITLE
        RTS
MPI_HANDLE_MOVE:
        JSR MAZE_HANDLE_MOVEMENT
        RTS

; 移動キーに従って座標を更新し、スクロールや描画を行う。
MAZE_HANDLE_MOVEMENT:
        LDAA INPUT_FLAGS
        BITA #KEY_FLAG_UP
        BEQ MHM_CHECK_DOWN
        LDAA PLAYER_Y
        BEQ MHM_CHECK_DOWN
        DECA
        STAA ROW_INDEX
        LDAA PLAYER_X
        STAA COL_INDEX
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX TEMP_PTR
        LDAA ,X
        CMPA #' '
        BEQ MHM_PASS_UP
        CMPA #'G'
        BNE MHM_CHECK_DOWN
MHM_PASS_UP:
        LDAA ROW_INDEX
        STAA PLAYER_Y
        JMP MHM_MOVED
MHM_CHECK_DOWN:
        LDAA INPUT_FLAGS
        BITA #KEY_FLAG_DOWN
        BEQ MHM_CHECK_LEFT
        LDAA PLAYER_Y
        CMPA CUR_CHAR_MAX_Y
        BCC MHM_CHECK_LEFT
        INCA
        STAA ROW_INDEX
        LDAA PLAYER_X
        STAA COL_INDEX
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX TEMP_PTR
        LDAA ,X
        CMPA #' '
        BEQ MHM_PASS_DOWN
        CMPA #'G'
        BNE MHM_CHECK_LEFT
MHM_PASS_DOWN:
        LDAA ROW_INDEX
        STAA PLAYER_Y
        JMP MHM_MOVED
MHM_CHECK_LEFT:
        LDAA INPUT_FLAGS
        BITA #KEY_FLAG_LEFT
        BEQ MHM_CHECK_RIGHT
        LDAA PLAYER_X
        BEQ MHM_CHECK_RIGHT
        DECA
        STAA COL_INDEX
        LDAA PLAYER_Y
        STAA ROW_INDEX
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX TEMP_PTR
        LDAA ,X
        CMPA #' '
        BEQ MHM_PASS_LEFT
        CMPA #'G'
        BNE MHM_CHECK_RIGHT
MHM_PASS_LEFT:
        LDAA COL_INDEX
        STAA PLAYER_X
        JMP MHM_MOVED
MHM_CHECK_RIGHT:
        LDAA INPUT_FLAGS
        BITA #KEY_FLAG_RIGHT
        BEQ MHM_NO_MOVE
        LDAA PLAYER_X
        CMPA CUR_CHAR_MAX_X
        BCC MHM_NO_MOVE
        INCA
        STAA COL_INDEX
        LDAA PLAYER_Y
        STAA ROW_INDEX
        JSR MAZE_MAP_PTR_FROM_COORD
        LDX TEMP_PTR
        LDAA ,X
        CMPA #' '
        BEQ MHM_PASS_RIGHT
        CMPA #'G'
        BNE MHM_NO_MOVE
MHM_PASS_RIGHT:
        LDAA COL_INDEX
        STAA PLAYER_X
MHM_MOVED:
        JSR MAZE_INCREMENT_STEPS
        JSR MAZE_SCROLL_TO_PLAYER
        JSR MAZE_RENDER_VIEW
        JSR MAZE_DRAW_OVERLAY
        JSR MAZE_DRAW_PLAYER
        JSR MAZE_CHECK_GOAL
        TSTA
        BNE MHM_EXIT
        CLRA
        RTS
MHM_EXIT:
        RTS
MHM_NO_MOVE:
        CLRA
        RTS

; プレイヤーがゴール座標に到達したか判定する。
MAZE_CHECK_GOAL:
        LDAA PLAYER_X
        CMPA GOAL_X_CUR
        BNE MCG_NO_GOAL
        LDAA PLAYER_Y
        CMPA GOAL_Y_CUR
        BNE MCG_NO_GOAL
        LDAA STATUS_FLAGS
        BITA #STATUS_GOAL_FLAG
        BNE MCG_SIGNAL_EXIT
        ORAA #STATUS_GOAL_FLAG
        STAA STATUS_FLAGS
        JSR MAZE_DISPLAY_GOAL_MESSAGE
MCG_SIGNAL_EXIT:
        LDAA #MAZE_EXIT_TITLE
        RTS
MCG_NO_GOAL:
        CLRA
        RTS

MAZE_MAP_PTR_FROM_COORD:
        JSR BUILD_CHAR_FROM_RC
        RTS

; プレイヤーが表示領域の端に近づいた際にビュー原点を滑らかに移動する。
MAZE_SCROLL_TO_PLAYER:
        STD_SCROLL_UPDATE VIEW_ORIGIN_X, VIEW_ORIGIN_Y, PLAYER_X, PLAYER_Y, SCROLL_MARGIN_CUR, SCROLL_RIGHT_BOUND_CUR, SCROLL_BOTTOM_BOUND_CUR, MAX_VIEW_X_CUR, MAX_VIEW_Y_CUR, PLAYER_DRAW_X, PLAYER_DRAW_Y
        RTS

; 画面下部にステップ数 (MOV) を描画する。
MAZE_DRAW_OVERLAY:
        JSR MAZE_FORMAT_STEPS
        ; bottom row pointer
        LDAA #HUD_ROW_INDEX
        STAA CHAR_OFFSET_LO
        CLRA
        STAA CHAR_OFFSET_HI
        LDAA #5
        STAA TEMP_SHIFT
MDO_SHIFT:
        LDAA TEMP_SHIFT
        BEQ MDO_ADD
        ASL CHAR_OFFSET_LO
        ROL CHAR_OFFSET_HI
        DEC TEMP_SHIFT
        BRA MDO_SHIFT
MDO_ADD:
        LDX #STD_VRAM_BASE
        STX TEMP_PTR
        ADD16 TEMP_PTR+1, TEMP_PTR, CHAR_OFFSET_LO, CHAR_OFFSET_HI
        LDX TEMP_PTR
        PRINT_STR HUD_STEPS_BUF
        RTS

; ゴール到達時にメッセージを表示し、約3秒待機する。
MAZE_DISPLAY_GOAL_MESSAGE:
        LDAA #GOAL_MSG_ROW
        DECA
        STAA ROW_INDEX
        LDAA #GOAL_MSG_COL
        STAA COL_INDEX
        JSR MAZE_VRAM_PTR_FROM_RC
        LDX TEMP_PTR
        STX STD_VRAM_PTR
        LDX #GOAL_MSG_PAD
        JSR __STD_PRINT_STR

        LDAA #GOAL_MSG_ROW
        STAA ROW_INDEX
        LDAA #GOAL_MSG_COL
        STAA COL_INDEX
        JSR MAZE_VRAM_PTR_FROM_RC
        LDX TEMP_PTR
        STX STD_VRAM_PTR
        LDX #GOAL_MESSAGE
        JSR __STD_PRINT_STR

        LDAA #GOAL_MSG_ROW
        INCA
        STAA ROW_INDEX
        LDAA #GOAL_MSG_COL
        STAA COL_INDEX
        JSR MAZE_VRAM_PTR_FROM_RC
        LDX TEMP_PTR
        STX STD_VRAM_PTR
        LDX #GOAL_MSG_PAD
        JSR __STD_PRINT_STR
        JSR MAZE_WAIT_GOAL_DELAY
        RTS

MAZE_WAIT_GOAL_DELAY:
        LDAA #2
        STAA TMP_MASK
MWGD_OUTER:
        LDAB #200
MWGD_INNER:
        JSR WAIT_2MS
        DECB
        BNE MWGD_INNER
        DEC TMP_MASK
        BNE MWGD_OUTER
        RTS

; 1 歩進むたびにステップカウンタを BCD で加算する。
MAZE_INCREMENT_STEPS:
        LDAA MOVE_COUNT_LO
        ADDA #$01
        DAA
        STAA MOVE_COUNT_LO
        BCC MFSK_UPDATE
        LDAA MOVE_COUNT_HI
        ADDA #$01
        DAA
        STAA MOVE_COUNT_HI
        BCC MFSK_UPDATE
        LDAA #$99
        STAA MOVE_COUNT_HI
        LDAA #$99
        STAA MOVE_COUNT_LO
MFSK_UPDATE:
        JSR MAZE_FORMAT_STEPS
        RTS

; BCD カウンタから ASCII 文字列 "MOV:0000" を生成する。
MAZE_FORMAT_STEPS:
        PSHB
        LDAA MOVE_COUNT_HI
        LSRA
        LSRA
        LSRA
        LSRA
        ANDA #$0F
        ADDA #'0'
        STAA HUD_STEPS_BUF + 4

        LDAA MOVE_COUNT_HI
        ANDA #$0F
        ADDA #'0'
        STAA HUD_STEPS_BUF + 5

        LDAA MOVE_COUNT_LO
        LSRA
        LSRA
        LSRA
        LSRA
        ANDA #$0F
        ADDA #'0'
        STAA HUD_STEPS_BUF + 6

        LDAA MOVE_COUNT_LO
        ANDA #$0F
        ADDA #'0'
        STAA HUD_STEPS_BUF + 7
        PULB
        RTS

; 約2ms待機 (CPUクロック 0.894MHz を前提とした概算)。
WAIT_2MS:
        LDX #$0190              ; 400 ループ ≒ 0.5 秒 / 250 カウント
W2_LOOP:
        NOP
        NOP
        NOP
        NOP
        DEX
        BNE W2_LOOP
        RTS

        .data
HUD_STEPS_BUF:
        .byte $4D,$4F,$56,$3A,$30,$30,$30,$30,$00
        .code
