        .org $0300
        JMP MAIN

        .include "macro.inc"
        .include "ctl.inc"

; --------------------------------------------------------------------------
; サンプル概要
; I/J/K/M など複数のキーを含む JR-100 のキーマトリクスを直接スキャンし、
; 押下中のキー名または特殊キー名を画面中央 (15,11) に表示する。
; 1 フレームに 1 行ずつ走査し、最初に見つけたキーのみを採用することで表示の安定性を確保している。
; 前回表示内容と変わらない場合は再描画を省略し、不要な点滅を抑制する。

; --------------------------------------------------------------------------
; constants

CENTER_VRAM_ADDR: .equ STD_VRAM_BASE + (11 * 32) + 15  ; 画面中央 (X=15, Y=11) の VRAM 先頭アドレス
KEY_ROW_COUNT:    .equ 9                               ; キーマトリクスの行数
DISPLAY_WIDTH:    .equ 6                               ; 中央表示領域をスペースで初期化する文字数
NO_KEY_HOLD_FRAMES: .equ 2                             ; 無入力が連続した際に表示を消すまでのフレーム数

; --------------------------------------------------------------------------
; variables

        .data
; 現在表示中の文字列を指すポインタ。NULL の場合は空白表示。
VAR16 CURRENT_TEXT_PTR, 0
; 最新フレームで検出した文字列ポインタ。後段で差分判定に利用。
VAR16 NEW_TEXT_PTR, 0
; 無入力フレームの連続数をカウントする。
VAR8 NO_KEY_FRAMES, 0
; 表示内容を更新する必要がある場合に 1 がセットされる。
VAR8 DISPLAY_DIRTY, 1
; 今フレームでキーを検出したかを示すフラグ。
VAR8 KEY_FOUND, 0
; 現在走査しているキーマトリクス行番号。
VAR8 ROW_INDEX, 0
; 行読み取り結果のビットマスク。
VAR8 ROW_BITS, 0
; 連続読み取りで安定確認するための一時領域。
VAR8 ROW_TEMP, 0
; 行テーブルを走査するときに利用するループカウンタ。
VAR8 ROW_ITER, 0
; 各行のキー表を指すポインタ。
VAR16 ROW_PTR, 0

; --------------------------------------------------------------------------
; code

        .code

MAIN:   CLR_VRAM
        JSR INIT_IO              ; VIA ポートの方向を初期化
        JSR DRAW_UI              ; タイトルおよび補足文を描画

MAIN_LOOP:
        JSR SCAN_KEYBOARD        ; 1 行ずつキーマトリクスを走査
        JSR DRAW_CENTER_TEXT     ; 表示が変化した場合のみ再描画
        JSR WAIT_2MS             ; ループ周期を約 2ms に調整
        BRA MAIN_LOOP

INIT_IO:
        LDAA #$0F
        STAA STD_VIA_DDRA        ; キー行選択 (ポート A 下位 4bit) を出力に設定
        CLRA
        STAA STD_VIA_DDRB        ; キーデータ入力 (ポート B 下位 5bit) は入力のまま
        STAA STD_VIA_ORA         ; 行選択を 0 に初期化
        RTS

DRAW_UI:
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        LDX #STD_VRAM_BASE + 32
        PRINT_STR PROMPT
        RTS

DRAW_CENTER_TEXT:
        LDAA DISPLAY_DIRTY
        BNE DCT_UPDATE            ; 差分がある場合のみ描画処理へ
        RTS
DCT_UPDATE:
        LDX #CENTER_VRAM_ADDR
        LDAA #DISPLAY_WIDTH
        STAA ROW_BITS
DCT_CLEAR_LOOP:
        LDAA #' '                ; 既存表示をスペースで埋めてから書き直す
        JSR __STD_TO_VRAM
        STAA ,X
        INX
        DEC ROW_BITS
        BNE DCT_CLEAR_LOOP
        LDX #CENTER_VRAM_ADDR
        LDAA CURRENT_TEXT_PTR
        ORAA CURRENT_TEXT_PTR+1
        BEQ DCT_APPLY_DONE
        STX STD_VRAM_PTR
        LDX CURRENT_TEXT_PTR
        JSR __STD_PRINT_STR       ; 0 終端の文字列を VRAM へコピー
DCT_APPLY_DONE:
        CLRA
        STAA DISPLAY_DIRTY
        RTS

