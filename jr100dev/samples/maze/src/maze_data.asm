        .org MAZE_MAP

        .include "common.inc"

MAZE_MAP:
        .fill MAZE_CHAR_W * MAZE_CHAR_H, $00

MAZE_CELLS:
        .fill MAZE_CELL_W * MAZE_CELL_H, $0F ; walls(NESW) = 1

VISITED_MAP:
        .fill MAZE_CELL_W * MAZE_CELL_H, $00

STACK_X:
        .fill MAZE_CELL_W * MAZE_CELL_H, $00

STACK_Y:
        .fill MAZE_CELL_W * MAZE_CELL_H, $00

STACK_TOP:
        .word $0000

PLAYER_X:
        .byte PLAYER_START_X
PLAYER_Y:
        .byte PLAYER_START_Y

TEMP_PTR:
        .word $0000
ROW_INDEX:
        .byte $00
COL_INDEX:
        .byte $00
TMP_DIRS:
        .byte $00
TMP_CHOICE:
        .byte $00
CUR_CELL_X:
        .byte $00
CUR_CELL_Y:
        .byte $00
NEXT_CELL_X:
        .byte $00
NEXT_CELL_Y:
        .byte $00
STACK_POS:
        .word $0000
