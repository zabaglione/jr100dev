.org $0600


.include "common.inc"

DIR_N: .equ 0
DIR_E: .equ 1
DIR_S: .equ 2
DIR_W: .equ 3



; 迷路サンプルで使用するワーク領域とプリセット迷路データ。
; 生成アルゴリズムの過去資産を再利用しつつ、レベル選択によってマップサイズを切り替えられるようにする。

; ---- ランタイム設定値 -------------------------------------------------

CUR_CHAR_W:         .byte 11
CUR_CHAR_H:         .byte 11
CUR_CELL_W:         .byte 5
CUR_CELL_H:         .byte 5
CUR_MAP_SIZE:       .word 121
CUR_CELL_COUNT:     .word 25
CUR_CELL_MAX_X:     .byte 4
CUR_CELL_MAX_Y:     .byte 4

VIEW_TILE_W_CUR:    .byte MAZE_VIEW_TILE_W
VIEW_TILE_H_CUR:    .byte MAZE_VIEW_TILE_H
VIEW_CHAR_W_CUR:    .byte MAZE_VIEW_CHAR_W
VIEW_CHAR_H_CUR:    .byte MAZE_VIEW_CHAR_H
VIEW_HALF_TILE_W:   .byte 5
VIEW_HALF_TILE_H:   .byte 3
SCROLL_MARGIN_CUR:  .byte 1               ; タイル単位のマージン
SCROLL_RIGHT_BOUND_CUR: .byte 0
SCROLL_BOTTOM_BOUND_CUR: .byte 0
MAX_VIEW_X_CUR:     .byte 0
MAX_VIEW_Y_CUR:     .byte 0
GOAL_X_CUR:         .byte (11 - 2)
GOAL_Y_CUR:         .byte (11 - 2)
CUR_CHAR_MAX_X:     .byte (11 - 1)
CUR_CHAR_MAX_Y:     .byte (11 - 1)
CURRENT_LEVEL_INDEX:.byte 0

MENU_SELECTED:      .byte 0
MENU_BLINK_COUNT:   .byte 0
MENU_BLINK_STATE:   .byte 0
MENU_WAIT_RELEASE:  .byte 0
MENU_REDRAW:        .byte 1
MENU_LAST_INPUT:    .byte 0
MENU_HILITE_DIRTY:  .byte 1

; ---- 迷路データ領域 ---------------------------------------------------

MAZE_MAP:
        .fill MAZE_MAP_MAX_SIZE, $00

; セル情報・訪問状態・スタックはいずれも最大サイズ分を確保する。
MAZE_CELLS:
        .fill MAZE_CELL_MAX_COUNT, $0F

VISITED_MAP:
        .fill MAZE_CELL_MAX_COUNT, $00

STACK_BASE:
        .fill MAZE_CELL_MAX_COUNT * 2, $00

STACK_PTR:
        .word STACK_BASE

; ---- レベル定義／メニュー表示 -----------------------------------------

LEVEL_STRUCT_SIZE: .equ 5
LEVEL_COUNT:       .equ 3

; 各レベルの設定値: [マップ幅, マップ高さ, ビュー幅, ビュー高さ, スクロールマージン]
MAZE_LEVEL_PARAMS:
        .byte 11,11,1
        .byte 21,21,1
        .byte 41,41,2

LEVEL_ITEM_TABLE:
        ; EASY (11x11)
        .byte 2,2, 4,5, 7,3, 8,7, 3,8
        ; NORMAL (21x21)
        .byte 3,3, 10,4, 15,9, 6,15, 18,12
        ; HARD (41x41)
        .byte 5,5, 12,7, 20,12, 30,18, 34,27

LEVEL_ENEMY_TABLE:
        ; EASY: count + (x,y,dir)*4
        .byte 1, 5,5, DIR_E, 0,0,0, 0,0,0, 0,0,0
        ; NORMAL
        .byte 2, 8,10, DIR_N, 14,4, DIR_W, 0,0,0, 0,0,0
        ; HARD
        .byte 4, 6,6, DIR_E, 12,20, DIR_N, 25,10, DIR_W, 32,30, DIR_S

MENU_OPTION_COUNT: .equ 3

MENU_TITLE_LINE1: .ascii "          MAZE2 SAMPLE\0"
MENU_TITLE_LINE2: .ascii "        SELECT TO LEVEL\0"
MENU_FOOTER:      .ascii "      START TO [Z] KEY\0"


MENU_OPTION_EASY:   .ascii "EASY   (11 X 11)\0"
MENU_OPTION_NORMAL: .ascii "NORMAL (21 X 21)\0"
MENU_OPTION_HARD:   .ascii "HARD   (41 X 41)\0"

