        .org $0300
        JMP MAIN

        .include "macro.inc"
        .include "ctl.inc"

; VRAM への文字表示、キー入力、サウンド出力の一連の流れを確認できるデモ。
; 0〜9 を描画した後、押下したキーコードを画面に表示しつつ SPACE のみビープ音を鳴らす。

        .data
; FOR ループの制御用カウンタ。
VAR8 LOOP_I, 0
; 直近で検出したキーコード。
VAR8 LAST_KEY, 0

        .code
MAIN:
        ; 画面を初期化し、タイトルと操作説明を表示する。
        CLR_VRAM
        BEEP                            ; 起動確認用に短いビープを鳴らす
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        LDX #STD_VRAM_BASE + 32
        PRINT_STR PROMPT

        ; 3 行目に 0〜9 の文字を並べる。
        LDX #STD_VRAM_BASE + 64
FOR_BEGIN DIGITS_TOP, DIGITS_END, LOOP_I, 0, 9
        LDAA LOOP_I
        ADDA #$30                      ; 数値を ASCII コードへ変換
        JSR __STD_TO_VRAM
        STAA ,X
        INX
FOR_END DIGITS_TOP, DIGITS_END, LOOP_I

        ; 押されたキーのコードを表示する領域を初期化。
        LDX #STD_VRAM_BASE + 96
        PRINT_STR LABEL

; 入力待ちループ。いずれかのキーが押されるまで WAIT_TOP を回る。
WHILE_BEGIN WAIT_TOP
        SCAN_KEY
        STAA LAST_KEY
        WHILE_IF_ZERO WAIT_END, LAST_KEY

        ; 押されたキーのコード値を画面に表示する。
        LDX #STD_VRAM_BASE + 112
        LDAA LAST_KEY
        JSR __STD_TO_VRAM
        STAA ,X

        ; SPACE (コード 0x01) のみビープ音を鳴らす。
        IF_EQ NOT_SPACE, LAST_KEY, $01
            BEEP
        IF_END NOT_SPACE

        ; 表示を消して次の入力へ備える。
        LDX #STD_VRAM_BASE + 96
        PRINT_STR LABEL
        LDX #STD_VRAM_BASE + 112
        LDAA #' '
        JSR __STD_TO_VRAM
        STAA ,X
WHILE_END WAIT_TOP, WAIT_END

        BRA MAIN

TITLE:  .ascii "JR-100 I/O DEMO\0"
PROMPT: .ascii "PRESS KEY TO SHOW CODE\0"
LABEL:  .ascii "LAST CODE: \0"
