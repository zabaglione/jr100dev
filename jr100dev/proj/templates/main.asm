        .org $0300
        .include "macro.inc"

START:  LDX #STD_VRAM_BASE
        PRINT_STR MESSAGE
        RTS

MESSAGE: .ascii "HELLO JR-100!\0"