GOAL_MESSAGE:       .ascii "  G O A L ! ! !  \0"
GOAL_MSG_PAD:       .ascii "                 \0"

; プレイヤー位置と描画・入力に関する状態変数。
PLAYER_X:
        .byte PLAYER_START_X
PLAYER_Y:
        .byte PLAYER_START_Y
PLAYER_DIR:
        .byte PLAYER_DEFAULT_DIR

SCR_PTR_SRC:
        .word $0000
SCR_PTR_DST:
        .word $0000

VIEW_ORIGIN_X:
        .byte $00
VIEW_ORIGIN_Y:
        .byte $00
TARGET_VIEW_X:
        .byte $00
TARGET_VIEW_Y:
        .byte $00
PLAYER_DRAW_X:
        .byte $00
PLAYER_DRAW_Y:
        .byte $00
PLAYER_SCREEN_TILE_X:
        .byte $00
PLAYER_SCREEN_TILE_Y:
        .byte $00
STATUS_FLAGS:
        .byte $00
INPUT_FLAGS:
        .byte $00
MOVE_COUNT_LO:
        .byte $00
MOVE_COUNT_HI:
        .byte $00
TIME_REMAIN_LO:
        .byte $00
TIME_REMAIN_HI:
        .byte $00
ITEM_REMAIN_COUNT:
        .byte $00
TIME_TICK_LO:
        .byte $F4
TIME_TICK_HI:
        .byte $01
TIME_TICK_RESET_LO:
        .byte $F4
TIME_TICK_RESET_HI:
        .byte $01
TIME_TMP_LO:
        .byte $00

; アイテム／敵／弾丸の状態
ITEM_COLLECTED:
        .fill ITEM_COUNT, $00
ITEM_POSITIONS:
        .fill ITEM_COUNT * 2, $00       ; [X0,Y0,X1,Y1,...]

ENEMY_COUNT:
        .byte $00
ENEMY_ACTIVE:
        .fill ENEMY_MAX, $00
ENEMY_X:
        .fill ENEMY_MAX, $00
ENEMY_Y:
        .fill ENEMY_MAX, $00
ENEMY_DIR:
        .fill ENEMY_MAX, $00
ENEMY_TURN_DELAY:
        .fill ENEMY_MAX, $00
ENEMY_TARGET_DIR:
        .fill ENEMY_MAX, $00
ENEMY_CHASE_TIMER:
        .fill ENEMY_MAX, $00

BULLET_ACTIVE:
        .byte $00
BULLET_X:
        .byte $00
BULLET_Y:
        .byte $00
BULLET_DIR:
        .byte $00

DEBUG_NEXT_VISITED:
        .byte $00
DEBUG_DIR_COUNT:
        .byte $00
DEBUG_CHAR_PTR:
        .word $0000
DEBUG_ROW_VAL:
        .byte $00
DEBUG_COL_VAL:
        .byte $00
DEBUG_VISIT_PTR:
        .word $0000
DEBUG_VISIT_VAL:
        .byte $00

; 描画や探索で共有するワークレジスタ群。
TEMP_PTR:
        .word $0000
ROW_INDEX:
        .byte $00
COL_INDEX:
        .byte $00
TMP_DIR_COUNT:
        .byte $00
TMP_DIR_BUF:
        .fill 4, $00
TMP_CHOICE:
        .byte $00
TMP_DIR_MASK:
        .byte $00
CUR_CELL_POS:
        .word $0000
NEXT_CELL_POS:
        .word $0000
CELL_OFFSET_LO:
        .byte $00
CELL_OFFSET_HI:
        .byte $00
CHAR_OFFSET_LO:
        .byte $00
CHAR_OFFSET_HI:
        .byte $00
CHAR_ROW_BASE:
        .byte $00
CHAR_COL_BASE:
        .byte $00
TEMP_SHIFT:
        .byte $00
TMP_MASK:
        .byte $00
TILE_ROW_REL:
        .byte $00
TILE_COL_REL:
        .byte $00
SUBROW_INDEX:
        .byte $00
BULLET_DELAY:
        .byte $00
WORLD_ROW:
        .byte $00
WORLD_COL:
        .byte $00
RNG_SEED:
        .byte $5A

        .data
HUD_TIME_BUF:
        .byte $54,$49,$4D,$45,$3A,$30,$30,$30,$30,$00
HUD_ITEM_BUF:
        .byte $49,$54,$45,$4D,$3A,$30,$00
HUD_STEPS_BUF:
        .byte $4D,$4F,$56,$3A,$30,$30,$30,$30,$00
        .code
