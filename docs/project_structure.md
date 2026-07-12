# リポジトリ構成とビルド成果物

このリポジトリは「JR-100開発ルール」と「実行可能なサンプル」を中心に構成し、それらを支えるツールチェーンを`src/jr100dev`へ分離しています。

| パス | 役割 |
| --- | --- |
| `rules/` | JR-100固有のCPU、メモリ、I/O、実装ルール |
| `samples/` | 学習用および実践用のサンプルプロジェクト |
| `src/jr100dev/` | アセンブラ、リンカ、プロジェクト生成、標準マクロ |
| `tests/unit/` | アセンブラ、リンカ、マクロの単体テスト |
| `tests/opcodes/` | MB8861H命令表の同期テスト |
| `tests/integ/` | サンプルを実際にビルドする統合テスト |
| `tools/` | PCGエディタ、命令表同期、検証用ツール |
| `docs/` | マクロ仕様、オブジェクト形式、設計記録 |
| `external/` | 検証に使用する外部プロジェクト |

## サンプルの標準構成

```text
samples/example/
├── README.md
├── Makefile
├── main.asm または src/main.asm
└── build/                 生成物、Git管理対象外
```

リポジトリルートから次の共通形式でビルドします。

```sh
make -C samples/example
```

各サンプルのMakefileは`src/`を`PYTHONPATH`へ加えるため、ツールを事前インストールしなくても動作します。

## `jr100dev new`の生成物

| パス | 役割 |
| --- | --- |
| `src/main.asm` | `.org $0300`から始まるエントリソース |
| `std/macro.inc` | プロジェクト側で変更可能な標準マクロのコピー |
| `jr100.toml` | CPU、クロック、エントリ、メモリ設定 |
| `build/` | `.bin`、`.prg`、マップなどの出力先 |
| `.gitignore` | ビルド生成物の除外設定 |

```sh
jr100dev new my-project
cd my-project
jr100dev assemble src/main.asm -o build/main.prg
```

## リポジトリ全体の確認

```sh
make samples
make test
npm test --prefix tools/pcg_editor
```

`make samples`は全サンプルをビルドし、`make test`はPythonの全テストを実行します。
