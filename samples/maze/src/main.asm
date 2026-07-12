        .org $0300

; メインループは `maze_gen.asm` 内の MAZE_MAIN に処理を委譲し、
; プレイ終了時も即座に再スタートする構成としている。
START:
        JSR MAZE_MAIN
        BRA START
