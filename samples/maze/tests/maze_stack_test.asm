.org $0300

; 迷路スタック操作の最小テスト

RESULT_EMPTY_CHECK:              .equ $0600
RESULT_PEEK_STATUS:              .equ $0601
RESULT_PEEK_X:                   .equ $0602
RESULT_PEEK_Y:                   .equ $0603
RESULT_POP1_STATUS:              .equ $0604
RESULT_POP1_X:                   .equ $0605
RESULT_POP1_Y:                   .equ $0606
RESULT_POP2_STATUS:              .equ $0607
RESULT_PTR_RESET:                .equ $0608  ; 2 bytes
RESULT_PTR_AFTER_EMPTY:          .equ $060A  ; 2 bytes
RESULT_PTR_AFTER_PUSH:           .equ $060C  ; 2 bytes
RESULT_PTR_AFTER_POP1:           .equ $060E  ; 2 bytes
RESULT_PTR_AFTER_POP2:           .equ $0610  ; 2 bytes
RESULT_POP2_X:                   .equ $0612
RESULT_POP2_Y:                   .equ $0613
RESULT_EMPTY_POP_STATUS:         .equ $0614
RESULT_PTR_AFTER_EMPTY_POP:      .equ $0615  ; 2 bytes

STACK_BASE_ADDR: .equ $0500
STACK_CAPACITY:  .equ $0010
STACK_LIMIT:     .equ (STACK_BASE_ADDR + STACK_CAPACITY)

STACK_PTR:       .equ (STACK_BASE_ADDR + STACK_CAPACITY)
CUR_CELL_POS:    .equ (STACK_PTR + 2)
NEXT_CELL_POS:   .equ (CUR_CELL_POS + 2)

; --- テスト本体 ---------------------------------------------------------

START:
        ; スタックバッファをダミー値で埋める
        LDX #STACK_BASE_ADDR
        LDAA #$EE
FILL_LOOP:
        STAA 0,X
        INX
        CPX #STACK_LIMIT
        BNE FILL_LOOP

        JSR STACK_RESET
        LDX STACK_PTR
        STX RESULT_PTR_RESET

        JSR STACK_PEEK_CUR
        BCC EMPTY_FAIL
        LDAA #1
        STAA RESULT_EMPTY_CHECK
        BRA AFTER_EMPTY_CHECK
EMPTY_FAIL:
        CLR RESULT_EMPTY_CHECK
AFTER_EMPTY_CHECK:
        LDX STACK_PTR
        STX RESULT_PTR_AFTER_EMPTY

        ; (1,2) を push
        LDAA #1
        STAA CUR_CELL_POS
        LDAA #2
        STAA CUR_CELL_POS+1
        JSR STACK_PUSH_CUR

        ; (3,4) を push
        LDAA #3
        STAA CUR_CELL_POS
        LDAA #4
        STAA CUR_CELL_POS+1
        JSR STACK_PUSH_CUR

        LDX STACK_PTR
        STX RESULT_PTR_AFTER_PUSH

        CLR CUR_CELL_POS
        CLR CUR_CELL_POS+1

        ; top を peek
        JSR STACK_PEEK_CUR
        BCS PEEK_FAIL
        LDAA #1
        STAA RESULT_PEEK_STATUS
        LDAA CUR_CELL_POS
        STAA RESULT_PEEK_X
        LDAA CUR_CELL_POS+1
        STAA RESULT_PEEK_Y
        BRA AFTER_PEEK
PEEK_FAIL:
        CLR RESULT_PEEK_STATUS
        CLR RESULT_PEEK_X
        CLR RESULT_PEEK_Y
AFTER_PEEK:

        ; pop 1 回目（3,4 のはず）
        JSR STACK_POP_TO_CUR
        BCS POP1_FAIL
        LDAA #1
        STAA RESULT_POP1_STATUS
        LDAA CUR_CELL_POS
        STAA RESULT_POP1_X
        LDAA CUR_CELL_POS+1
        STAA RESULT_POP1_Y
        BRA AFTER_POP1
POP1_FAIL:
        CLR RESULT_POP1_STATUS
        CLR RESULT_POP1_X
        CLR RESULT_POP1_Y
AFTER_POP1:
        LDX STACK_PTR
        STX RESULT_PTR_AFTER_POP1

        ; pop 2 回目（1,2 のはず）
        JSR STACK_POP_TO_CUR
        BCS POP2_FAIL
        LDAA #1
        STAA RESULT_POP2_STATUS
        LDAA CUR_CELL_POS
        STAA RESULT_POP2_X
        LDAA CUR_CELL_POS+1
        STAA RESULT_POP2_Y
        BRA AFTER_POP2
POP2_FAIL:
        CLR RESULT_POP2_STATUS
        CLR RESULT_POP2_X
        CLR RESULT_POP2_Y
AFTER_POP2:
        LDX STACK_PTR
        STX RESULT_PTR_AFTER_POP2

        ; 空スタックでさらに pop して Carry=1 か確認
        JSR STACK_POP_TO_CUR
        BCC EMPTY_POP_FAIL
        LDAA #1
        STAA RESULT_EMPTY_POP_STATUS
        BRA AFTER_EMPTY_POP
EMPTY_POP_FAIL:
        CLR RESULT_EMPTY_POP_STATUS
AFTER_EMPTY_POP:
        LDX STACK_PTR
        STX RESULT_PTR_AFTER_EMPTY_POP

HALT:
        BRA HALT

; --- スタック操作 (maze_gen.asm と整合) --------------------------------

STACK_RESET:
        LDX #STACK_BASE_ADDR
        STX STACK_PTR
        RTS

STACK_PUSH_CUR:
        LDX STACK_PTR
        LDAA CUR_CELL_POS
        STAA 0,X
        INX
        LDAA CUR_CELL_POS+1
        STAA 0,X
        INX
        STX STACK_PTR
        RTS

STACK_PEEK_CUR:
        LDX STACK_PTR
        CPX #STACK_BASE_ADDR
        BEQ STACK_PEEK_EMPTY
        DEX
        LDAA 0,X
        STAA CUR_CELL_POS+1
        DEX
        LDAA 0,X
        STAA CUR_CELL_POS
        CLC
        RTS
STACK_PEEK_EMPTY:
        SEC
        RTS

STACK_POP_TO_CUR:
        LDX STACK_PTR
        CPX #STACK_BASE_ADDR
        BEQ STACK_POP_EMPTY
        DEX
        DEX
        STX STACK_PTR
        LDAA 1,X
        STAA CUR_CELL_POS+1
        LDAA 0,X
        STAA CUR_CELL_POS
        CLC
        RTS
STACK_POP_EMPTY:
        SEC
        RTS
