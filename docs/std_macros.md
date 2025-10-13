# 標準マクロ利用メモ

## 取り込み方法
- ソース先頭で `.include "macro.inc"` を記述すると `jr100dev/std/macro.inc` を展開できる。`jr100dev new` で生成される `src/main.asm` も `.org $0300` から開始する。
- 制御構造マクロを使用する場合は `.include "ctl.inc"` も併記する。
- `.include` はソースファイルのディレクトリと `jr100dev/std/` を探索するため、追加設定は不要。

## 提供マクロ
- `PUT_CHAR` : A レジスタの値を `(X)` に書き込み、X をインクリメント。
- `PRINT_STR <label>` : VRAM アドレスを指す X を保存し、ラベルの 0 終端文字列 (ASCII) を VRAM 文字コードへ変換して描画。
- `CLR_VRAM` : VRAM (`$C100`〜`$C3FF`) をスペースでクリアし、X を先頭に戻す。
- `BEEP` : VIA (`$C800`) の PB7 をトグルしてビープを鳴らす。
- `SCAN_KEY` : VIA の下位ポートを使ってキーマトリクスを読み込む（低ニブルを選択→`$C800` から取得）。

## 常駐サブルーチンと変数
- サブルーチン `__STD_PRINT_STR` / `__STD_CLEAR_VRAM` / `__STD_BEEP` / `__STD_SCAN_KEY` / `__STD_TO_VRAM` を自動生成。
- ワーク領域（`STD_VRAM_PTR` / `STD_SRC_PTR`）はマクロ内で `.bss` に確保されるため、BASIC ワーク RAM を汚さない。
- 定数シンボル `STD_VRAM_BASE` / `STD_VRAM_END` / `STD_VIA_ORB` / `STD_VIA_ORA` / `STD_VIA_DDRB` / `STD_VIA_DDRA` を `.equ` で提供。

## 制御構造マクロ（`ctl.inc`）
- `VAR8/VAR16/VARZ` : 8bit/16bit 変数または未初期化領域を宣言するヘルパー。
- `FOR_BEGIN label_top, label_end, var, start, limit` と `FOR_END label_top, label_end, var` : 基本的な for ループ。`label_*` でユニークなラベルを指定する。
- `WHILE_BEGIN label_top` / `WHILE_IF_ZERO label_end, addr` / `WHILE_END label_top, label_end` : 条件が 0 であれば抜ける while ループ。条件値の計算は利用者側で行う。
- `IF_EQ label_end, addr, value` / `IF_NE ...` / `IF_END label_end` : 単純な if 判定。
- `ADD8/SUB8/INC8/DEC8` : 8bit 変数に対する四則演算ヘルパー。即値を渡す場合は `#` を付ける。

## 確認済みテスト
- `pytest jr100dev/tests/unit/test_macros.py`
- `pytest jr100dev/tests/unit/test_ctl_macros.py`
