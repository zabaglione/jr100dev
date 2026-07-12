# multi サンプル

## 概要
- 複数の ASM ファイルを組み合わせる方法を示すサンプルです。
- メイン (`src/main.asm`) から別モジュール (`src/message.asm`) の `DRAW_MESSAGE` を呼び出し、分割されたソースをリンクして `.prg` を生成します。

## ビルド
```sh
make -C samples/multi
```
- `Makefile` が `jr100dev.cli.main assemble` と `link` を呼び出し、`build/` 以下に `multi.prg` ほかを生成します。
- 個別にビルドしたい場合は以下のように明示的に指定できます。
  ```sh
  PYTHONPATH=/path/to/jr100dev/src python3 -m jr100dev.cli.main assemble src/main.asm -o build/main.prg --obj build/main.json
  PYTHONPATH=/path/to/jr100dev/src python3 -m jr100dev.cli.main assemble src/message.asm -o build/message.prg --obj build/message.json
  PYTHONPATH=/path/to/jr100dev/src python3 -m jr100dev.cli.main link build/main.json build/message.json -o build/multi.prg --bin build/multi.bin --map build/multi.map --entry 0x0300 --data-base 0x0500 --bss-base 0x0600
  ```

## 実行
1. エミュレーターで `samples/multi/build/multi.prg` をロードし、`A=USR($300)` を実行します。
2. タイトルと "DRAWN FROM MODULE" のメッセージ、そして0〜5が1行に表示されれば成功です。

## メモ
- `DRAW_MESSAGE` は`$0400`に配置し、メイン側でも同じアドレスを定数として参照します。
- 標準マクロはメイン側だけで展開し、別モジュールはそのサブルーチンとワーク領域を外部参照します。
- リンク時は`.data`を`$0500`、`.bss`を`$0600`へ再配置し、メインのコード領域との重複を避けます。
