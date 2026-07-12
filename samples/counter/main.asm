        .org $0300
        JMP MAIN

        .include "macro.inc"
        .include "ctl.inc"

; カウンタ値を表示し、任意キー押下でリセットできるサンプル。
; `ctl.inc` の FOR/IF/WHILE マクロを併用し、制御構文の使い方も確認できる。

        .data
; 表示中のカウンタ値。FOR ループの制御変数としても兼用する。
VAR8 COUNT, 0

        .code
MAIN:
        ; 画面全体を初期化し、タイトルと説明を描画する。
        CLR_VRAM
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        LDX #STD_VRAM_BASE + 32
        PRINT_STR PROMPT

        ; VRAM 3 行目に 0〜9 を並べて描画する。
        LDX #STD_VRAM_BASE + 64
FOR_BEGIN LOOP_TOP, LOOP_END, COUNT, 0, 9
        LDAA COUNT
        ADDA #$30              ; 10進数字を ASCII コードへ変換
        JSR __STD_TO_VRAM      ; VRAM 文字コードへマッピング
        STAA ,X
        INX
FOR_END LOOP_TOP, LOOP_END, COUNT

; いずれかのキーが押されるまで待機する。
WAIT_KEY:
        SCAN_KEY
        BEQ WAIT_KEY
        CMPA #$01              ; SPACE (0x01) のみビープ音を鳴らす
        BNE RESET
        BEEP

; カウンタ値を初期化してループの最初へ戻る。
RESET:
        CLR COUNT
        BRA MAIN

TITLE:  .ascii "FOR LOOP DEMO\0"
PROMPT: .ascii "COUNTING 0-9\0"
