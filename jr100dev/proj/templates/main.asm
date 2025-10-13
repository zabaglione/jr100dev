        .org $0246
        .include "macro.inc"

START:  LDX #STD_VRAM_BASE
        PRINT_STR MESSAGE
        RTS

MESSAGE: .ascii "HELLO JR-100!\0"
