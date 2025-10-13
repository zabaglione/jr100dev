# 標準マクロ利用メモ

## 取り込み方法
- ソース先頭で `.include "macro.inc"` を記述すると `jr100dev/std/macro.inc` を展開できる。
- `.include` はソースファイルのディレクトリと `jr100dev/std/` を探索するため、追加設定は不要。

## 提供マクロ
- `PUT_CHAR` : A レジスタの値を `(X)` に書き込み、X をインクリメント。
- `PRINT_STR <label>` : VRAM アドレスを指す X を保存し、ラベルの 0 終端文字列を描画して X を更新。
- `CLR_VRAM` : VRAM (`$C100`〜`$C3FF`) をスペースでクリアし、X を先頭に戻す。
- `BEEP` : VIA (`$C800`) の PB7 をトグルしてビープを鳴らす。
- `SCAN_KEY` : VIA の下位ポートを使ってキーマトリクスを読み込む（低ニブルを選択→`$C800` から取得）。

## 常駐サブルーチンと変数
- サブルーチン `__STD_PRINT_STR` / `__STD_CLEAR_VRAM` / `__STD_BEEP` / `__STD_SCAN_KEY` を自動生成。
- ダイレクトページ $00F0〜$00F3 を内部ワーク（VRAM ポインタ／文字列ポインタ）として使用。
- 定数シンボル `STD_VRAM_BASE` / `STD_VRAM_END` / `STD_VIA_ORB` / `STD_VIA_ORA` / `STD_VIA_DDRB` / `STD_VIA_DDRA` を `.equ` で提供。

## 確認済みテスト
- `pytest jr100dev/tests/unit/test_macros.py`
