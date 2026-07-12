; Each frame is four row-major 8x8 glyphs: top-left, top-right,
; bottom-left, bottom-right. The runtime copies one 32-byte frame.

PLAYER_DOWN_0:
        .byte $03, $07, $06, $07, $03, $0F, $1B, $33
        .byte $C0, $E0, $60, $E0, $C0, $F0, $D8, $CC
        .byte $63, $03, $07, $0E, $1C, $38, $78, $00
        .byte $C6, $CC, $E0, $60, $60, $30, $38, $00

PLAYER_DOWN_1:
        .byte $03, $07, $06, $07, $03, $0F, $1B, $33
        .byte $C0, $E0, $60, $E0, $C0, $F0, $D8, $CC
        .byte $63, $33, $07, $06, $06, $0C, $1C, $00
        .byte $C6, $C0, $E0, $70, $38, $1C, $1E, $00

PLAYER_UP_0:
        .byte $03, $07, $07, $07, $03, $0F, $1B, $33
        .byte $C0, $E0, $E0, $E0, $C0, $F0, $D8, $CC
        .byte $63, $03, $07, $0E, $1C, $38, $78, $00
        .byte $C6, $CC, $E0, $60, $60, $30, $38, $00

PLAYER_UP_1:
        .byte $03, $07, $07, $07, $03, $0F, $1B, $33
        .byte $C0, $E0, $E0, $E0, $C0, $F0, $D8, $CC
        .byte $63, $33, $07, $06, $06, $0C, $1C, $00
        .byte $C6, $C0, $E0, $70, $38, $1C, $1E, $00

PLAYER_RIGHT_0:
        .byte $03, $07, $07, $07, $03, $07, $0D, $07
        .byte $C0, $E0, $B0, $E0, $C0, $E0, $EC, $C6
        .byte $03, $03, $07, $03, $03, $06, $0F, $00
        .byte $C3, $C6, $E0, $60, $38, $1C, $0F, $00

PLAYER_RIGHT_1:
        .byte $03, $07, $07, $07, $03, $07, $19, $31
        .byte $C0, $E0, $B0, $E0, $C0, $E0, $EC, $F0
        .byte $63, $C3, $07, $06, $0E, $1C, $3C, $00
        .byte $D8, $C0, $E0, $E0, $60, $30, $38, $00

PLAYER_LEFT_0:
        .byte $03, $07, $0D, $07, $03, $07, $37, $63
        .byte $C0, $E0, $E0, $E0, $C0, $E0, $B0, $E0
        .byte $C3, $63, $07, $06, $1C, $38, $F0, $00
        .byte $C0, $C0, $E0, $C0, $C0, $60, $F0, $00

PLAYER_LEFT_1:
        .byte $03, $07, $0D, $07, $03, $07, $37, $0F
        .byte $C0, $E0, $E0, $E0, $C0, $E0, $98, $8C
        .byte $1B, $03, $07, $07, $06, $0C, $1C, $00
        .byte $C6, $C3, $E0, $60, $70, $38, $3C, $00

PLAYER_FRAME_POINTERS:
        .word PLAYER_LEFT_0, PLAYER_LEFT_1
        .word PLAYER_RIGHT_0, PLAYER_RIGHT_1
        .word PLAYER_UP_0, PLAYER_UP_1
        .word PLAYER_DOWN_0, PLAYER_DOWN_1
