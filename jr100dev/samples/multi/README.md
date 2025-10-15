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
  PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main assemble src/main.asm --obj build/main.json
  PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main assemble src/message.asm --obj build/message.json
  PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main link build/main.json build/message.json -o build/multi.prg --bin build/multi.bin --map build/multi.map
  ```

## 実行
1. エミュレーターで `samples/multi/build/multi.prg` をロードし、`A=USR($300)` を実行します。
2. タイトルと "DRAWN FROM MODULE" のメッセージ、そして 0〜5 が 1 行に表示されれば成功です。

## メモ
- `DRAW_MESSAGE` は `.public` で公開しており、リンク後にメイン側で呼び出せます。
- `.org $0400` のモジュールをリンクするため、リンカオプション `--bss-base` がプロジェクトの Makefile で指定されています。他のアドレスに配置したい場合は `.org` とリンクオプションを合わせて変更してください。