SCAN_KEYBOARD:
        ; 今フレームの検出結果を初期化する。
        CLRA
        STAA NEW_TEXT_PTR
        STAA NEW_TEXT_PTR+1
        STAA KEY_FOUND
        CLR ROW_INDEX

SK_ROW_LOOP:
        LDAA ROW_INDEX
        CMPA #KEY_ROW_COUNT
        BNE SK_SCAN_ACTIVE
        JMP SK_POST_SCAN
SK_SCAN_ACTIVE:
        STAA STD_VIA_ORA           ; 行を選択
        JSR READ_ROW_STABLE        ; 同じ値を 2 回取得できた場合のみ採用
        STAA ROW_BITS
        BNE SK_BITS_READY
        JMP SK_NEXT_ROW
SK_BITS_READY:
        LDAA KEY_FOUND
        BEQ SK_DECODE_ROW
        JMP SK_POST_SCAN
SK_DECODE_ROW:
        LDAA ROW_INDEX
        JSR LOAD_ROW_PTR
        LDX ROW_PTR
        LDAA ROW_BITS
        BITA #$10
        BEQ SK_BIT3
        LDAA ,X
        JSR SET_SINGLE_CHAR
        BRA SK_FOUND
SK_BIT3:
        LDAA ROW_BITS
        BITA #$08
        BEQ SK_BIT2
        LDAA ROW_INDEX
        CMPA #8
        BEQ SK_STORE_RETURN
        LDAA 1,X
        JSR SET_SINGLE_CHAR
        BRA SK_FOUND
SK_STORE_RETURN:
        ; RETURN キーはラベル付き文字列をそのまま表示する。
        LDX #RETURN_TEXT
        STX NEW_TEXT_PTR
        BRA SK_FOUND
SK_BIT2:
        LDAA ROW_BITS
        BITA #$04
        BEQ SK_BIT1
        LDAA 2,X
        JSR SET_SINGLE_CHAR
        BRA SK_FOUND
SK_BIT1:
        LDAA ROW_BITS
        BITA #$02
        BEQ SK_BIT0
        LDAA ROW_INDEX
        CMPA #0
        BEQ SK_STORE_SHIFT
        CMPA #8
        BEQ SK_STORE_SPACE
        LDAA 3,X
        JSR SET_SINGLE_CHAR
        BRA SK_FOUND
SK_STORE_SHIFT:
        ; SHIFT 行 (row0 bit1) は "SHIFT" と表示する。
        LDX #SHIFT_TEXT
        STX NEW_TEXT_PTR
        BRA SK_FOUND
SK_STORE_SPACE:
        ; SPACE (row8 bit2) は大文字英字ではなく "SPACE" を表示する。
        LDX #SPACE_TEXT
        STX NEW_TEXT_PTR
        BRA SK_FOUND
SK_BIT0:
        LDAA ROW_BITS
        BITA #$01
        BNE SK_HANDLE_BIT0
        JMP SK_NEXT_ROW
SK_HANDLE_BIT0:
        LDAA ROW_INDEX
        CMPA #0
        BEQ SK_STORE_CTRL
        LDAA 4,X
        JSR SET_SINGLE_CHAR
        BRA SK_FOUND
SK_STORE_CTRL:
        ; CTRL (row0 bit0) も同様に専用文字列で表示する。
        LDX #CTRL_TEXT
        STX NEW_TEXT_PTR
        BRA SK_FOUND

SK_NEXT_ROW:
        INC ROW_INDEX
        JMP SK_ROW_LOOP

SK_FOUND:
        ; 最初に検出したキーだけ採用し、残りの行はスキップする。
        LDAA #1
        STAA KEY_FOUND
        JMP SK_POST_SCAN

SK_POST_SCAN:
        CLRA
        STAA STD_VIA_ORA
        LDAA KEY_FOUND
        BNE SK_APPLY_RESULT
        ; キーが見つからなかった場合は一定フレーム様子を見てから表示を消す。
        LDAA NO_KEY_FRAMES
        INCA
        STAA NO_KEY_FRAMES
        CMPA #NO_KEY_HOLD_FRAMES
        BCC SK_DONE_RETURN
        LDAA CURRENT_TEXT_PTR
        ORAA CURRENT_TEXT_PTR+1
        BEQ SK_CLEAR_RESET
        CLRA
        STAA CURRENT_TEXT_PTR
        STAA CURRENT_TEXT_PTR+1
        LDAA #1
        STAA DISPLAY_DIRTY
