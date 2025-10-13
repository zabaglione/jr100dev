        .org $0300
        JMP MAIN

        .include "macro.inc"

MAIN:   BEEP
        LDX #STD_VRAM_BASE
        PRINT_STR PROMPT
WAIT:   SCAN_KEY
        CMPA #$00
        BEQ WAIT
        BRA MAIN

PROMPT: .ascii "PRESS ANY KEY\0"
