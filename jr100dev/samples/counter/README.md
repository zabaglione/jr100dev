# counter サンプル

## 概要
- FOR マクロを使って数字 0〜9 を VRAM に描画し、キー入力でリセットする例です。
- `ctl.inc` に含まれる FOR/IF マクロの書き方と、`macro.inc` の `CLR_VRAM`・`PRINT_STR` を組み合わせた基本処理を確認できます。

## ビルド
```sh
PYTHONPATH=/path/to/jr100dev python -m jr100dev.cli.main assemble main.asm \
  --obj build/counter.json --bin build/counter.bin --map build/counter.map -o build/counter.prg
```

## 実行
1. エミュレーターで `build/counter.prg` を読み込み、`A=USR($300)` を実行します。
2. 画面に "FOR LOOP DEMO" と数字 0〜9 が並び、任意のキーを押すと初期状態へ戻ります。
3. スペースキー (コード 0x01) を押すとビープ音が鳴る点が他のキーとの違いです。

## メモ
- `VAR8 COUNT` をループ変数と値保存の両方に利用しており、FOR マクロの生成する構造が読み取れます。
- ループが終わるたびに `RESET` ラベルへ飛んで再度描画しているため、VRAM の状態が常にリセットされる点に注意してください。
