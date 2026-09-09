# JR-100 Development Guide and Samples

JR-100向けプログラムを安全に作るための開発ルールと、実際にビルドして動かせるサンプルコードをまとめたリポジトリです。

最初に[`rules/README.md`](rules/README.md)でCPU・メモリ・I/Oの制約を確認し、次に[`samples/`](samples/)のコードを動かしてください。付属の`jr100dev`は、これらのサンプルを再現可能にビルドするためのアセンブラ、リンカ、標準マクロです。

## はじめに

```sh
git clone https://github.com/zabaglione/jr100dev.git
cd jr100dev
python3 -m pip install -e .
make -C samples/hello
```

生成された`samples/hello/build/hello.prg`をJR-100エミュレーターまたは実機へロードし、BASICから`A=USR($0300)`を実行します。

インストールせずに使う場合は、各サンプルのMakefileが`src/`を自動的に`PYTHONPATH`へ追加するため、そのまま`make`を実行できます。

## どこから読むか

| 目的 | 場所 |
| --- | --- |
| JR-100固有の制約を知る | [`rules/`](rules/) |
| 動くコードから学ぶ | [`samples/`](samples/) |
| 標準マクロやPRG形式の詳細を調べる | [`docs/`](docs/) |
| アセンブラとリンカの実装を調べる | [`src/jr100dev/`](src/jr100dev/) |
| PCG文字を編集する | [`tools/pcg_editor/`](tools/pcg_editor/) |
| 回帰テストを調べる | [`tests/`](tests/) |

## サンプル

| サンプル | 内容 |
| --- | --- |
| [`hello`](samples/hello/) | VRAMへ1文字を直接書く最小例 |
| [`counter`](samples/counter/) | `FOR`マクロを使ったカウンター |
| [`io_demo`](samples/io_demo/) | VRAM、キー入力、簡易ビープの組み合わせ |
| [`key_display`](samples/key_display/) | VIAを直接使ったキーマトリクス読み取り |
| [`multi`](samples/multi/) | 複数オブジェクトのアセンブルとリンク |
| [`pcg_clock`](samples/pcg_clock/) | PCG数字を使った24時間時計 |
| [`pcg_animation`](samples/pcg_animation/) | 4つの常駐PCGを書き換える2×2キャラクターアニメーション |
| [`sound_demo`](samples/sound_demo/) | Timer 1単音BGM、効果音、PCG共存を確認するサンプル |
| [`maze`](samples/maze/) | 迷路生成、入力、スクロールを含む実践例 |
| [`relic_dive`](samples/relic_dive/) | 標準16KB、64×32マス、8方向・1ボタンパッド対応のローグライク |

個別のサンプルは共通の操作でビルドできます。

```sh
make -C samples/pcg_clock
make -C samples/maze
```

全サンプルをまとめてビルドする場合は次を実行します。

```sh
make samples
```

## 開発ツール

編集可能インストール後はCLIを直接利用できます。

```sh
jr100dev new my-project
cd my-project
jr100dev assemble src/main.asm -o build/main.prg
```

複数オブジェクトのリンク方法は[`samples/multi`](samples/multi/)を参照してください。

ローカルソースから直接呼ぶ場合は次の形式です。

```sh
PYTHONPATH=/path/to/jr100dev/src python3 -m jr100dev.cli.main --help
```

## テスト

```sh
python3 -m pip install -e ".[test]"
make test
npm test --prefix tools/pcg_editor
npm test --prefix tools/sound_editor
```

`make test`は`tests/unit`、`tests/opcodes`、`tests/integ`を実行します。サンプル単体の確認方法は各ディレクトリのREADMEを参照してください。

## Web PCGエディタ

`tools/pcg_editor`は、JR-100のPCG領域`$C000-$C0FF`に対応する32文字を編集するWebアプリです。8×8文字だけでなく、連続スロットを使った複合キャラクターも編集できます。

```sh
cd tools/pcg_editor
npm run serve
```

ブラウザーで`http://localhost:8000`を開いて使用します。外部ライブラリのインストールは不要です。

## Webサウンドエディタ

`tools/sound_editor`は、Timer 1の単音BGMと最大500msのブロッキング効果音を編集するWebアプリです。ピアノロールで作った資産を`sound_assets.inc`として出力でき、ローカルビルダーから確認用PRGも生成できます。

```sh
cd tools/sound_editor
npm run serve
```

ブラウザーで`http://127.0.0.1:8001`を開いて使用します。初期表示は日本語で、画面右上から英語へ切り替えられます。外部ライブラリのインストールは不要です。

## リポジトリ構成

```text
rules/          JR-100開発時に守るハードウェア・実装ルール
samples/        ビルド・実行可能なサンプルプロジェクト
src/jr100dev/   サンプルを支えるアセンブラ、リンカ、標準マクロ
tests/          ツールチェーンとサンプルの回帰テスト
tools/          PCGエディタや命令同期などの補助ツール
docs/           マクロ、オブジェクト形式、設計記録などの詳細資料
external/       検証に使う外部プロジェクト
```

構成と生成物の詳細は[`docs/project_structure.md`](docs/project_structure.md)を参照してください。
