; A=1..8 pose, B=tile index, X=consecutive 32-byte poses.
; Each actor owns exactly four character slots. Other actors never share them.
FACE_CACHE: .equ $3380
FACE_SOURCE: .equ $3388
FACE_DEST: .equ $338A
FACE_POSE: .equ $338C
FACE_SLOT: .equ $338D
N_FACE_RESET:
    LDX #FACE_CACHE
    CLRA
    LDAB #8
N_FACE_RESET_LOOP:
    STAA 0,X
    INX
    DECB
    BNE N_FACE_RESET_LOOP
    RTS
N_FACE:
    STX FACE_SOURCE
    STAB FACE_SLOT
    STAA FACE_POSE
    LDX #FACE_CACHE
    TBA
    JSR N_INDEX
    LDAA FACE_POSE
    CMPA 0,X
    BEQ N_FACE_DONE
    STAA 0,X
    DECA
    ASLA
    ASLA
    ASLA
    ASLA
    ASLA
    LDX FACE_SOURCE
    JSR N_INDEX
    STX FACE_SOURCE
    LDAA FACE_SLOT
    ASLA
    ASLA
    ASLA
    ASLA
    ASLA
    LDX #$C000
    JSR N_INDEX
    STX FACE_DEST
    LDAB #32
N_FACE_COPY:
    LDX FACE_SOURCE
    LDAA 0,X
    INX
    STX FACE_SOURCE
    LDX FACE_DEST
    STAA 0,X
    INX
    STX FACE_DEST
    DECB
    BNE N_FACE_COPY
N_FACE_DONE:
    RTS
