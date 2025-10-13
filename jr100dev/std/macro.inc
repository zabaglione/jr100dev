; JR-100 標準マクロ定義

STD_VRAM_BASE:   .equ $C100
STD_VRAM_END:    .equ $C400
STD_VIA_ORB:     .equ $C800
STD_VIA_ORA:     .equ $C801
STD_VIA_DDRB:    .equ $C802
STD_VIA_DDRA:    .equ $C803

STD_VRAM_PTR:    .equ $00F0
STD_SRC_PTR:     .equ $00F2

MACRO PUT_CHAR
        STAA ,X
        INX
ENDM

MACRO PRINT_STR PTR
        STX STD_VRAM_PTR
        LDX #\PTR
        JSR __STD_PRINT_STR
ENDM

MACRO CLR_VRAM
        JSR __STD_CLEAR_VRAM
ENDM

MACRO BEEP
        JSR __STD_BEEP
ENDM

MACRO SCAN_KEY
        JSR __STD_SCAN_KEY
ENDM

.code

__STD_PRINT_STR:   STX STD_SRC_PTR
__STD_PRINT_LOOP:  LDX STD_SRC_PTR
                    LDAA ,X
                    BEQ __STD_PRINT_DONE
                    INX
                    STX STD_SRC_PTR
                    LDX STD_VRAM_PTR
                    STAA ,X
                    INX
                    STX STD_VRAM_PTR
                    BRA __STD_PRINT_LOOP
__STD_PRINT_DONE:  LDX STD_VRAM_PTR
                    RTS

__STD_CLEAR_VRAM:  LDX #STD_VRAM_BASE
                    LDAA #' '
__STD_CLEAR_LOOP:  STAA ,X
                    INX
                    CPX #STD_VRAM_END
                    BNE __STD_CLEAR_LOOP
                    LDX #STD_VRAM_BASE
                    RTS

__STD_BEEP:        LDAA #$80
                    STAA STD_VIA_DDRB
                    LDAA #$80
                    STAA STD_VIA_ORB
                    LDAA #$00
                    STAA STD_VIA_ORB
                    RTS

__STD_SCAN_KEY:    LDAA #$0F
                    STAA STD_VIA_DDRA
                    LDAA #$00
                    STAA STD_VIA_DDRB
                    LDAA #$00
                    STAA STD_VIA_ORA
                    LDAA STD_VIA_ORB
                    RTS