SK_CLEAR_RESET:
        CLRA
        STAA NO_KEY_FRAMES
        BRA SK_DONE_RETURN

SK_APPLY_RESULT:
        ; 表示中の内容と異なる場合のみポインタを更新する。
        CLRA
        STAA NO_KEY_FRAMES
        LDAA NEW_TEXT_PTR
        CMPA CURRENT_TEXT_PTR
        BNE SK_UPDATE_POINTER
        LDAA NEW_TEXT_PTR+1
        CMPA CURRENT_TEXT_PTR+1
        BNE SK_UPDATE_POINTER
        BRA SK_DONE_RETURN
SK_UPDATE_POINTER:
        LDAA NEW_TEXT_PTR
        STAA CURRENT_TEXT_PTR
        LDAA NEW_TEXT_PTR+1
        STAA CURRENT_TEXT_PTR+1
        LDAA #1
        STAA DISPLAY_DIRTY

SK_DONE_RETURN:
        RTS

READ_ROW_STABLE:
        ; 行選択を切り替えた直後の揺らぎを吸収するため、2 回連続で同じ値が読めた場合のみ採用する。
        LDAA STD_VIA_ORB
        EORA #$1F
        ANDA #$1F
        STAA ROW_TEMP
        NOP                     ; わずかな待機で配線の安定を待つ
        LDAA STD_VIA_ORB
        EORA #$1F
        ANDA #$1F
        CMPA ROW_TEMP
        BEQ RRS_DONE
        CLRA                    ; 値が揺れた場合は 0 (無入力) を返す
        RTS
RRS_DONE:
        RTS

; 約2ms待機 (CPUクロック 0.894MHz を前提とした概算)。
WAIT_2MS:
        LDX #$FA
W2_LOOP:
        NOP
        NOP
        NOP
        NOP
        DEX
        BNE W2_LOOP
        RTS

LOAD_ROW_PTR:
        PSHB
        STAA ROW_ITER
        LDX #KEY_ROW_PTRS
LRP_LOOP:
        LDAA ROW_ITER
        BEQ LRP_READY
        INX
        INX
        DEC ROW_ITER
        BRA LRP_LOOP
LRP_READY:
        LDAA 0,X
        STAA ROW_PTR
        LDAA 1,X
        STAA ROW_PTR+1
        PULB
        RTS

SET_SINGLE_CHAR:
        STAA SINGLE_CHAR_TEXT     ; 1 文字を単体の 0 終端文字列として保持
        CLRA
        STAA SINGLE_CHAR_TEXT+1
        LDX #SINGLE_CHAR_TEXT
        STX NEW_TEXT_PTR
        RTS

; --------------------------------------------------------------------------
; data tables

        .data
TITLE:  .ascii "JR-100 KEY DEMO\0"
PROMPT: .ascii "PRESS A KEY (RESULT AT 15,11)\0"

KEY_ROW_PTRS:
        .word KEY_ROW0
        .word KEY_ROW1
        .word KEY_ROW2
        .word KEY_ROW3
        .word KEY_ROW4
        .word KEY_ROW5
        .word KEY_ROW6
        .word KEY_ROW7
        .word KEY_ROW8

KEY_ROW0:
        .byte 'C','X','Z',$5E,$40
KEY_ROW1:
        .byte 'G','F','D','S','A'
KEY_ROW2:
        .byte 'T','R','E','W','Q'
KEY_ROW3:
        .byte '5','4','3','2','1'
KEY_ROW4:
        .byte '0','9','8','7','6'
KEY_ROW5:
        .byte 'P','O','I','U','Y'
KEY_ROW6:
        .byte $3B,'L','K','J','H'
KEY_ROW7:
        .byte $2C,'M','N','B','V'
KEY_ROW8:
        .byte $2D,$52,$3A,$20,$2E

SHIFT_TEXT:
        .ascii "SHIFT\0"
CTRL_TEXT:
        .ascii "CTRL\0"
SPACE_TEXT:
        .ascii "SPACE\0"
RETURN_TEXT:
        .ascii "RETURN\0"
SINGLE_CHAR_TEXT:
        .byte ' ', $00

        .code
