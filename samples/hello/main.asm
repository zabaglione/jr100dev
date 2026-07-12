        .org $0300

; 起動直後に ASCII コード 'A' を読み込み、VRAM 先頭へ書き出して終了するだけの最小サンプル。
START:  LDAA #$41
        STAA $C100
        RTS
