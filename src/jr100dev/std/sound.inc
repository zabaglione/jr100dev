; Cooperative JR-100 monophonic sound driver.
; Public routines clobber A, B, X, and CCR.
; Timer 1 is reserved for PB7 square-wave output and its interrupt is never enabled.

SOUND_VIA_ORB:       .equ $C800
SOUND_VIA_DDRB:      .equ $C802
SOUND_VIA_T1CL:      .equ $C804
SOUND_VIA_T1CH:      .equ $C805
SOUND_VIA_ACR:       .equ $C80B
SOUND_VIA_IFR:       .equ $C80D
SOUND_PB7_MASK:      .equ $80
SOUND_T1_IFR_MASK:   .equ $40
SOUND_T1_MODE_MASK:  .equ $C0
SOUND_MAX_PITCH:     .equ 48
SOUND_MAX_SFX_UNITS: .equ 200

.code

; Configure PB7 without altering any other Port B direction bits.
SOUND_INIT:
        LDAA SOUND_VIA_DDRB
        ORAA #SOUND_PB7_MASK
        STAA SOUND_VIA_DDRB
        LDAA #SOUND_T1_IFR_MASK
        STAA SOUND_VIA_IFR
        JMP SOUND_STOP

; X points to a BGM descriptor:
;   .word event_data
;   .byte event_count, loop_event_index
; loop_event_index $FF disables looping.
SOUND_PLAY_BGM:
        LDAA 2,X
        BNE SOUND_PLAY_BGM_HAS_EVENTS
        JMP SOUND_STOP
SOUND_PLAY_BGM_HAS_EVENTS:
        STAA SOUND_BGM_EVENT_COUNT
        STAA SOUND_BGM_EVENTS_LEFT
        LDAA 3,X
        STAA SOUND_BGM_LOOP_INDEX
        LDX ,X
        STX SOUND_BGM_EVENT_PTR
        LDAA SOUND_BGM_LOOP_INDEX
        CMPA #$FF
        BEQ SOUND_PLAY_BGM_NO_LOOP
        LDX SOUND_BGM_EVENT_PTR
        LDAB SOUND_BGM_LOOP_INDEX
SOUND_PLAY_BGM_FIND_LOOP:
        TSTB
        BEQ SOUND_PLAY_BGM_LOOP_READY
        INX
        INX
        DECB
        BRA SOUND_PLAY_BGM_FIND_LOOP
SOUND_PLAY_BGM_LOOP_READY:
        STX SOUND_BGM_LOOP_PTR
        LDAA SOUND_BGM_EVENT_COUNT
        SUBA SOUND_BGM_LOOP_INDEX
        STAA SOUND_BGM_LOOP_COUNT
        LDAA #$01
        STAA SOUND_BGM_LOOP_ENABLED
        BRA SOUND_PLAY_BGM_START
SOUND_PLAY_BGM_NO_LOOP:
        CLRA
        STAA SOUND_BGM_LOOP_ENABLED
        STAA SOUND_BGM_LOOP_COUNT
SOUND_PLAY_BGM_START:
        LDAA #$01
        STAA SOUND_BGM_ACTIVE
        JMP SOUND_LOAD_BGM_EVENT

; Advance the BGM by one game-owned tick.
SOUND_TICK:
        LDAA SOUND_BGM_ACTIVE
        BEQ SOUND_TICK_DONE
        LDAA SOUND_BGM_REMAINING
        BNE SOUND_TICK_DECREMENT
        JMP SOUND_LOAD_BGM_EVENT
SOUND_TICK_DECREMENT:
        DEC SOUND_BGM_REMAINING
        BNE SOUND_TICK_DONE
        JMP SOUND_LOAD_BGM_EVENT
SOUND_TICK_DONE:
        RTS

; X points to an SFX descriptor:
;   .byte event_count
;   .byte pitch, duration_in_10ms_units ...
; Playback is synchronous and hard-limited to 200 units.
SOUND_PLAY_SFX_BLOCKING:
        JSR SOUND_MUTE
        LDAB ,X
        STAB SOUND_SFX_EVENTS_LEFT
        INX
        STX SOUND_SFX_EVENT_PTR
        LDAA #SOUND_MAX_SFX_UNITS
        STAA SOUND_SFX_BUDGET
SOUND_PLAY_SFX_NEXT:
        LDAB SOUND_SFX_EVENTS_LEFT
        BEQ SOUND_PLAY_SFX_RESUME
        LDX SOUND_SFX_EVENT_PTR
        LDAA ,X
        STAA SOUND_SFX_PITCH
        LDAB 1,X
        STAB SOUND_SFX_DURATION
        INX
        INX
        STX SOUND_SFX_EVENT_PTR
        DEC SOUND_SFX_EVENTS_LEFT
        LDAA SOUND_SFX_PITCH
        JSR SOUND_SET_PITCH
SOUND_PLAY_SFX_WAIT:
        LDAA SOUND_SFX_DURATION
        BEQ SOUND_PLAY_SFX_NEXT
        LDAA SOUND_SFX_BUDGET
        BEQ SOUND_PLAY_SFX_RESUME
        DEC SOUND_SFX_DURATION
        DEC SOUND_SFX_BUDGET
        JSR SOUND_WAIT_10MS
        BRA SOUND_PLAY_SFX_WAIT
