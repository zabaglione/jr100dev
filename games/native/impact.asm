; Blink just the struck 2x2 cell in VRAM. Shared enemy PCG is never inverted.
; N_RENDER has already constructed the contact state before it is removed.
N_IMPACT:
    JSR N_XY
    STX IMPACT_CELL
    LDAA IMPACT_CELL
    ADDA #$91
    STAA IMPACT_CELL
    JSR N_RENDER
    JMP SCENE_IMPACT
