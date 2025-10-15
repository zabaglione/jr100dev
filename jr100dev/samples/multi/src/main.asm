        .org $0300
        JMP START

        .include "macro.inc"
        .include "ctl.inc"

; 複数ファイル構成のサンプル。`message.asm` で定義したルーチンを呼び出しつつ、
; メイン側ではタイトル表示とカウンタ描画を担当する。

DRAW_MESSAGE EQU $0400

        .data
; LOOP_I は 0〜5 の数値を表示するためのループ変数。
VAR8 LOOP_I, 0

        .code
START:
        CLR_VRAM
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        JSR DRAW_MESSAGE         ; 別モジュールで定義したメッセージ描画ルーチンを呼ぶ

        ; 数字 0〜5 を 1 行に並べて表示する。
        LDX #STD_VRAM_BASE + 64
FOR_BEGIN LOOP_TOP, LOOP_END, LOOP_I, 0, 5
        LDAA LOOP_I
        ADDA #$30
        JSR __STD_TO_VRAM
        STAA ,X
        INX
FOR_END LOOP_TOP, LOOP_END, LOOP_I

        RTS

TITLE:  .ascii "MULTI FILE DEMO\0"
