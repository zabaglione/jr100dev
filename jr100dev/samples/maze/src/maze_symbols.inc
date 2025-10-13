        .equ MAZE_MAP, $0600
        .equ MAZE_CELLS, MAZE_MAP + MAZE_CHAR_W * MAZE_CHAR_H
        .equ VISITED_MAP, MAZE_CELLS + MAZE_CELL_W * MAZE_CELL_H
        .equ STACK_X, VISITED_MAP + MAZE_CELL_W * MAZE_CELL_H
        .equ STACK_Y, STACK_X + MAZE_CELL_W * MAZE_CELL_H
        .equ STACK_TOP, STACK_Y + MAZE_CELL_W * MAZE_CELL_H
        .equ PLAYER_X, STACK_TOP + 2
        .equ PLAYER_Y, PLAYER_X + 1
        .equ TEMP_PTR, PLAYER_Y + 1
        .equ ROW_INDEX, TEMP_PTR + 2
        .equ COL_INDEX, ROW_INDEX + 1
        .equ TMP_DIRS, COL_INDEX + 1
        .equ TMP_CHOICE, TMP_DIRS + 1
        .equ CUR_CELL_X, TMP_CHOICE + 1
        .equ CUR_CELL_Y, CUR_CELL_X + 1
        .equ NEXT_CELL_X, CUR_CELL_Y + 1
        .equ NEXT_CELL_Y, NEXT_CELL_X + 1
        .equ STACK_POS, NEXT_CELL_Y + 1
