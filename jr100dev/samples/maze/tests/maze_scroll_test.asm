        .org $0300

        .include "../src/common.inc"
        .include "../../../std/scroll.inc"

; 入力ワーク
ORIGIN_X:      .byte 0
ORIGIN_Y:      .byte 0
PLAYER_X:      .byte 0
PLAYER_Y:      .byte 0
MARGIN_VAL:    .byte 0
RIGHT_BOUND:   .byte 0
BOTTOM_BOUND:  .byte 0
MAX_ORIGIN_X:  .byte 0
MAX_ORIGIN_Y:  .byte 0
DRAW_X:        .byte 0
DRAW_Y:        .byte 0

; 結果領域
RESULT_BASE:   .equ $0900

START:
        JSR CASE_NO_SCROLL
        JSR CASE_SCROLL_LEFT_CLAMP
        JSR CASE_SCROLL_RIGHT
        JSR CASE_SCROLL_BOTTOM_CLAMP
        JSR CASE_SCROLL_TOP

HALT:
        BRA HALT

CASE_NO_SCROLL:
        LDAA #5
        STAA ORIGIN_X
        LDAA #3
        STAA ORIGIN_Y
        LDAA #7
        STAA PLAYER_X
        LDAA #10
        STAA PLAYER_Y
        LDAA #2
        STAA MARGIN_VAL
        STAA RIGHT_BOUND      ; placeholder, overwritten below
        LDAA #8
        STAA RIGHT_BOUND
        LDAA #20
        STAA BOTTOM_BOUND
        LDAA #30
        STAA MAX_ORIGIN_X
        STAA MAX_ORIGIN_Y

        STD_SCROLL_UPDATE ORIGIN_X, ORIGIN_Y, PLAYER_X, PLAYER_Y, MARGIN_VAL, RIGHT_BOUND, BOTTOM_BOUND, MAX_ORIGIN_X, MAX_ORIGIN_Y, DRAW_X, DRAW_Y

        LDX #RESULT_BASE
        LDAA ORIGIN_X
        STAA ,X
        LDAA ORIGIN_Y
        STAA 1,X
        LDAA DRAW_X
        STAA 2,X
        LDAA DRAW_Y
        STAA 3,X
        RTS

CASE_SCROLL_LEFT_CLAMP:
        LDAA #5
        STAA ORIGIN_X
        LDAA #4
        STAA ORIGIN_Y
        LDAA #6
        STAA PLAYER_X
        LDAA #8
        STAA PLAYER_Y
        LDAA #4
        STAA MARGIN_VAL
        LDAA #10
        STAA RIGHT_BOUND
        LDAA #15
        STAA BOTTOM_BOUND
        LDAA #40
        STAA MAX_ORIGIN_X
        STAA MAX_ORIGIN_Y

        STD_SCROLL_UPDATE ORIGIN_X, ORIGIN_Y, PLAYER_X, PLAYER_Y, MARGIN_VAL, RIGHT_BOUND, BOTTOM_BOUND, MAX_ORIGIN_X, MAX_ORIGIN_Y, DRAW_X, DRAW_Y

        LDX #RESULT_BASE+4
        LDAA ORIGIN_X
        STAA ,X
        LDAA DRAW_X
        STAA 1,X
        RTS

CASE_SCROLL_RIGHT:
        LDAA #0
        STAA ORIGIN_X
        LDAA #0
        STAA ORIGIN_Y
        LDAA #12
        STAA PLAYER_X
        LDAA #5
        STAA PLAYER_Y
        LDAA #1
        STAA MARGIN_VAL
        LDAA #8
        STAA RIGHT_BOUND
        LDAA #10
        STAA BOTTOM_BOUND
        LDAA #20
        STAA MAX_ORIGIN_X
        LDAA #15
        STAA MAX_ORIGIN_Y

        STD_SCROLL_UPDATE ORIGIN_X, ORIGIN_Y, PLAYER_X, PLAYER_Y, MARGIN_VAL, RIGHT_BOUND, BOTTOM_BOUND, MAX_ORIGIN_X, MAX_ORIGIN_Y, DRAW_X, DRAW_Y

        LDX #RESULT_BASE+6
        LDAA ORIGIN_X
        STAA ,X
        LDAA DRAW_X
        STAA 1,X
        RTS

CASE_SCROLL_BOTTOM_CLAMP:
        LDAA #2
        STAA MARGIN_VAL
        LDAA #25
        STAA RIGHT_BOUND
        LDAA #20
        STAA BOTTOM_BOUND
        LDAA #0
        STAA ORIGIN_X
        LDAA #18
        STAA ORIGIN_Y
        LDAA #5
        STAA PLAYER_X
        LDAA #40
        STAA PLAYER_Y
        LDAA #0
        STAA MAX_ORIGIN_X
        LDAA #18
        STAA MAX_ORIGIN_Y

        STD_SCROLL_UPDATE ORIGIN_X, ORIGIN_Y, PLAYER_X, PLAYER_Y, MARGIN_VAL, RIGHT_BOUND, BOTTOM_BOUND, MAX_ORIGIN_X, MAX_ORIGIN_Y, DRAW_X, DRAW_Y

        LDX #RESULT_BASE+8
        LDAA ORIGIN_Y
        STAA ,X
        LDAA DRAW_Y
        STAA 1,X
        RTS

CASE_SCROLL_TOP:
        LDAA #5
        STAA ORIGIN_Y
        LDAA #4
        STAA PLAYER_Y
        LDAA #0
        STAA ORIGIN_X
        LDAA #3
        STAA PLAYER_X
        LDAA #3
        STAA MARGIN_VAL
        LDAA #10
        STAA RIGHT_BOUND
        LDAA #15
        STAA BOTTOM_BOUND
        LDAA #30
        STAA MAX_ORIGIN_X
        LDAA #40
        STAA MAX_ORIGIN_Y

        STD_SCROLL_UPDATE ORIGIN_X, ORIGIN_Y, PLAYER_X, PLAYER_Y, MARGIN_VAL, RIGHT_BOUND, BOTTOM_BOUND, MAX_ORIGIN_X, MAX_ORIGIN_Y, DRAW_X, DRAW_Y

        LDX #RESULT_BASE+10
        LDAA ORIGIN_Y
        STAA ,X
        LDAA DRAW_Y
        STAA 1,X
        RTS
