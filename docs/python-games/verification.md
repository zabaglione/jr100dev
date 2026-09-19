# 開発キットの検証記録

2026-09-19、macOS / Python 3.12.11、ローカルの pyjr100emu C++ コアで確認しました。この記録は開発キット導入時の検証であり、今後生成する任意のゲームに対する合格証明ではありません。

| 対象 | 結果 |
| --- | --- |
| 新規の単体・統合テスト | 41 件合格。構文・行番号、未初期化、再帰、8 ビット中間値、ループ、JSON、境界、古い証拠の拒否、配置失敗時の復元、HTTP 上の改変検出など |
| 空のフォルダーからの生成 | `init` → `release --web-root` が合格。検査、ビルド、入力テスト、撮影、配布、配置まで実行 |
| エラー → 修正 | 300 の代入を導入すると指定行で失敗。修正後に再実行して合格。誤った宝石数の期待値は REPLAY エラーとして検出 |
| 雛形の入力検証 | 3 シナリオ×2 入力系統、追加 160 混合入力。全 2 面クリア、棘で失敗、再挑戦、リセット取消・確定、壁、時刻更新 |
| メモリ | コードと固定データ 5,417 バイト、標準 RAM 16 KB、PCG 32 文字、スタック予約 512 バイト |
| 実 ROM での撮影 | BASIC 経由で起動。ホストによる状態書き換え 0。25.2 秒の等速 MP4、title/play/clear/ending の 4 PNG |
| 画像・動画 | 文字あふれを修正し画像を確認。ブラウザーで動画の終端まで再生。映像・音声ストリームと非無音 PCM を検査。音の聴覚評価は未実施 |
| 配布物 | PRG、PNG、MP4、プロジェクトソース ZIP、ライセンス、紹介ページ、検証記録。ROM とローカルパスを同梱しないことを確認 |
| HTTP 配信 | localhost の配信先で `verify-published` が合格。インターネットへの公開は未実施 |
| 既存ゲーム | 導入前 `9cf3732` の 51 作品を各 Makefile で再ビルド。PRG の SHA-256 は全件一致 |
| 共通演算 | 既存 `native/check_compiler.py` の 56 境界ケースが合格 |
| 既存の動作回帰 | ECHO PARRY と ABYSS SIGNAL の `make test` が合格。全 51 作品の動作テストを今回やり直したわけではない |
| 実機 | この新規雛形の SS1 / オリジナル JR-100 は未確認 |

再確認するコマンド:

```sh
make devkit-test PYTHON=.venv/bin/python
PYTHONPATH=src .venv/bin/python games/native/check_compiler.py
make -C games/echo_parry test
make -C games/abyss_signal test
```

再生成したサンプル、配置先、記録はローカルの `build/devkit-demo/`、既存 51 本の比較結果は `build/devkit-existing-games-regression.json` に保存しました。どちらも Git 管理外の生成物です。任意のマシンでは [入門手順](README.md)から新しいプロジェクトを作って検証してください。
