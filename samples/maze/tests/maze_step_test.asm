        .org $0300

        .include "../src/common.inc"

MAZE_MAP:        .equ $0600
MAZE_MAP_END:    .equ (MAZE_MAP + MAZE_CHAR_W * MAZE_CHAR_H)
VRAM_BASE:       .equ $C100

ROW_INDEX:       .equ $0500
COL_INDEX:       .equ $0501
CHAR_OFFSET_LO:  .equ $0502
CHAR_OFFSET_HI:  .equ $0503
TEMP_SHIFT:      .equ $0504
TEMP_PTR:        .equ $0505
CUR_CELL_POS:    .equ $0507  ; low=x, high=y
DST_PTR:         .equ $0509

        JSR INIT_MAP
        JSR CARVE_EAST_FROM_ORIGIN
        JSR COPY_MAP_TO_VRAM

HALT:
        BRA HALT


INIT_MAP:
        LDAA #'#'
        LDX #MAZE_MAP
FILL_ALL:
        STAA ,X
        INX
        CPX #MAZE_MAP_END
        BNE FILL_ALL
        RTS

CARVE_EAST_FROM_ORIGIN:
        CLRA
        STAA >CUR_CELL_POS
        STAA >CUR_CELL_POS+1
        JSR OPEN_CELL_FROM_CUR
        ; passage wall between cells
        LDAA >CUR_CELL_POS
        ASLA
        INCA
        STAA >COL_INDEX        ; char x
        LDAA >CUR_CELL_POS+1
        ASLA
        INCA
        STAA >ROW_INDEX        ; char y
        ; open current cell
        JSR MAP_PTR_FROM_CHAR
        LDX >TEMP_PTR
        LDAA #' '
        STAA ,X
        ; open wall between cells (x+1)
        INC >COL_INDEX
        JSR MAP_PTR_FROM_CHAR
        LDX >TEMP_PTR
        LDAA #' '
        STAA ,X
        ; open next cell (x+2)
        INC >COL_INDEX
        JSR MAP_PTR_FROM_CHAR
        LDX >TEMP_PTR
        LDAA #' '
        STAA ,X
        RTS

OPEN_CELL_FROM_CUR:
        LDAA >CUR_CELL_POS+1
        ASLA
        INCA
        STAA >ROW_INDEX
        LDAA >CUR_CELL_POS
        ASLA
        INCA
        STAA >COL_INDEX
        JSR MAP_PTR_FROM_CHAR
        LDX >TEMP_PTR
        LDAA #' '
        STAA ,X
        RTS

COPY_MAP_TO_VRAM:
        LDX #VRAM_BASE
        STX >DST_PTR
        LDAA #1
        STAA >ROW_INDEX
        CLRA
        STAA >COL_INDEX
        JSR MAP_PTR_FROM_CHAR
        LDX >TEMP_PTR
        LDAA ,X
        JSR STORE_TO_VRAM
        LDAA 1,X
        JSR STORE_TO_VRAM
        LDAA 2,X
        JSR STORE_TO_VRAM
        LDAA 3,X
        JSR STORE_TO_VRAM
        RTS

STORE_TO_VRAM:
        CMPA #'#'
        BEQ STORE_HASH
        LDAA #$40
        BRA STORE_CHAR
STORE_HASH:
        LDAA #$03
STORE_CHAR:
        LDX >DST_PTR
        STAA ,X
        INX
        STX >DST_PTR
        RTS

MAP_PTR_FROM_CHAR:
        CLRA
        STAA >CHAR_OFFSET_LO
        STAA >CHAR_OFFSET_HI
        LDAA >ROW_INDEX
        BEQ ADD_COL
        STAA >TEMP_SHIFT
ROW_LOOP:
        LDAA >CHAR_OFFSET_LO
        ADDA #MAZE_CHAR_W
        STAA >CHAR_OFFSET_LO
        LDAA >CHAR_OFFSET_HI
        ADCA #0
        STAA >CHAR_OFFSET_HI
        DEC >TEMP_SHIFT
        BNE ROW_LOOP
ADD_COL:
        LDAA >COL_INDEX
        ADDA >CHAR_OFFSET_LO
        STAA >CHAR_OFFSET_LO
        LDAA #0
        ADCA >CHAR_OFFSET_HI
        STAA >CHAR_OFFSET_HI
        LDAA #((MAZE_MAP >> 8) & $00FF)
        STAA >TEMP_PTR
        LDAA #(MAZE_MAP & $00FF)
        STAA >TEMP_PTR+1
        LDAA >CHAR_OFFSET_LO
        ADDA >TEMP_PTR+1
        STAA >TEMP_PTR+1
        LDAA >CHAR_OFFSET_HI
        ADCA >TEMP_PTR
        STAA >TEMP_PTR
        RTS
