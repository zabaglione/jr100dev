# プロジェクト構成とビルド成果物

標準の `jr100dev new <name>` で生成されるディレクトリ構成と、ビルド時に生成されるファイルの位置をまとめる。

| パス | 役割 |
| --- | --- |
| `src/main.asm` | エントリポイントとなるアセンブリソース（`.org $0300`、`JMP MAIN` が含まれる） |
| `src/*.asm` | 追加のソースを配置するディレクトリ。`run_assemble` や `run_link` で取り込む |
| `std/macro.inc` | 標準マクロ定義。カスタマイズする場合はこのコピーを編集する |
| `jr100.toml` | プロジェクト設定（エントリアドレスや VRAM 基準アドレスなど） |
| `build/` | ビルド成果物の出力先ディレクトリ（既定で `.bin` と `.prg` が生成される） |
| `samples/hello` | 最小の VRAM 出力サンプル（テンプレートと同様の構成で 1 文字表示） |
| `samples/io_demo` | VRAM 表示とサウンド・キースキャンのマクロ使用例 |

## ビルドフロー

```
PYTHONPATH=/path/to/jr100dev jr100dev assemble src/main.asm -o build/main.prg
```

- 上記コマンドは `build/main.prg` と `build/main.bin` を出力する。
- 中間オブジェクトやマップを保存したい場合は `--obj`, `--map`, `--bin` を明示的に指定する。
- 複数モジュールを扱う場合は `jr100dev assemble` で `.obj` を生成し、`jr100dev link` で連結する。成果物は同じく `build/` 配下に置く運用を推奨。

## 手動確認フロー

1. `PYTHONPATH=/path/to/jr100dev pytest jr100dev/tests/unit` で単体テストを実行し、リンカやマクロの回帰を確認する。
2. `PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main new sample` で雛形を生成し、`build/main.prg` をエミュレーターへ読み込んで表示・ビープ・入力待ちを手動確認する。

### `.prg` スモークテストの流れ

1. `jr100dev assemble src/main.asm -o build/main.prg --bin build/main.bin --map build/main.map` を実行し、セクションが `PBIN` として複数化されているか `hexdump -C build/main.prg` で確認する（`PBIN` が複数あり最初のコメントに `entry=$xxxx` が出力されていること）。
2. エミュレーター (`python -m jr100emu.app --rom datas/jr100rom.prg --load build/main.prg` 等) でロードし、VRAM 表示・ビープ・キー入力待ちが行えることを目視で確認する。
   - VRAM に「HELLO JR-100!」が ASCII 変換済みコードで表示される。
   - 起動直後に BEEP が鳴る。
   - キー押下でループから抜け、再度メッセージが描画される（`samples/io_demo` 参照）。
3. GUI 環境が無い場合は、`build/main.prg` の `PBIN` セグメント先頭アドレスと `build/main.map` のシンボルが一致するかをもって静的確認とする。
