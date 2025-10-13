        .org $0400
        .include "macro.inc"

        .public DRAW_MESSAGE

DRAW_MESSAGE:
        LDX #STD_VRAM_BASE + 32
        PRINT_STR MESSAGE
        RTS

MESSAGE: .ascii "DRAWN FROM MODULE\0"
