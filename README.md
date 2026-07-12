# JR-100 DSL ツールチェーン

JR-100 向けアセンブラ／リンカ／CLI を備えた DSL 開発環境です。`.prs` ではなくアセンブリ互換の DSL を入力とし、JR-100 エミュレーターでロード可能な `.prg` を生成します。

## 特徴
- `jr100dev assemble` / `jr100dev link` によるビルドパイプライン
- `macro.inc` による VRAM 出力／サウンド／キースキャンマクロ
- `ctl.inc` による `FOR` / `WHILE` / `IF` 等の制御構造マクロと 8/16bit 算術ヘルパー
- `.prg` 出力は `PBIN` セグメントを保持し、ベースアドレスを適切に反映

## ディレクトリ構成
| パス | 役割 |
| --- | --- |
| `jr100dev/` | CLI・アセンブラ・リンカ本体 |
| `jr100dev/std/macro.inc` | 標準 I/O マクロ |
| `jr100dev/std/ctl.inc` | 制御構造・算術マクロ |
| `jr100dev/samples/hello` | 最小の VRAM 出力サンプル |
| `jr100dev/samples/io_demo` | 高レベルマクロ＋I/O のデモ |
| `jr100dev/samples/counter` | `FOR` マクロを使ったカウンタ |
| `jr100dev/samples/pcg_clock` | PCG数字を使った24時間時計サンプル |
| `tools/pcg_editor` | 32文字・複合キャラクター対応Web PCGエディタ |
| `docs/` | ビルド手順やマクロ仕様などのドキュメント |

詳細な説明は `docs/project_structure.md` および `docs/std_macros.md` / `docs/high_level_macros.md` を参照してください。

## セットアップ
```bash
git clone https://github.com/zabaglione/jr100dev.git
cd jr100dev
PYTHONPATH=$(pwd) python -m jr100dev.cli.main new sample
```

- `PYTHONPATH` を指定することでローカルツリーから CLI を呼び出せます。
- `sample` ディレクトリ配下に `jr100.toml`, `src/main.asm`, `std/macro.inc`, `build/` 等が生成されます。

## ビルド
```bash
cd sample
PYTHONPATH=/path/to/jr100dev jr100dev assemble src/main.asm -o build/main.prg
```

- `build/main.prg` と `build/main.bin` が出力されます。
- 複数オブジェクトを扱う場合は `--obj` で JSON オブジェクトを書き出し、`jr100dev link` に渡してください。

## エミュレーターでの確認
1. `hexdump -C build/main.prg` で `PBIN` セグメントのアドレスと `entry=$xxxx` を確認。
2. `python -m jr100emu.app --rom datas/jr100rom.prg --load build/main.prg` などでロードし、画面表示・ビープ・キー入力が期待通りか確認。
3. GUI が利用できない環境では `build/main.map` のシンボルと `.prg` の `PBIN` 先頭アドレスが一致することをもって静的に検証します。

## テスト
```bash
PYTHONPATH=$(pwd) pytest jr100dev/tests/unit
```

- リンカ／マクロ／高レベル DSL の単体テストが実行されます。

## ドキュメント
- `docs/project_structure.md`: ディレクトリ構成とビルド成果物の説明、スモークテスト手順
- `docs/std_macros.md`: 標準マクロ (`macro.inc`) の詳細
- `docs/high_level_macros.md`: 制御構造／算術マクロ (`ctl.inc`) の使い方
- `docs/prg_packaging_notes.md`: `.prg` 形式と `PBIN` セグメントの仕様

## Web PCGエディタ

JR-100のPCG領域 `$C000-$C0FF` に対応する32文字を編集できるWebアプリを `tools/pcg_editor` に用意しています。1文字は8×8ドット・8バイトです。2×2や3×3などの連続スロットを一枚の大型キャンバスとして編集でき、8×8境界をまたいだマウス描画、Undo/Redo、シフト、反転、塗りつぶし、JSON保存、アセンブリ出力に対応します。

```bash
cd tools/pcg_editor
npm run serve
```

ブラウザーで `http://localhost:8000` を開いて使用します。外部ライブラリのインストールは不要です。

- 左ドラッグは描画、右ドラッグは消去です。高速ドラッグ時は座標間を補間します。
- 32スロットのサムネイル、実機サイズの画面プレビュー、各行の16進値を常時確認できます。
- ATARI / NAMCO系アーケードフォントを参考にした数字0〜9とコロンのプリセットを収録しています。
- `ASM Output` は32文字・256バイトを `.byte` 形式で出力します。
- `npm test --prefix tools/pcg_editor` で座標変換、複合編集、プリセット、出力処理をテストできます。

従来のPython + Pygame版は `tools/char_editor.py` に残しています。

## PCG時計サンプル

Web PCGエディタと同じアーケード数字データを利用する時計サンプルを `jr100dev/samples/pcg_clock` に用意しています。

```bash
make -C jr100dev/samples/pcg_clock
```

`build/pcg_clock.prg` をロードして `A=USR($0300)` を実行すると、`12:00:00` から約1秒間隔で24時間時計を表示します。

## ライセンス
本リポジトリ全体のライセンスについてはプロジェクトルートに配置されたファイル・ヘッダーを参照してください。
