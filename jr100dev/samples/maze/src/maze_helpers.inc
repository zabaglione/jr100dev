; Direction vectors (NESW)
DIR_COUNT      .equ 4
DIR_N          .equ 0
DIR_E          .equ 1
DIR_S          .equ 2
DIR_W          .equ 3

WALL_N         .equ $08
WALL_E         .equ $04
WALL_S         .equ $02
WALL_W         .equ $01

DX_TABLE:
        .byte 0, 1, 0, -1
DY_TABLE:
        .byte -1, 0, 1, 0
OPPOSITE_TABLE:
        .byte DIR_S, DIR_W, DIR_N, DIR_E
WALL_TABLE:
        .byte WALL_N, WALL_E, WALL_S, WALL_W
