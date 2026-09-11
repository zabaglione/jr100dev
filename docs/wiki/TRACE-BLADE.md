# TRACE BLADE

[ホーム](Home) → [パズル](Genre-Puzzle) → TRACE BLADE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=trace-blade) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/trace_blade)

同じブラウザーでBASIC ROMを事前に登録してください。

30の部屋を一筆の刀筋で突破する、JR-100・標準RAM 16KB向けパズルです。12×9マスの盤面で経路を計画し、全標的を通って菱形の出口へ到達したら実行します。刀が予定経路を走り、標的を連続で撃破します。

![Title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/title.png)

## タイトルのデザイン

大きな斜めの刃が経路を横切る構図です。傾いた文字と標的の菱形を斬撃の方向に揃えています。

## 画面の奥行き

壁を石積みの立体ブロック、出口をくぼんだ台座にしました。計画経路・標的の選択枠・斬撃は従来の位置で判別できます。

## ゲーム専用フォント

今回は通常フォントを維持しています。絵柄やアニメーションに使うPCGを残すと、一式の数字・英字を揃える枠が足りないためです。一部の文字だけ書体が変わる置き換えは行いません。

## 操作

| 操作 | キーボード | 1ボタンパッド |
| --- | --- | --- |
| 経路を1マス伸ばす | W/A/S/D | 上下左右 |
| 操作メニュー／決定 | RETURN | ボタン |
| メニュー選択 | W/S | 上下 |
| 1手戻す | SPACE | メニューのUNDO |
| 実行 | F | メニューのCUT |
| BASICへ戻る | CTRL+C | キーボードを使用 |

一度通ったセルと壁は通れません。経路は好きなだけ考え、始点まで1手ずつ戻せます。全標的を通り、出口で終わっている経路だけを実行できます。メニューのRESETはその面の経路を消し、TITLEはタイトルへ戻ります。BACKで計画を続けられます。

HUDのTARGETは標的数、MARKEDは経路に入った数、PATHは歩数、COMBOは実行中の撃破数。経路に入った標的には四隅の印が付きます。実行は入力を待たずに進み、面クリア後にボタンを押すと次の面です。

![Planned route](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/planning-15.png)
![Strike in motion](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/strike-15.png)
![Ending](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/ending.png)

やり直し／プレイ中のタイトル移動は実行前に確認します。NOが初期選択です。A/Dで選びRETURNで確定、SPACEで取り消します。

## ビルドと検証

開発環境を用意して `make -C games/trace_blade` を実行します。出力は `build/trace-blade.prg`、開始番地は `$0300`。本体・定数は8,569 bytesで、状態、画面、BASICへ戻すための保存領域、512 bytesのスタックを含めて標準16KB内です。PCGは32文字です。

`make -C games/trace_blade test` は経路の重複、壁、未完成経路の実行拒否、戻し、標的数、リセット、連続実行、次面への遷移を検証します。全30面を915歩の入力でクリアし、コード領域の破壊がないこととスタック範囲を確認しています。

```sh
.venv/bin/python games/trace_blade/replay.py --rom /path/to/owned-rom.prg --capture
```

掲載画像は所有する実BASIC ROMからPRGを起動したエミュレーターの実画面です。実機動作は未確認。効果音と32小節の独自タイトル曲を収録しています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)、ROMは含みません。`art/`の画面データをPCG Workbenchで編集できます。
