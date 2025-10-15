; 迷路生成とプレイヤー移動で共有する方向ベクトルやフラグ定義。
DIR_COUNT:      .equ 4
DIR_N:          .equ 0
DIR_E:          .equ 1
DIR_S:          .equ 2
DIR_W:          .equ 3

DIR_BIT_N:      .equ $01
DIR_BIT_E:      .equ $02
DIR_BIT_S:      .equ $04
DIR_BIT_W:      .equ $08

WALL_N:         .equ $08
WALL_E:         .equ $04
WALL_S:         .equ $02
WALL_W:         .equ $01

DX_TABLE:
        .byte 0, 1, 0, 255          ; DIR_N/E/S/W に対応する X 軸の変化量 (255 は -1)
DY_TABLE:
        .byte 255, 0, 1, 0          ; DIR_N/E/S/W に対応する Y 軸の変化量
OPPOSITE_TABLE:
        .byte DIR_S, DIR_W, DIR_N, DIR_E ; 逆方向を参照するためのテーブル
WALL_TABLE:
        .byte WALL_N, WALL_E, WALL_S, WALL_W ; 各方向に対応する壁ビット

DIR_BIT_TABLE:
        .byte DIR_BIT_N, DIR_BIT_E, DIR_BIT_S, DIR_BIT_W

CELL_VISITED_FLAG: .equ $10

STATUS_GOAL_FLAG: .equ $01

KEY_FLAG_UP:       .equ $01
KEY_FLAG_DOWN:     .equ $02
KEY_FLAG_LEFT:     .equ $04
KEY_FLAG_RIGHT:    .equ $08
KEY_FLAG_RESTART:  .equ $10
KEY_FLAG_ACTION:   .equ $20
KEY_FLAG_DIR:      .equ (KEY_FLAG_UP | KEY_FLAG_DOWN | KEY_FLAG_LEFT | KEY_FLAG_RIGHT) ; 方向キー判定用マスク
