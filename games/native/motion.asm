; Draw an intermediate logical state and hold it for A ticks (about 60 Hz).
; Rule locals live in distinct slots from draw locals; no rule is re-entered.
MOTION_TICKS: .equ $3338
MOTION_START: .equ $3339
MOTION_ACTIVE: .equ $333A
N_ANIMATE:
    STAA MOTION_TICKS
    INC MOTION_ACTIVE
    JSR N_RENDER
    LDAA TICK
    STAA MOTION_START
MOTION_VISIBLE:
    JSR CLOCK_SERVICE
    CLR KEY_PENDING
    LDAA TICK
    SUBA MOTION_START
    CMPA MOTION_TICKS
    BCS MOTION_VISIBLE
    CLR KEY_ACTION
    CLR MOTION_ACTIVE
    RTS
