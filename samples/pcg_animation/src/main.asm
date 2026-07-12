        .org $0300
        JMP MAIN

PCG_BASE:          .equ $C000
PCG_FRAME_END:     .equ $C020
VRAM_BASE:         .equ $C100
VRAM_END:          .equ $C400
VIA_ORB:           .equ $C800
VIA_ORA:           .equ $C801
VIA_DDRB:          .equ $C802
VIA_DDRA:          .equ $C803
PB5_MASK:          .equ $20
PLAYER_START:      .equ $C26F
PLAYER_CODE:       .equ $80
DIR_LEFT:          .equ 1
DIR_RIGHT:         .equ 2
DIR_UP:            .equ 3
DIR_DOWN:          .equ 4
MOVE_DELAY:        .equ $3000

; Configure CMODE PCG, copy the initial frame, and draw four resident codes.
MAIN:
        JSR INIT_IO
        JSR CLEAR_SCREEN
        LDX #PLAYER_START
        STX PLAYER_VRAM_PTR
        JSR SELECT_PLAYER_FRAME
        JSR ANIM_APPLY_FRAME
        JSR DRAW_PLAYER

MAIN_LOOP:
        JSR READ_DIRECTION
        TSTA
        BEQ MAIN_LOOP
        STAA PLAYER_DIRECTION
        JSR MOVE_PLAYER
        JSR WAIT_MOVE_DELAY
        BRA MAIN_LOOP

; Keep keyboard inputs intact while selecting the PCG display plane with PB5.
INIT_IO:
        LDAA VIA_DDRA
        ORAA #$0F
        STAA VIA_DDRA
        LDAA VIA_DDRB
        ORAA #PB5_MASK
        STAA VIA_DDRB
        LDAA VIA_ORB
        ORAA #PB5_MASK
        STAA VIA_ORB
        CLRA
        STAA VIA_ORA
        RTS

CLEAR_SCREEN:
        LDX #VRAM_BASE
        CLRA
CLEAR_SCREEN_LOOP:
        STAA ,X
        INX
        CPX #VRAM_END
        BNE CLEAR_SCREEN_LOOP
        RTS

; I/J/K/M map to up/left/right/down. Port B keys are active-low.
READ_DIRECTION:
        LDAA #5
        STAA VIA_ORA
        JSR READ_KEY_ROW
        BITA #$04
        BNE READ_UP

        LDAA #6
        STAA VIA_ORA
        JSR READ_KEY_ROW
        BITA #$02
        BNE READ_LEFT
        BITA #$04
        BNE READ_RIGHT

        LDAA #7
        STAA VIA_ORA
        JSR READ_KEY_ROW
        BITA #$08
        BNE READ_DOWN
        CLRA
        RTS
READ_LEFT:
        LDAA #DIR_LEFT
        RTS
READ_RIGHT:
        LDAA #DIR_RIGHT
        RTS
READ_UP:
        LDAA #DIR_UP
        RTS
READ_DOWN:
        LDAA #DIR_DOWN
        RTS

READ_KEY_ROW:
        LDAA VIA_ORB
        EORA #$1F
        ANDA #$1F
        STAA KEY_ROW_TEMP
        NOP
        LDAA VIA_ORB
        EORA #$1F
        ANDA #$1F
        CMPA KEY_ROW_TEMP
        BEQ READ_KEY_ROW_DONE
        CLRA
READ_KEY_ROW_DONE:
        RTS

; Validate bounds before erasing. X receives the new top-left VRAM address.
MOVE_PLAYER:
        LDAA PLAYER_DIRECTION
        CMPA #DIR_LEFT
        BEQ MOVE_LEFT
        CMPA #DIR_RIGHT
        BEQ MOVE_RIGHT
        CMPA #DIR_UP
        BEQ MOVE_UP
        CMPA #DIR_DOWN
        BEQ MOVE_DOWN
        RTS

MOVE_LEFT:
        LDAA PLAYER_X
        CMPA #1
        BLS MOVE_REJECTED
        JSR ERASE_PLAYER
        DEC PLAYER_X
        LDX PLAYER_VRAM_PTR
        DEX
        BRA MOVE_ACCEPTED

MOVE_RIGHT:
        LDAA PLAYER_X
        CMPA #29
        BCC MOVE_REJECTED
        JSR ERASE_PLAYER
        INC PLAYER_X
        LDX PLAYER_VRAM_PTR
        INX
        BRA MOVE_ACCEPTED

