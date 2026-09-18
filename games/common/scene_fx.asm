; Local ROM-character effects for the assembly games. No PCG slots are borrowed.
FX_CELL: .equ $33A0
FX_CLOCK: .equ $33A2
FX_PHASE: .equ $33A3
FX_REGX: .equ $33A4
FX_SAVE: .equ $33A6
FX_DIR: .equ $33AA

; X = top-left VRAM cell. Save the scene and freeze gameplay time.
FX_BEGIN:
    STX FX_CELL
    LDAA TICK
    STAA FX_CLOCK
    INC PACE_ACTIVE
    LDAA 0,X
    STAA FX_SAVE
    LDAA 1,X
    STAA FX_SAVE + 1
    LDAA 32,X
    STAA FX_SAVE + 2
    LDAA 33,X
    STAA FX_SAVE + 3
    RTS
FX_END:
    CLR PACE_ACTIVE
    LDAA FX_CLOCK
    STAA TICK
    LDX FX_CELL
    RTS

; A/B = tile x/y on a 2x2 grid whose top row is screen row two.
FX_AT:
    LDX #$C140
FX_AT_ROW:
    TSTB
    BEQ FX_AT_COLUMN
    ADX #64
    DECB
    BRA FX_AT_ROW
FX_AT_COLUMN:
    TAB
    ASLB
FX_AT_COL_LOOP:
    TSTB
    BEQ FX_AT_DONE
    INX
    DECB
    BRA FX_AT_COL_LOOP
FX_AT_DONE:
    RTS

; Burst -> separated fragments -> dust, then the next complete frame clears the overlay.
FX_BURST:
    PSHA
    PSHB
    JSR FX_BEGIN
    CLR FX_PHASE
FX_BURST_FRAME:
    LDX #FX_PARTICLES
    LDAB FX_PHASE
FX_PARTICLE_INDEX:
    TSTB
    BEQ FX_PARTICLE_READ
    ADX #4
    DECB
    BRA FX_PARTICLE_INDEX
FX_PARTICLE_READ:
    LDAA 0,X
    LDAB 1,X
    LDX FX_CELL
    STAA 0,X
    STAB 1,X
    LDX #FX_PARTICLES + 2
    LDAB FX_PHASE
FX_LOWER_INDEX:
    TSTB
    BEQ FX_LOWER_READ
    ADX #4
    DECB
    BRA FX_LOWER_INDEX
FX_LOWER_READ:
    LDAA 0,X
    LDAB 1,X
    LDX FX_CELL
    STAA 32,X
    STAB 33,X
    LDAA #5
    JSR PACE_WAIT
    INC FX_PHASE
    LDAA FX_PHASE
    CMPA #3
    BCS FX_BURST_FRAME
    JSR FX_END
    PULB
    PULA
    RTS
FX_PARTICLES:
    .byte $61,$73,$7A,$78, $76,$63,$66,$64, $0E,$0E,$0E,$0E

; A = direction 1..4, X = previous actor cell. Shift one character halfway.
FX_MOVE:
    PSHA
    PSHB
    STAA FX_DIR
    JSR FX_BEGIN
    LDX FX_CELL
    LDAA #64
    STAA 0,X
    STAA 1,X
    STAA 32,X
    STAA 33,X
    LDAA FX_DIR
    CMPA #1
    BEQ FX_UP
    CMPA #2
    BEQ FX_DOWN
    CMPA #3
    BEQ FX_LEFT
    INX
    BRA FX_MOVE_DRAW
FX_UP:
    LDAB #32
FX_UP_STEP:
    DEX
    DECB
    BNE FX_UP_STEP
    BRA FX_MOVE_DRAW
FX_DOWN:
    ADX #32
    BRA FX_MOVE_DRAW
FX_LEFT:
    DEX
FX_MOVE_DRAW:
    LDAA FX_SAVE
    STAA 0,X
    LDAA FX_SAVE + 1
    STAA 1,X
    LDAA FX_SAVE + 2
    STAA 32,X
    LDAA FX_SAVE + 3
    STAA 33,X
    LDAA #3
    JSR PACE_WAIT
    JSR FX_END
    PULB
    PULA
    RTS

; A = cardinal direction. A short connected line shows the projectile's transit.
FX_BEAM:
    PSHA
    PSHB
    STAA FX_DIR
    JSR FX_BEGIN
    LDX FX_CELL
    LDAA FX_DIR
    CMPA #3
    BCS FX_BEAM_VERTICAL
    LDAA #13
    STAA 0,X
    STAA 1,X
    BRA FX_BEAM_HOLD
FX_BEAM_VERTICAL:
    LDAA #$71
    STAA 0,X
    STAA 32,X
FX_BEAM_HOLD:
    LDAA #2
    JSR PACE_WAIT
    JSR FX_END
    PULB
    PULA
    RTS
