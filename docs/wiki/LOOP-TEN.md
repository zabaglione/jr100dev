# LOOP TEN

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → LOOP TEN

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=loop-ten) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/loop_ten)

同じブラウザーでBASIC ROMを事前に登録してください。

10秒ごとに出発地点へ戻る、JR-100・標準RAM 16KB向け探索パズルです。12の部屋の封印を点灯させ、ループから脱出してください。点灯した封印と開いた扉は、巻き戻っても残ります。

![Title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/title.png)

## 紹介画像とプレイ動画

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=loop-ten)**

最初の2部屋の封印を回収するまでを収録。途中を省略せず、通常の速度で収録しています。画面を確認する間を入れた自動キー入力によるプレイです。

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/demo-start.png)

[![操作を進めた場面・クリックで動画](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/demo-play.png)](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=loop-ten)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/demo-clear.png)

## 操作とルール

| 操作 | キーボード | 1ボタンパッド |
| --- | --- | --- |
| 移動 | W/A/S/D、長押し可 | 上下左右、長押し可 |
| 封印／アンカーを使う | RETURN | ボタン |
| 早めに巻き戻す | SPACE | 点灯済みの封印をもう一度使う |
| BASICへ戻る | CTRL+C | キーボードを使用 |

菱形の封印と同じセルか上下左右の隣でボタンを押すと点灯し、その部屋の右端の扉が開きます。点灯済みの封印を再使用すると早めに巻き戻せます。各部屋の開始位置にある時計型アンカーは、最初の未点灯の部屋へ移動する近道です。

時間切れと罠への接触で最初の部屋へ戻ります。封印の記録は保持し、残り時間と位置を戻します。12番目の封印まで点灯すれば成功。タイトルへ戻って再開すると、封印の記録も最初からになります。

HUDは残り秒数、太い時間バー、ループ回数、部屋番号、12個の封印の点灯状態です。残り3秒から音で知らせます。待っていても、移動中でも、効果音が鳴っていても時計は進みます。

![Chamber five](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/chamber-05.png)
![An opened seal and door](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/seal-open.png)
![The last second](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/last-second.png)
![Escape](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/ending.png)
