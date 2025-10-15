# hello サンプル

## 概要
- JR-100 の VRAM 先頭へ ASCII 'A' を直接書き込み、動作確認だけを行う最小サンプルです。
- マクロを一切使用せず、`.org` と `LDAA`/`STAA` のみで画面に文字を出す流れを確認できます。

## ビルド
```sh
PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main assemble main.asm \
  --obj build/hello.json --bin build/hello.bin --map build/hello.map -o build/hello.prg
```
- `build/hello.prg` が生成されれば成功です。

## 実行
1. JR-100 エミュレーターで `build/hello.prg` をロードします。
2. BASIC 画面で `A=USR($300)` を実行すると、画面左上に `A` が表示されます。

## メモ
- VRAM の先頭アドレス `$C100` に 1 バイト書くだけなので、環境依存の副作用がほぼありません。
- DSL マクロを使う前に、JR-100 のアドレスマップや VRAM 書き込み手順を理解する目的で利用してください。
