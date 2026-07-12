; Each frame is four row-major 8x8 glyphs: top-left, top-right,
; bottom-left, bottom-right. The runtime copies one 32-byte frame.

PLAYER_DOWN_0:
        .byte $03, $07, $06, $07, $03, $0F, $1B, $1B
        .byte $C0, $E0, $60, $E0, $C0, $F0, $D8, $D8
        .byte $03, $03, $06, $0C, $0C, $18, $18, $00
        .byte $C0, $C0, $60, $30, $30, $18, $18, $00

PLAYER_DOWN_1:
        .byte $03, $07, $06, $07, $03, $0F, $1B, $1B
        .byte $C0, $E0, $60, $E0, $C0, $F0, $D8, $D8
        .byte $03, $03, $06, $0C, $18, $30, $0C, $18
        .byte $C0, $C0, $60, $30, $60, $30, $0C, $00

PLAYER_UP_0:
        .byte $03, $07, $07, $07, $03, $0F, $1B, $1B
        .byte $C0, $E0, $E0, $E0, $C0, $F0, $D8, $D8
        .byte $03, $03, $06, $0C, $0C, $18, $18, $00
        .byte $C0, $C0, $60, $30, $30, $18, $18, $00

PLAYER_UP_1:
        .byte $03, $07, $07, $07, $03, $0F, $1B, $1B
        .byte $C0, $E0, $E0, $E0, $C0, $F0, $D8, $D8
        .byte $03, $03, $06, $0C, $18, $30, $0C, $18
        .byte $C0, $C0, $60, $30, $60, $30, $0C, $00

PLAYER_RIGHT_0:
        .byte $03, $07, $07, $07, $03, $07, $0F, $0F
        .byte $C0, $E0, $C0, $F0, $C0, $F0, $F8, $F0
        .byte $03, $03, $06, $0C, $0C, $18, $18, $00
        .byte $C0, $C0, $60, $30, $30, $18, $18, $00

PLAYER_RIGHT_1:
        .byte $03, $07, $07, $07, $03, $07, $0F, $0F
        .byte $C0, $E0, $C0, $F0, $C0, $F0, $F8, $F0
        .byte $03, $03, $06, $0C, $18, $30, $0C, $18
        .byte $C0, $C0, $60, $30, $60, $30, $0C, $00

PLAYER_LEFT_0:
        .byte $03, $07, $03, $0F, $03, $0F, $1F, $0F
        .byte $C0, $E0, $E0, $E0, $C0, $E0, $F0, $F0
        .byte $03, $03, $06, $0C, $0C, $18, $18, $00
        .byte $C0, $C0, $60, $30, $30, $18, $18, $00

PLAYER_LEFT_1:
        .byte $03, $07, $03, $0F, $03, $0F, $1F, $0F
        .byte $C0, $E0, $E0, $E0, $C0, $E0, $F0, $F0
        .byte $03, $03, $06, $0C, $06, $0C, $30, $00
        .byte $C0, $C0, $60, $30, $18, $0C, $30, $18

PLAYER_FRAME_POINTERS:
        .word PLAYER_LEFT_0, PLAYER_LEFT_1
        .word PLAYER_RIGHT_0, PLAYER_RIGHT_1
        .word PLAYER_UP_0, PLAYER_UP_1
        .word PLAYER_DOWN_0, PLAYER_DOWN_1
