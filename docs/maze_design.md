# JR-100 迷路ゲーム設計メモ（壁伸ばし法）

## 現状仕様
- マップサイズはレベルに応じて可変。`EASY`: 11×11、`NORMAL`: 21×21、`HARD`: 41×41。ワーク領域は最大サイズ (41×41) で確保している。
- タイトル画面 (`MAZE_TITLE_MENU`) で I/M キーによるレベル選択、Z キーで開始。選択中の行は 0.5 秒間隔で反転表示と通常表示を繰り返す。
- ループエントリ: `samples/maze/src/main.asm` → `MAZE_MAIN`。タイトルメニュー → `MAZE_GENERATE` → `MAZE_RUN` を繰り返す。`R` キーで同レベルを再スタート。
- 生成ルーチン: `samples/maze/src/maze_gen.asm`。壁伸ばし法を実行時に回し、`CUR_CHAR_W/H` に基づいてセル数・マップ長を算出してから掘削する。プリセットデータは使用しない。
- ワーク領域: `samples/maze/src/maze_data.asm` が `.org $0600` から確保。最大サイズ分の `MAZE_MAP`・`MAZE_CELLS`・`VISITED_MAP`・スタックをまとめて保持する。
- スタート位置は左上内側 (`1,1`)、ゴールはレベル毎に (`width-2`,`height-2`) を設定。`HUD_STEPS_BUF` に移動回数を BCD 表示する。
- `HARD` レベルのみビューポートを 32×23 とし、スクロールマージンを 2 キャラに設定。`EASY`/`NORMAL` はマップ全体を表示する。

## データ構造
- `MAZE_MAP` (最大 41×41 bytes @ $0600): 壁は `'#'`, 通路は `' '`。描画時は `CUR_CHAR_W/H` とビュー幅 (`VIEW_CHAR_W/H`) を参照する。
- `MAZE_CELLS`, `VISITED_MAP`, `STACK_BASE` は最大セル数 (20×20) を想定して確保。動的にセル数を計算してループを回す。
- レベル設定 (`MAZE_LEVEL_PARAMS`): `[char_w, char_h, view_w, view_h, scroll_margin]` を 1 レコードとし、メニュー選択時に適用する。
- メニュー描画補助: 選択行・点滅制御 (`MENU_*` 系変数)、表示中テキストポインタ (`CURRENT_TEXT_PTR`) などを `maze_data.asm` に集約。

## 迷路生成フロー
1. `MAZE_APPLY_LEVEL`
   - レベル設定テーブルを読み、`CUR_CHAR_W/H` とビュー関連値を更新。マップサイズ・セル数は 16bit 加算で算出。
2. `MAZE_INIT`
   - `CUR_CHAR_W/H` を使って `MAZE_MAP` を `'#'` で埋め、`CUR_CELL_W/H` に基づき `MAZE_CELLS` を `0x0F`、`VISITED_MAP` を 0 で初期化。
3. `STACK_RESET` でスタックポインタをリセットし、スタートセル (0,0) を訪問済みにして push。
4. `MG_GROW_LOOP`
   - `FIND_NEIGHBORS` で未訪問の隣接セルを列挙。
   - 候補があれば `CHOOSE_AND_ADVANCE` → `CARVE_CUR_CELL` で通路を掘り、`NEXT_CELL_POS` をスタックに積んで次セルへ移動。
   - 候補が無ければ `STACK_POP_TO_CUR` でバックトラックし、スタックが空になるまで続行。
5. ゴールとスタート周辺を `MAZE_OPEN_START_GOAL` で空け、描画フェーズへ移行。

## 疑似乱数
- シード: `RNG_SEED` 初期値 `$5A`。
- 更新式: `seed = (seed * 5 + 1) mod 256` を `ASL` + `ADD` の組み合わせで実装。
- 方角選択は拒否法（`seed < count` になるまで再抽選）で行う。

## メモリマップ
- データ領域 (`maze_data.asm`) は $0600〜 に連続して確保。最大マップを前提にすることでレベル切り替え時の再配置を避けている。
- コード領域 (`maze_gen.asm`, `macro.inc`) は $2000〜。タイトルメニューや入力処理も同一セクションに含める。
- ビルド手順やテスト手順は README を参照 (`make -C samples/maze`, `make -C samples/maze test`)。

## 今後の課題
- レベル追加時に必要なメモリサイズを整理し、`maze_data.asm` のワーク領域を動的に割り振れる仕組みを検討する。
- FALSE キーリピート（I/M/Z）周りのデバウンス時間をより正確に計測し、実機での操作感を確認する。
- スクロール制御値のチューニング（特に HARD レベルのマージン調整）と HUD 表示の拡張。