SOUND_PLAY_SFX_RESUME:
        LDAA SOUND_BGM_ACTIVE
        BEQ SOUND_STOP
        LDAA SOUND_BGM_PITCH
        JMP SOUND_SET_PITCH

; Stop BGM and silence PB7 while preserving all non-PB7 Port B bits.
SOUND_STOP:
        CLRA
        STAA SOUND_BGM_ACTIVE
        STAA SOUND_BGM_REMAINING
        STAA SOUND_BGM_PITCH
        STAA SOUND_OUTPUT_PITCH
        JMP SOUND_MUTE

; Mute PB7 without changing the lower six ACR bits or other ORB bits.
SOUND_MUTE:
        LDAA SOUND_VIA_ACR
        ANDA #$3F
        STAA SOUND_VIA_ACR
        LDAA SOUND_VIA_ORB
        ANDA #$7F
        STAA SOUND_VIA_ORB
        RTS

; A is a pitch index: 0 is rest and 1 through 48 address the reload table.
SOUND_SET_PITCH:
        TSTA
        BEQ SOUND_MUTE
        CMPA #SOUND_MAX_PITCH + 1
        BCS SOUND_SET_PITCH_VALID
        JMP SOUND_MUTE
SOUND_SET_PITCH_VALID:
        STAA SOUND_OUTPUT_PITCH
        JSR SOUND_MUTE
        LDAA SOUND_OUTPUT_PITCH
        DECA
        LDX #SOUND_NOTE_RELOADS
SOUND_SET_PITCH_SEEK:
        TSTA
        BEQ SOUND_SET_PITCH_WRITE
        INX
        INX
        DECA
        BRA SOUND_SET_PITCH_SEEK
SOUND_SET_PITCH_WRITE:
        LDAB 1,X
        STAB SOUND_VIA_T1CL
        LDAA ,X
        STAA SOUND_VIA_T1CH
        LDAA SOUND_VIA_ACR
        ANDA #$3F
        ORAA #SOUND_T1_MODE_MASK
        STAA SOUND_VIA_ACR
        RTS

; Load and apply the next BGM event.  Zero-length events become one tick.
SOUND_LOAD_BGM_EVENT:
        LDAA SOUND_BGM_EVENTS_LEFT
        BNE SOUND_LOAD_BGM_READ
        LDAA SOUND_BGM_LOOP_ENABLED
        BNE SOUND_LOAD_BGM_LOOP
        JMP SOUND_STOP
SOUND_LOAD_BGM_LOOP:
        LDX SOUND_BGM_LOOP_PTR
        STX SOUND_BGM_EVENT_PTR
        LDAA SOUND_BGM_LOOP_COUNT
        STAA SOUND_BGM_EVENTS_LEFT
SOUND_LOAD_BGM_READ:
        LDX SOUND_BGM_EVENT_PTR
        LDAA ,X
        STAA SOUND_BGM_PITCH
        LDAB 1,X
        BNE SOUND_LOAD_BGM_DURATION_READY
        LDAB #$01
SOUND_LOAD_BGM_DURATION_READY:
        STAB SOUND_BGM_REMAINING
        INX
        INX
        STX SOUND_BGM_EVENT_PTR
        DEC SOUND_BGM_EVENTS_LEFT
        LDAA SOUND_BGM_PITCH
        JMP SOUND_SET_PITCH

; Approximately 10ms at the documented 894kHz development clock.
SOUND_WAIT_10MS:
        LDX #$045D
SOUND_WAIT_10MS_LOOP:
        DEX
        BNE SOUND_WAIT_10MS_LOOP
        RTS

; C3 through B6. Values use round(894886.25 / (2 * Hz)) - 2.
SOUND_NOTE_RELOADS:
        .word $0D5A, $0C9B, $0BE5, $0B3A, $0A99, $0A00
        .word $0971, $08E9, $0869, $07F0, $077E, $0712
        .word $06AC, $064C, $05F2, $059C, $054B, $04FF
        .word $04B7, $0473, $0433, $03F7, $03BE, $0388
        .word $0355, $0325, $02F8, $02CD, $02A5, $027F
        .word $025B, $0239, $0219, $01FA, $01DE, $01C3
        .word $01AA, $0192, $017B, $0166, $0151, $013E
        .word $012C, $011B, $010B, $00FC, $00EE, $00E0

.bss

SOUND_BGM_EVENT_PTR:    .res 2
SOUND_BGM_LOOP_PTR:     .res 2
SOUND_SFX_EVENT_PTR:    .res 2
SOUND_BGM_EVENT_COUNT:  .res 1
SOUND_BGM_EVENTS_LEFT:  .res 1
SOUND_BGM_LOOP_INDEX:   .res 1
SOUND_BGM_LOOP_COUNT:   .res 1
SOUND_BGM_LOOP_ENABLED: .res 1
SOUND_BGM_ACTIVE:       .res 1
SOUND_BGM_REMAINING:    .res 1
SOUND_BGM_PITCH:        .res 1
SOUND_OUTPUT_PITCH:     .res 1
SOUND_SFX_EVENTS_LEFT:  .res 1
SOUND_SFX_BUDGET:       .res 1
SOUND_SFX_PITCH:        .res 1
SOUND_SFX_DURATION:     .res 1
