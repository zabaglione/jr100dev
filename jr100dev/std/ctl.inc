; High-level control structure and arithmetic macros for JR-100 DSL
;
; NOTE: ラベル名はユーザーが一意に指定する。例: `FOR0_TOP`, `FOR0_END`。

; --- Variable helpers ----------------------------------------------------

MACRO VAR8 NAME, INIT
\NAME:  .byte \INIT
ENDM

MACRO VAR16 NAME, INIT
\NAME:  .word \INIT
ENDM

MACRO VARZ NAME, SIZE
\NAME:  .res \SIZE
ENDM

; --- Arithmetic helpers ---------------------------------------------------

MACRO ADD8 TARGET, VALUE
        LDAA \TARGET
        ADDA \VALUE
        STAA \TARGET
ENDM

MACRO SUB8 TARGET, VALUE
        LDAA \TARGET
        SUBA \VALUE
        STAA \TARGET
ENDM

MACRO INC8 TARGET
        INC \TARGET
ENDM

MACRO DEC8 TARGET
        DEC \TARGET
ENDM

; --- FOR loop -------------------------------------------------------------

MACRO FOR_BEGIN TOP, END, VAR, START, LIMIT
        LDAA #\START
        STAA \VAR
\TOP:
        LDAA \VAR
        CMPA #\LIMIT
        BHI \END
ENDM

MACRO FOR_END TOP, END, VAR
        INC \VAR
        BRA \TOP
\END:
ENDM

; --- WHILE loop -----------------------------------------------------------

MACRO WHILE_BEGIN TOP
\TOP:
ENDM

MACRO WHILE_IF_ZERO END, ADDR
        LDAA \ADDR
        BEQ \END
ENDM

MACRO WHILE_END TOP, END
        BRA \TOP
\END:
ENDM

; --- IF statement ---------------------------------------------------------

MACRO IF_EQ END, ADDR, VALUE
        LDAA \ADDR
        CMPA #\VALUE
        BNE \END
ENDM

MACRO IF_NE END, ADDR, VALUE
        LDAA \ADDR
        CMPA #\VALUE
        BEQ \END
ENDM

MACRO IF_END END
\END:
ENDM
