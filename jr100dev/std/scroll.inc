; ---------------------------------------------------------------------------
; 汎用スクロール更新マクロ
; 
; STD_SCROLL_UPDATE ORX, ORY, PX, PY, MARGIN, RIGHT_BOUND, BOTTOM_BOUND,
;                    MAX_X, MAX_Y, DRAW_X, DRAW_Y
;
; - ORX/ORY:        現在のビュー原点 (書き換えられる)
; - PX/PY:          プレイヤー（あるいは追従対象）のワールド座標
; - MARGIN:         左上マージン（上下共通）
; - RIGHT_BOUND:    右側許容位置（VIEW_WIDTH - 1 - margin）
; - BOTTOM_BOUND:   下側許容位置（VIEW_HEIGHT - 1 - margin）
; - MAX_X/MAX_Y:    ビュー原点の最大値
; - DRAW_X/DRAW_Y:  ビュー内での描画座標（結果を書き込む）
;
; 呼び出し側は 8bit の値を前提としており、マクロは必要に応じて
; ビュー原点を前後へ調整してマージンを満たす。
; ---------------------------------------------------------------------------

MACRO STD_SCROLL_UPDATE ORX, ORY, PX, PY, MARGIN, RIGHT_BOUND, BOTTOM_BOUND, MAX_X, MAX_Y, DRAW_X, DRAW_Y

SSU_RECALC_X\@:
        LDAA \PX
        SUBA \ORX
        BPL SSU_STORE_X\@
        CLRA
        STAA \DRAW_X
        LDAA \PX
        STAA \ORX
        BRA SSU_AFTER_RECALC_X\@
SSU_STORE_X\@:
        STAA \DRAW_X
SSU_AFTER_RECALC_X\@:
        LDAA \DRAW_X
        CMPA \MARGIN
        BCC SSU_RIGHT_CHECK\@
        LDAA \ORX
        BEQ SSU_RIGHT_CHECK\@
        DECA
        STAA \ORX
        BRA SSU_RECALC_X\@

SSU_RIGHT_CHECK\@:
        LDAA \DRAW_X
        CMPA \RIGHT_BOUND
        BLS SSU_RECALC_Y\@
        LDAA \ORX
        CMPA \MAX_X
        BEQ SSU_RECALC_Y\@
        INCA
        STAA \ORX
        BRA SSU_RECALC_X\@

SSU_RECALC_Y\@:
        LDAA \PY
        SUBA \ORY
        BPL SSU_STORE_Y\@
        CLRA
        STAA \DRAW_Y
        LDAA \PY
        STAA \ORY
        BRA SSU_AFTER_RECALC_Y\@
SSU_STORE_Y\@:
        STAA \DRAW_Y
SSU_AFTER_RECALC_Y\@:
        LDAA \DRAW_Y
        CMPA \MARGIN
        BCC SSU_BOTTOM_CHECK\@
        LDAA \ORY
        BEQ SSU_BOTTOM_CHECK\@
        DECA
        STAA \ORY
        BRA SSU_RECALC_Y\@

SSU_BOTTOM_CHECK\@:
        LDAA \DRAW_Y
        CMPA \BOTTOM_BOUND
        BLS SSU_FINALIZE\@
        LDAA \ORY
        CMPA \MAX_Y
        BEQ SSU_FINALIZE\@
        INCA
        STAA \ORY
        BRA SSU_RECALC_Y\@

SSU_FINALIZE\@:
        LDAA \PX
        SUBA \ORX
        BPL SSU_FINAL_STORE_X\@
        CLRA
SSU_FINAL_STORE_X\@:
        STAA \DRAW_X
        LDAA \PY
        SUBA \ORY
        BPL SSU_FINAL_STORE_Y\@
        CLRA
SSU_FINAL_STORE_Y\@:
        STAA \DRAW_Y
ENDM