MOVE_UP:
        LDAA PLAYER_Y
        CMPA #2
        BLS MOVE_REJECTED
        JSR ERASE_PLAYER
        DEC PLAYER_Y
        LDX PLAYER_VRAM_PTR
        LDAB #32
MOVE_UP_LOOP:
        DEX
        DECB
        BNE MOVE_UP_LOOP
        BRA MOVE_ACCEPTED

MOVE_DOWN:
        LDAA PLAYER_Y
        CMPA #21
        BCC MOVE_REJECTED
        JSR ERASE_PLAYER
        INC PLAYER_Y
        LDX PLAYER_VRAM_PTR
        LDAB #32
MOVE_DOWN_LOOP:
        INX
        DECB
        BNE MOVE_DOWN_LOOP

MOVE_ACCEPTED:
        STX PLAYER_VRAM_PTR
        LDAA ANIM_PHASE
        EORA #1
        STAA ANIM_PHASE
        JSR SELECT_PLAYER_FRAME
        JSR ANIM_APPLY_FRAME
        JSR DRAW_PLAYER
MOVE_REJECTED:
        RTS

; Convert direction and phase to a byte offset in PLAYER_FRAME_POINTERS.
; Table order is LEFT_0, LEFT_1, RIGHT_0, RIGHT_1, UP_0, UP_1,
; DOWN_0, DOWN_1, matching the Animation editor timeline order.
SELECT_PLAYER_FRAME:
        LDAA PLAYER_DIRECTION
        DECA
        ASLA
        ASLA
        LDAB ANIM_PHASE
        BEQ SELECT_FRAME_OFFSET_READY
        ADDA #2
SELECT_FRAME_OFFSET_READY:
        STAA FRAME_TABLE_OFFSET
        LDX #PLAYER_FRAME_POINTERS
SELECT_FRAME_SEEK:
        LDAA FRAME_TABLE_OFFSET
        BEQ SELECT_FRAME_POINTER_READY
        INX
        DEC FRAME_TABLE_OFFSET
        BRA SELECT_FRAME_SEEK
SELECT_FRAME_POINTER_READY:
        LDAA ,X
        STAA ANIM_SOURCE_PTR
        INX
        LDAA ,X
        STAA ANIM_SOURCE_PTR+1
        RTS

; Copy exactly four glyphs from frame storage to resident slots $80-$83.
ANIM_APPLY_FRAME:
        LDX #PCG_BASE
        STX ANIM_TARGET_PTR
ANIM_COPY_LOOP:
        LDX ANIM_SOURCE_PTR
        LDAA ,X
        INX
        STX ANIM_SOURCE_PTR
        LDX ANIM_TARGET_PTR
        STAA ,X
        INX
        STX ANIM_TARGET_PTR
        CPX #PCG_FRAME_END
        BNE ANIM_COPY_LOOP
        RTS

DRAW_PLAYER:
        LDX PLAYER_VRAM_PTR
        LDAA #PLAYER_CODE
        STAA ,X
        INCA
        INX
        STAA ,X
        LDAB #31
DRAW_PLAYER_NEXT_ROW:
        INX
        DECB
        BNE DRAW_PLAYER_NEXT_ROW
        INCA
        STAA ,X
        INCA
        INX
        STAA ,X
        RTS

ERASE_PLAYER:
        LDX PLAYER_VRAM_PTR
        CLRA
        STAA ,X
        INX
        STAA ,X
        LDAB #31
ERASE_PLAYER_NEXT_ROW:
        INX
        DECB
        BNE ERASE_PLAYER_NEXT_ROW
        STAA ,X
        INX
        STAA ,X
        RTS

WAIT_MOVE_DELAY:
        LDX #MOVE_DELAY
WAIT_MOVE_DELAY_LOOP:
        DEX
        BNE WAIT_MOVE_DELAY_LOOP
        RTS

PLAYER_X:          .byte 15
PLAYER_Y:          .byte 11
PLAYER_DIRECTION:  .byte DIR_DOWN
ANIM_PHASE:        .byte 0
KEY_ROW_TEMP:      .byte 0
FRAME_TABLE_OFFSET: .byte 0
PLAYER_VRAM_PTR:   .word PLAYER_START
ANIM_SOURCE_PTR:   .word 0
ANIM_TARGET_PTR:   .word PCG_BASE

        .include "player_frames.inc"
