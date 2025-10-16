; MAZE2 共通定数

; ---- マップ基本情報 ---------------------------------------------------

MAZE_CHAR_W_MAX:     .equ 41
MAZE_CHAR_H_MAX:     .equ 41
MAZE_CELL_W_MAX:     .equ 20
MAZE_CELL_H_MAX:     .equ 20
MAZE_CELL_MAX_COUNT: .equ 512

MAZE_ORIGIN_X:       .equ 0
MAZE_ORIGIN_Y:       .equ 0
MAZE_MAP_ADDR:       .equ $0600
MAZE_MAP_MAX_SIZE:   .equ 1681

; ---- タイル／表示設定 -------------------------------------------------

MAZE_TILE_CHAR_W:    .equ 3          ; 1 タイル = 3x3 キャラクター
MAZE_TILE_CHAR_H:    .equ 3
MAZE_VIEW_TILE_W:    .equ 10         ; 表示タイル幅（30 文字）
MAZE_VIEW_TILE_H:    .equ 7          ; 表示タイル高さ（21 文字）
MAZE_VIEW_CHAR_W:    .equ (MAZE_TILE_CHAR_W * MAZE_VIEW_TILE_W)
MAZE_VIEW_CHAR_H:    .equ (MAZE_TILE_CHAR_H * MAZE_VIEW_TILE_H)
MAZE_VIEW_CHAR_X_OFF:.equ 1          ; 左右余白（VRAM カラム単位）
MAZE_VIEW_CHAR_Y_OFF:.equ 1
MAZE_TILE_CENTER_OFF:.equ 1

HUD_ROW_INDEX:       .equ 23
HUD_TIME_COL:       .equ 2
HUD_ITEM_COL:       .equ 16
HUD_STEP_COL:       .equ 28

; ---- ゲーム要素 -------------------------------------------------------

PLAYER_START_X:      .equ 1
PLAYER_START_Y:      .equ 1
PLAYER_GLYPH:        .equ '@'

ITEM_COUNT:          .equ 5
ITEM_PAIR_BYTES:     .equ (ITEM_COUNT * 2)
ENEMY_MAX:           .equ 4          ; ステージ同時出現上限
ENEMY_ENTRY_BYTES:   .equ 3
ENEMY_TABLE_STRIDE:  .equ (1 + ENEMY_MAX * ENEMY_ENTRY_BYTES)
BULLET_MAX:          .equ 1
LEVEL_TIME_LIMIT:    .equ 180        ; 秒
PLAYER_DEFAULT_DIR:  .equ 1          ; DIR_E

; ゴール表示演出位置（キャラクター座標）
GOAL_MSG_ROW:        .equ 11
GOAL_MSG_COL:        .equ 9
