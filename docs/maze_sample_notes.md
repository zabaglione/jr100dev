# Maze サンプル開発メモ

本ドキュメントは `samples/maze` を実装する際に得たノウハウの記録です。以後のサンプル開発やデバッグ時に参照してください。

## 画面・文字コード関連
- VRAM の空白は `$40`、壁 `#` は `$03` を書き込む。内部マップでは ASCII `' '`／`'#'` を使い、VRAM へ転送する際に変換する（`MAZE_RENDER_VIEW` 参照）。
- ゴールセルはマップ上で常時 `'G'` に置き換え、移動判定では `' '` と `'G'` を通路として扱う。ゴール表示を変える際は `MAZE_OPEN_START_GOAL` と移動ルーチン両方を更新する。
- ゴール演出は既存画面を消さず、中央 3 行だけに空白＋「`G O A L !!!`」＋空白を描画する。開始列は `common.inc` の `GOAL_MSG_COL` で調整する。

## 入力・移動処理
- Z キー以外でのゴールメニューは廃止。`MAZE_CHECK_GOAL` でゴール検知後、演出 → 約 3 秒待機 → タイトル復帰の流れを一括で処理する。
- 移動判定は `'G'` を通路扱いにするため、`MAZE_HANDLE_MOVEMENT` で `' '` に加えて `'G'` を許可している。追加の地形を通過可能にしたい場合は同様の分岐を入れる。

## カウンタ・表示
- ステップ数は BCD 4 桁で管理。`MOVE_COUNT_LO` が 0 に戻ったときだけ上位桁を進める実装に修正済み（`MAZE_INCREMENT_STEPS`）。9999 歩まで表示できる。
- HUD の更新は `MAZE_DRAW_OVERLAY`（VRAM 最終行）で一括して行う。演出時に画面全体をクリアしないこと。

## ビルドと依存関係
- `src/common.inc` を変更した場合は再アセンブルが必須。Makefile に依存関係を追加したため、通常の `make` / `make build/maze.prg` で自動的に再ビルドされる。それでも挙動がおかしいときは `make clean && make build/maze.prg` を実行し直す。
- `maze_gen.asm` は `common.inc`/`maze_helpers.inc`/`macro.inc`/`ctl.inc`/`scroll.inc` に依存している。新たなインクルードファイルを追加した際は Makefile の `GEN_INC` へも追記する。

## テスト・デバッグ手順
- `make test`（内部では `tests/run_debug_checks.py`）で VRAM ダンプやゴール生成などのスモークテストを実行する。演出変更後も必ず通ることを確認する。
- 迷路挙動を個別に確認する場合は `external/pyjr100emu` の `jr100emu.debug_runner` を利用すると RAM/VRAM ダンプが容易。

## よくあったミスと回避策
- ゴール表示位置の定数変更後に再ビルドを忘れる → `common.inc` 変更後は必ず `make build/maze.prg` 以上を実行する。
- VRAM へ ASCII のまま書き込んで文字化け → `__STD_TO_VRAM` を通すこと。固定文字を置く場合も必ず JSR を挟む。
- カウンタが 99 でゼロリセットされる → 4 桁 BCD 実装を利用すること（既に修正済み）。

以後サンプルに類似処理を追加する際は、本メモと `samples/maze/src/` の実装をテンプレートとして活用してください。
