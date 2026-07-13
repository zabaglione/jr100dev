        .org $0300
        JMP MAIN

DEMO_PCG_BASE:      .equ $C000
DEMO_VRAM_BASE:     .equ $C100
DEMO_PCG_VRAM:      .equ $C180
DEMO_VIA_ORB:       .equ $C800
DEMO_VIA_ORA:       .equ $C801
DEMO_VIA_DDRB:      .equ $C802
DEMO_VIA_DDRA:      .equ $C803
DEMO_PB5_MASK:      .equ $20
DEMO_KEY_ROW_MASK:  .equ $0F

        .include "sound.inc"
        .include "sound_assets.inc"

        .data
DEMO_PCG_DATA:
        .byte $3C, $42, $A5, $81, $A5, $99, $42, $3C
        .byte $00, $18, $3C, $7E, $7E, $3C, $18, $00

        .bss
DEMO_PCG_SOURCE:    .res 2
DEMO_PCG_TARGET:    .res 2
DEMO_KEYS_NOW:      .res 1
DEMO_KEYS_PREVIOUS: .res 1
DEMO_LAST_ACTION:   .res 1
DEMO_SFX_COUNT:     .res 1

        .code
MAIN:
        LDS #$02FF
        JSR SOUND_INIT
        JSR DEMO_ENABLE_PCG
        JSR DEMO_LOAD_PCG
        JSR DEMO_DRAW_SCREEN
        LDX #SOUND_BGM_ODE_TO_JOY_OPENING
        JSR SOUND_PLAY_BGM

DEMO_LOOP:
        JSR SOUND_TICK
        JSR DEMO_SCAN_KEYS
        JSR DEMO_HANDLE_KEYS
        JSR DEMO_WAIT_TICK
        BRA DEMO_LOOP

; PB5 selects the PCG plane while PB7 stays owned by the sound driver.
DEMO_ENABLE_PCG:
        LDAA DEMO_VIA_DDRB
        ORAA #DEMO_PB5_MASK
        STAA DEMO_VIA_DDRB
        LDAA DEMO_VIA_ORB
        ORAA #DEMO_PB5_MASK
        STAA DEMO_VIA_ORB
        RTS

; Copy two glyphs to slots $80 and $81 in the PCG RAM.
DEMO_LOAD_PCG:
        LDX #DEMO_PCG_DATA
        STX DEMO_PCG_SOURCE
        LDX #DEMO_PCG_BASE
        STX DEMO_PCG_TARGET
        LDAB #16
DEMO_LOAD_PCG_LOOP:
        LDX DEMO_PCG_SOURCE
        LDAA ,X
        INX
        STX DEMO_PCG_SOURCE
        LDX DEMO_PCG_TARGET
        STAA ,X
        INX
        STX DEMO_PCG_TARGET
        DECB
        BNE DEMO_LOAD_PCG_LOOP
        RTS

; Draw two PCG characters so that PB5 coexistence is observable.
DEMO_DRAW_SCREEN:
        LDAA #$80
        STAA DEMO_PCG_VRAM
        LDAA #$81
        STAA DEMO_PCG_VRAM + 1
        RTS

; Scan keyboard row 0 through PB0-PB4 without changing PB5 or PB7.
DEMO_SCAN_KEYS:
        LDAA DEMO_VIA_DDRA
        ORAA #DEMO_KEY_ROW_MASK
        STAA DEMO_VIA_DDRA
        CLRA
        STAA DEMO_VIA_ORA
        LDAA DEMO_VIA_ORB
        EORA #$1F
        ANDA #$1F
        RTS

; Edge-triggered controls on row 0: bit0 SFX, bit1 second BGM,
; bit2 first BGM, bit3 stop. This keeps a held key from restarting audio.
DEMO_HANDLE_KEYS:
        STAA DEMO_KEYS_NOW
        EORA DEMO_KEYS_PREVIOUS
        LDAB DEMO_KEYS_NOW
        STAB DEMO_KEYS_PREVIOUS
        ANDA DEMO_KEYS_NOW
        BEQ DEMO_HANDLE_DONE
        BITA #$01
        BNE DEMO_HANDLE_SFX
        BITA #$02
        BNE DEMO_HANDLE_BGM_TWO
        BITA #$04
        BNE DEMO_HANDLE_BGM_ONE
        BITA #$08
        BNE DEMO_HANDLE_STOP
DEMO_HANDLE_DONE:
        RTS

DEMO_HANDLE_SFX:
        LDAA #$01
        STAA DEMO_LAST_ACTION
        LDX #SOUND_SFX_BLIP
        JSR SOUND_PLAY_SFX_BLOCKING
        INC DEMO_SFX_COUNT
        LDAA DEMO_SFX_COUNT
        ANDA #$01
        ADDA #$80
        STAA DEMO_PCG_VRAM
        RTS

DEMO_HANDLE_BGM_TWO:
        LDAA #$02
        STAA DEMO_LAST_ACTION
        LDX #SOUND_BGM_AH_VOUS_DIRAIJE_OPENING
        JSR SOUND_PLAY_BGM
        RTS

DEMO_HANDLE_BGM_ONE:
        LDAA #$03
        STAA DEMO_LAST_ACTION
        LDX #SOUND_BGM_ODE_TO_JOY_OPENING
        JSR SOUND_PLAY_BGM
        RTS

DEMO_HANDLE_STOP:
        LDAA #$04
        STAA DEMO_LAST_ACTION
        JSR SOUND_STOP
        RTS

; Approximately one 60Hz update at the 894kHz development clock.
DEMO_WAIT_TICK:
        LDX #$0746
DEMO_WAIT_TICK_LOOP:
        DEX
        BNE DEMO_WAIT_TICK_LOOP
        RTS
