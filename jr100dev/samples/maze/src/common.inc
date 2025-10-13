; Common constants for maze sample

MAZE_CHAR_W    .equ 128
MAZE_CHAR_H    .equ 96
MAZE_CELL_W    .equ 64
MAZE_CELL_H    .equ 48
MAZE_CELL_COUNT .equ (MAZE_CELL_W * MAZE_CELL_H)

MAZE_ORIGIN_X  .equ 0
MAZE_ORIGIN_Y  .equ 0

PLAYER_START_X .equ 1
PLAYER_START_Y .equ (MAZE_CHAR_H - 2)

GOAL_X         .equ (MAZE_CHAR_W - 2)
GOAL_Y         .equ 1
