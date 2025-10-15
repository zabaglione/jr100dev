        .org $0400
        .include "macro.inc"

        .public DRAW_MESSAGE

; VRAM の 2 行目に固定メッセージを描画するサブルーチン。
DRAW_MESSAGE:
        LDX #STD_VRAM_BASE + 32
        PRINT_STR MESSAGE
        RTS

MESSAGE: .ascii "DRAWN FROM MODULE\0"
