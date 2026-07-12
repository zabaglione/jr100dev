        .org $0300
        JMP MAIN

PCG_BASE:       .equ $C000
PCG_END:        .equ $C100
VRAM_BASE:      .equ $C100
VRAM_END:       .equ $C400
VIA_ORB:        .equ $C800
VIA_DDRB:       .equ $C802
PB5_MASK:       .equ $20
CLOCK_VRAM:     .equ VRAM_BASE + (11 * 32) + 12
DIGIT_BASE:     .equ $80
COLON_CHAR:     .equ $8A
DELAY_INNER:    .equ $DA37

; PCGを設定し、12:00:00を表示して時計ループへ入る。
MAIN:
        JSR SELECT_PCG_BANK
        JSR LOAD_PCG_DATA
        JSR CLEAR_SCREEN
        JSR RESET_CLOCK
        JSR DRAW_CLOCK

CLOCK_LOOP:
        JSR WAIT_ONE_SECOND
        JSR INCREMENT_CLOCK
        JSR DRAW_CLOCK
        BRA CLOCK_LOOP

; VIA PB5だけを出力かつHighにし、他のポート設定を保持する。
SELECT_PCG_BANK:
        LDAA VIA_DDRB
        ORAA #PB5_MASK
        STAA VIA_DDRB
        LDAA VIA_ORB
        ORAA #PB5_MASK
        STAA VIA_ORB
        RTS

; PCG_DATAからPCG領域全体へ256バイトを転送する。
LOAD_PCG_DATA:
        LDX #PCG_DATA
        STX PCG_SOURCE_PTR
        LDX #PCG_BASE
        STX PCG_TARGET_PTR

LOAD_PCG_LOOP:
        LDX PCG_SOURCE_PTR
        LDAA ,X
        INX
        STX PCG_SOURCE_PTR
        LDX PCG_TARGET_PTR
        STAA ,X
        INX
        STX PCG_TARGET_PTR
        CPX #PCG_END
        BNE LOAD_PCG_LOOP
        RTS

; 時計以外の表示を残さないようにVRAMを消去する。
CLEAR_SCREEN:
        LDX #VRAM_BASE
        CLRA

CLEAR_SCREEN_LOOP:
        STAA ,X
        INX
        CPX #VRAM_END
        BNE CLEAR_SCREEN_LOOP
        RTS

RESET_CLOCK:
        LDAA #$01
        STAA HOUR_TENS
        LDAA #$02
        STAA HOUR_ONES
        CLRA
        STAA MINUTE_TENS
        STAA MINUTE_ONES
        STAA SECOND_TENS
        STAA SECOND_ONES
        RTS

; 中央付近へPCG文字コードでHH:MM:SSを描画する。
DRAW_CLOCK:
        LDX #CLOCK_VRAM
        LDAA HOUR_TENS
        ADDA #DIGIT_BASE
        STAA ,X
        INX
        LDAA HOUR_ONES
        ADDA #DIGIT_BASE
        STAA ,X
        INX
        LDAA #COLON_CHAR
        STAA ,X
        INX
        LDAA MINUTE_TENS
        ADDA #DIGIT_BASE
        STAA ,X
        INX
        LDAA MINUTE_ONES
        ADDA #DIGIT_BASE
        STAA ,X
        INX
        LDAA #COLON_CHAR
        STAA ,X
        INX
        LDAA SECOND_TENS
        ADDA #DIGIT_BASE
        STAA ,X
        INX
        LDAA SECOND_ONES
        ADDA #DIGIT_BASE
        STAA ,X
        RTS

; 10進各桁を繰り上げ、24:00:00を00:00:00へ戻す。
INCREMENT_CLOCK:
        INC SECOND_ONES
        LDAA SECOND_ONES
        CMPA #$0A
        BNE INCREMENT_DONE
        CLR SECOND_ONES

        INC SECOND_TENS
        LDAA SECOND_TENS
        CMPA #$06
        BNE INCREMENT_DONE
        CLR SECOND_TENS

        INC MINUTE_ONES
        LDAA MINUTE_ONES
        CMPA #$0A
        BNE INCREMENT_DONE
        CLR MINUTE_ONES

        INC MINUTE_TENS
        LDAA MINUTE_TENS
        CMPA #$06
        BNE INCREMENT_DONE
        CLR MINUTE_TENS

        INC HOUR_ONES
        LDAA HOUR_TENS
        CMPA #$02
        BNE CHECK_HOUR_ONES
        LDAA HOUR_ONES
        CMPA #$04
        BNE INCREMENT_DONE
        CLR HOUR_TENS
        CLR HOUR_ONES
        BRA INCREMENT_DONE

CHECK_HOUR_ONES:
        LDAA HOUR_ONES
        CMPA #$0A
        BNE INCREMENT_DONE
        CLR HOUR_ONES
        INC HOUR_TENS

INCREMENT_DONE:
        RTS

; 6800標準サイクル数で、呼び出しを含む待ち時間を約894,000サイクルにする。
WAIT_ONE_SECOND:
        LDAA #$02

DELAY_OUTER_LOOP:
        LDX #DELAY_INNER

DELAY_INNER_LOOP:
        DEX
        BNE DELAY_INNER_LOOP
        DECA
        BNE DELAY_OUTER_LOOP
        RTS

HOUR_TENS:      .byte $00
HOUR_ONES:      .byte $00
MINUTE_TENS:    .byte $00
MINUTE_ONES:    .byte $00
SECOND_TENS:    .byte $00
SECOND_ONES:    .byte $00
PCG_SOURCE_PTR: .word $0000
PCG_TARGET_PTR: .word $0000

; スロット0-9は数字、スロット10はコロン。データはWebエディタのプリセットから生成する。
PCG_DATA:
        .include "pcg_data.inc"
