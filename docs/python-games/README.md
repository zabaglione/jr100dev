# Python で JR-100 ゲームを作る

この開発キットは、Python に似た小さな言語でルールを書き、JR-100 の機械語 PRG を作ります。Python が動くのは開発 PC だけです。標準 RAM 16 KB、画面 32×24 文字、PCG 32 文字、単音という条件は変わりません。

新作では **`games/dev.py` を入口にします**。初期化、構文検査、ビルド、入力テスト、画像・動画の撮影、配布物の生成、ローカル Web 配置を同じコマンド体系で行えます。既存 51 作品の配置・ルール・Makefile はそのまま使います。アセンブリ用の `jr100dev new` とは別の入口です。

## 最初の準備

以下は SDK のルートディレクトリで実行します。Python 3.9 以上を使います。検証に用いた環境は macOS / Python 3.12 / C++20 / ffmpeg です。Windows のネイティブ実行は未検証です。

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test,media]'
```

| 作業 | 必要なもの | 理由 |
| --- | --- | --- |
| 初期化・構文検査・ビルド | Python とこの SDK | Python ソースから機械語を作る |
| エミュレーターでテスト | C++20 コンパイラー、[pyjr100emu](https://github.com/zabaglione/pyjr100emu) のソース | 実際の MB8861H 命令を実行する |
| 画像・動画を撮影 | 上記、Pillow、ffmpeg / ffprobe、自分が使用権を持つ BASIC ROM | 本物の文字 ROM と音で撮影する |
| 配布物を配置 | 書き込み可能な Web 公開用ディレクトリ | PRG・画像・動画・ソースをまとめる |

macOS のコンパイラーは `xcode-select --install`、ffmpeg は利用しているパッケージ管理ツールで導入できます。エミュレーターは隣接フォルダー等に取得し、パスを指定します。ROM は配布物に入れません。

```sh
git clone https://github.com/zabaglione/pyjr100emu.git ../jr100emu
export JR100EMU_ROOT="$PWD/../jr100emu"
.venv/bin/python games/dev.py doctor
```

`PASS [doctor]` なら操作テストの準備ができています。`MISSING` があれば、その行の `fix` に従います。ROM がなくてもビルドとテストまでは進められます。

## 最初のゲームを作る

```sh
.venv/bin/python games/dev.py init games/my_first_game --id my-first-game --title "CRYSTAL TRAIL"
.venv/bin/python games/dev.py test games/my_first_game
```

2 面の探索ゲームが生成されます。宝石を 2 個集め、棘を避け、歩数が尽きる前に門に到達する遊びです。初期状態からクリア・失敗・再挑戦を試せるため、まずルールを一箇所変えて、画面とテストがどう変わるかを確認してください。既存フォルダーの上書きや、公開ゲーム一覧への登録は行いません。

`PASS [test]` は、構文とメモリ配置の検査に加え、エミュレーター上で入力列と期待値が一致したことを表します。実機の動作確認ではありません。

```text
my_first_game/
  game.json           タイトル、バージョン、速度、操作説明
  src/rules.py        init / act / tick / draw とゲームのルール
  levels.json         各面に渡す最大 128 バイトのデータ
  art.json            PCG スプライト、タイトル、BGM・効果音
  tests/replay.json   入力列、独立した期待値、撮影する場面
  GAME_DESIGN.md      遊びの設計と出荷前チェック
  AGENTS.md           別の生成 AI へ引き継ぐ指針
  Makefile            共通コマンドの短縮入口
  README.md           作品の操作と編集箇所
  build/              生成物。手で編集せず、Git 管理にも入れない
