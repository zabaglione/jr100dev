; Ambient movement completes atomically, retaining the next key for dispatch.
; Unlike an impact/result hold, normal travel must not swallow steering or pause.
N_GLIDE:
    STAA MOTION_TICKS
    LDAA TICK
    STAA MOTION_CLOCK
    INC MOTION_ACTIVE
    JSR N_RENDER
    LDAA TICK
    STAA MOTION_START
GLIDE_VISIBLE:
    JSR CLOCK_SERVICE
    LDAA TICK
    SUBA MOTION_START
    CMPA MOTION_TICKS
    BCS GLIDE_VISIBLE
    CLR MOTION_ACTIVE
    LDAA MOTION_CLOCK
    STAA TICK
    RTS
