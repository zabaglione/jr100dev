; Draw four arbitrary PCG/ROM quadrants without recomputing the screen address.
; OPTICS_ARRAY is the build-checked optical atlas, four bytes per 16x16 cell.
N_STAMP:
    JSR N_XY
    STX N_PTR
    LDAA N_ARG2
    ASLA
    ASLA
    LDX #OPTICS_ARRAY
    JSR N_INDEX
    LDAB 3,X
    PSHB
    LDAB 2,X
    PSHB
    LDAB 1,X
    PSHB
    LDAA 0,X
    LDX N_PTR
    STAA 0,X
    PULA
    STAA 1,X
    PULA
    STAA 32,X
    PULA
    STAA 33,X
    RTS
