        .org $0500

        .include "macro.inc"
        .include "ctl.inc"

VAR8 RNG_SEED, $5A

RNG_INIT:
        LDAA #$5A
        STAA RNG_SEED
        RTS

RNG_NEXT:
        LDAA RNG_SEED
        LSLA        ; *2
        LSLA        ; *4
        ADDA RNG_SEED ; *5
        ADDA #$01
        STAA RNG_SEED
        RTS
