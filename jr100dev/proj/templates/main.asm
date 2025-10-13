        .org $0300
        JMP MAIN

        .include "macro.inc"

MAIN:   LDX #STD_VRAM_BASE
        PRINT_STR MESSAGE
        RTS

MESSAGE: .ascii "HELLO JR-100!\0"
