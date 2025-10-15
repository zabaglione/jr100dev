# io_demo サンプル

## 概要
- 画面描画、ビープ音、キースキャンという基本的な I/O を一通り試せるデモです。
- 0〜9 の数字を表示し、押下したキーコードをそのまま VRAM に表示します。スペースキーを押したときだけビープ音が鳴ります。

## ビルド
```sh
PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main assemble main.asm \
  --obj build/io_demo.json --bin build/io_demo.bin --map build/io_demo.map -o build/io_demo.prg
```

## 実行
1. エミュレーターで `build/io_demo.prg` をロードし、`A=USR($300)` を実行します。
2. 画面に "JR-100 I/O DEMO" が表示され、キーを押すとそのキーコード (マクロの戻り値) が画面に描画されます。
3. スペースキーを押すとビープ音が鳴り、表示領域がクリアされて次の入力を待ちます。

## メモ
- `SCAN_KEY` マクロは VIA のポーリングを行って整数値を返しており、複数キーを同時に押した場合はビット積が戻る点に注意してください。
- 直前の表示を消すために `' '` (空白) を書き戻しており、別の文字列を描画する場合は同様に VRAM をクリーンアップする必要があります。