```

`games/library.json`、共通の絵柄一覧、共通の攻略スクリプトを編集する必要はありません。SDK 外にも作成できます。その場合は `dev.py` の絶対パスを使うか、`make JR100DEV_ROOT=/path/to/jr100dev test` と指定します。

## 編集 → 検査 → 修正

1. `GAME_DESIGN.md` に「何を判断して、何をすると成功・失敗するか」を書きます。
2. `src/rules.py` を編集します。最初は `init()` の歩数や `act()` の結果を変える程度にします。
3. `check` で未対応の構文、引数、配列範囲、アセット形式を検査します。
4. `test` で機械語と Python のモデルを比較し、入力に対する具体的な期待値も確認します。
5. 失敗したら表示されたファイル・行・`Fix` を読み、元のソースを修正して同じコマンドを再実行します。

```sh
.venv/bin/python games/dev.py check games/my_first_game
.venv/bin/python games/dev.py test games/my_first_game
```

例えば `s.steps = 300` は 1 バイトに入りません。`LANGUAGE` エラーがその行を示します。値を 0〜255 に直して再実行します。配列の上限を広げたり、テストの期待値を実装の値へ機械的に置き換えたりして隠さないでください。

AI や CI からは JSON で結果を受け取れます。失敗時の終了コードは 1 です。

```sh
.venv/bin/python games/dev.py --json test games/my_first_game
```

`build/devkit/report.json` に段階・結果・エラー、`run.log` にビルド出力と詳細な例外を保存します。ゲームの修正を自動で推測する機能はありません。生成 AI はこの結果を読んで修正し、再実行するループを担当します。[AI 用の制作指示書](ai-workflow.md)を渡してください。

## 撮影から配置までを 1 回で実行する

```sh
.venv/bin/python games/dev.py doctor --capture --rom /path/to/owned-rom.prg
.venv/bin/python games/dev.py release games/my_first_game --rom /path/to/owned-rom.prg --web-root /path/to/web
```

`release` は **検査 → ビルド → テスト → 実 ROM 起動 → 撮影 → 配布物生成 → 指定先への配置と照合**を順に行います。途中で失敗した場合は、その先へ進みません。`--web-root` を省略すると配布フォルダーの生成までです。`JR100_ROM` 環境変数でも ROM を指定できます。

| コマンド | 到達点 |
| --- | --- |
| `check PROJECT` | ソース・アセット・リプレイの事前検査 |
| `build PROJECT` | 検査と PRG・メモリ配置の生成 |
| `test PROJECT` | ビルドとキーボード／パッドの操作テスト |
| `capture PROJECT --rom ROM` | テストに続いて PNG、音声付き MP4、撮影記録を生成 |
| `release PROJECT --rom ROM` | 撮影に続いて配布フォルダーを生成 |
| `deploy PROJECT --rom ROM --web-root WEB` | release と同じ全工程を経てローカル Web 配置 |
| `verify-published PROJECT --base-url URL` | 配置後の HTTP 公開ファイルをハッシュ照合 |

Web サーバーへの push、GitHub Pages の公開設定、外部サービスへのアップロードは行いません。ローカル配置とインターネット公開を区別します。既存 Web エミュレーターのゲーム一覧への登録には `sourceUrl` の条件があります。[配布と公開](publishing.md)を読んでください。

## 生成結果を見る

`build/release/game-media/my-first-game/index.html` を開くと、PRG・ソース ZIP・動画・画像・検証記録がまとまっています。撮影画像は `title.png` と、リプレイで名前を付けた `play.png`、`clear.png`、`ending.png` です。

ブラウザー経由で確認する場合は、別のターミナルで次を実行します。確認後は Ctrl+C でサーバーを停止します。

```sh
.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory games/my_first_game/build/release
```

`http://127.0.0.1:8000/game-media/my-first-game/` を開き、画像の文字切れ、盤面、クリア表示、動画の入力と音を確認します。自動テストだけで「面白い」「初見で分かる」と判断しないでください。

## 次に読むもの

- [言語と API](language.md): 普通の Python との違い、状態、入力、描画
- [絵・音・面データ](assets.md): PCG と音の編集箇所
- [テストと撮影](testing.md): リプレイ形式、失敗と回復の作り方
- [配布と公開](publishing.md): ソース同梱、カタログ、公開後の照合
- [AI 用の制作指示書](ai-workflow.md): 一度の依頼で制作と修正ループを進める
- [よくある失敗](troubleshooting.md): 症状・原因・修正・再確認
- [導入時の検証記録](verification.md): 新規 41 テスト、撮影、既存 51 作品への影響

開発キット自体を変更した場合の回帰テストは `make devkit-test PYTHON=.venv/bin/python` です。C++20 と `JR100EMU_ROOT` がない環境では、ネイティブ統合テストはスキップになります。新規ゲームの動作確認には、その作品への `dev.py test` を使います。
