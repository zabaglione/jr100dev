; Blink every valid neighbor using only the four glyphs also used by fusion.
; Only the idle loop calls this: movement, fusion and dialogs own their frames.
PHASE_HINT_TICK:
    LDAA MODE
    CMPA #1
    BNE PHASE_HINT_DONE
    LDAA PHASE_FIRST
    CMPA #255
    BEQ PHASE_HINT_DONE
    LDAA TICK
    ANDA #16
    BEQ PHASE_HINT_DIM
    LDAA #5
    BRA PHASE_HINT_POSE
PHASE_HINT_DIM:
    LDAA #6
PHASE_HINT_POSE:
    LDAB #7
    LDX #FACE_7_FRAMES
    JMP N_FACE
PHASE_HINT_DONE:
    RTS
