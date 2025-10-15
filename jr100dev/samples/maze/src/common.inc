; Common constants for maze sample

; 最大マップサイズ（HARD レベルの 41×41）に合わせたメモリ確保を行う。
MAZE_CHAR_W_MAX:     .equ 41
MAZE_CHAR_H_MAX:     .equ 41
MAZE_CELL_W_MAX:     .equ 20
MAZE_CELL_H_MAX:     .equ 20
MAZE_CELL_MAX_COUNT: .equ 512

; 互換用のデフォルトサイズ（EASY レベル相当）。テストコードなどから参照される。
MAZE_CHAR_W:    .equ 11
MAZE_CHAR_H:    .equ 11
MAZE_CELL_W:    .equ 5
MAZE_CELL_H:    .equ 5
MAZE_CELL_COUNT: .equ (MAZE_CELL_W * MAZE_CELL_H)

MAZE_ORIGIN_X:  .equ 0
MAZE_ORIGIN_Y:  .equ 0
MAZE_MAP_ADDR:  .equ $0600
MAZE_MAP_MAX_SIZE: .equ 1681

STACK_BASE_ADDR: .equ MAZE_MAP_ADDR + MAZE_MAP_MAX_SIZE + (MAZE_CELL_MAX_COUNT * 2)
HUD_ROW_INDEX:  .equ 23

PLAYER_START_X: .equ 1
PLAYER_START_Y: .equ 1
PLAYER_GLYPH:   .equ '@'
