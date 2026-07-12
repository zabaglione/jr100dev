        .org $0400

; VRAM の 2 行目に固定メッセージを描画するサブルーチン。
; 標準マクロ本体は main.asm だけで展開し、その公開ラベルを再利用する。
DRAW_MESSAGE:
        LDX #$C120
        STX STD_VRAM_PTR
        LDX #MESSAGE
        JSR __STD_PRINT_STR
        RTS

MESSAGE: .ascii "DRAWN FROM MODULE\0"
