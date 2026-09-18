# TRACE BLADE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/trace-blade.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/trace-blade.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → TRACE BLADE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=trace-blade) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/trace_blade)

同じブラウザーでBASIC ROMを事前に登録してください。

30の部屋を一筆の刀筋で突破する、JR-100・標準RAM 16KB向けパズルです。12×9マスの盤面で経路を計画し、全標的を通って菱形の出口へ到達したら実行します。刀が予定経路を走り、標的を連続で撃破します。

![Title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/demo-clear.png)

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=trace-blade)**

1ステージのクリアまでを収録。

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
