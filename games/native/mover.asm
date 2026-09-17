; Half-cell interpolation between two adjacent positions on an 8-wide board.
; ARG0=destination, ARG1=origin, ARG2=tile, ARG3=left offset. Same positions
; produce the settled tile. Only drawing changes; collision stays on the grid.
N_ARG3: .equ $338E
N_MOVE_ROW: .equ $338F
N_MOVER:
    LDAA N_ARG0
    LSRA
    LSRA
    LSRA
    STAA N_TMP
    LDAA N_ARG1
    LSRA
    LSRA
    LSRA
    ADDA N_TMP
    ADDA #3
    STAA N_MOVE_ROW
    LDAA N_ARG0
    ANDA #7
    STAA N_TMP
    LDAA N_ARG1
    ANDA #7
    ADDA N_TMP
    ADDA N_ARG3
    STAA N_ARG0
    LDAA N_MOVE_ROW
    STAA N_ARG1
    JMP N_TILE
