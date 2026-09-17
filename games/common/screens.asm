; X points to (length, value) runs; zero length terminates exactly 768 cells.
UNPACK_SCREEN:
    STX SRC
    LDX #FRAMEBUFFER
    STX DST
UNPACK_NEXT:
    LDX SRC
    LDAB 0,X
    BEQ UNPACK_DONE
    LDAA 1,X
    INX
    INX
    STX SRC
    LDX DST
UNPACK_RUN:
    STAA 0,X
    INX
    DECB
    BNE UNPACK_RUN
    STX DST
    JSR CLOCK_SERVICE
    BRA UNPACK_NEXT
UNPACK_DONE:
    RTS
