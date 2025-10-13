        .org $0300
        JMP MAIN

        .include "macro.inc"

MAIN:   BEEP
        LDX #STD_VRAM_BASE
        PRINT_STR TITLE
        LDX #STD_VRAM_BASE + 32
        PRINT_STR PROMPT
        LDX #STD_VRAM_BASE + 64
        PRINT_STR LABEL
        LDX #STD_VRAM_BASE + 96
        PRINT_STR KEYMAP
        LDX #STD_VRAM_BASE + 128
        PRINT_STR KEYMAP2
        LDX #STD_VRAM_BASE + 32

INPUT_LOOP:
        SCAN_KEY
        CMPA #$00
        BEQ INPUT_LOOP

        STAA LAST_KEY
        PLA

SHOW_KEY:
        LDX #STD_VRAM_BASE + 96 + 16
        LDAA LAST_KEY
        JSR __STD_TO_VRAM
        STAA ,X

        LDX #STD_VRAM_BASE + 64
        PRINT_STR LABEL
        LDX #STD_VRAM_BASE + 96
        PRINT_STR KEYMAP
        LDX #STD_VRAM_BASE + 128
        PRINT_STR KEYMAP2
        BRA INPUT_LOOP

TITLE:  .ascii "JR-100 I/O DEMO\0"
PROMPT: .ascii "PRESS ANY KEY TO SEE CODE\0"
LABEL:  .ascii "LAST KEY CODE:\0"
KEYMAP: .ascii "0-9 -> 00-09  A-F -> 0A-0F\0"
KEYMAP2:.ascii "START/STOP -> 1C   SPACE -> 01\0"
LAST_KEY: .byte $00
