# LOOP TEN

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → LOOP TEN

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=loop-ten) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/loop_ten)

同じブラウザーでBASIC ROMを事前に登録してください。

10秒ごとに出発地点へ戻る、JR-100・標準RAM 16KB向け探索パズルです。12の部屋の封印を点灯させ、ループから脱出してください。点灯した封印と開いた扉は、巻き戻っても残ります。

![Title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/title.png)

## 画面の奥行き

迷宮の石壁、門、封印に厚みを付け、主人公には接地影を加えました。時間ゲージと危険な床の記号は見やすさを優先しています。

## ゲーム専用フォント

今回は通常フォントを維持しています。絵柄やアニメーションに使うPCGを残すと、一式の数字・英字を揃える枠が足りないためです。一部の文字だけ書体が変わる置き換えは行いません。

## 操作とルール

| 操作 | キーボード | 1ボタンパッド |
| --- | --- | --- |
| 移動 | W/A/S/D、長押し可 | 上下左右、長押し可 |
| 封印／アンカーを使う | RETURN | ボタン |
| 早めに巻き戻す | SPACE | 点灯済みの封印をもう一度使う |
| BASICへ戻る | CTRL+C | キーボードを使用 |

菱形の封印と同じセルか上下左右の隣でボタンを押すと点灯し、その部屋の右端の扉が開きます。点灯済みの封印を再使用すると早めに巻き戻せます。各部屋の開始位置にある時計型アンカーは、最初の未点灯の部屋へ移動する近道です。

時間切れと罠への接触で最初の部屋へ戻ります。封印の記録は保持し、残り時間と位置を戻します。12番目の封印まで点灯すれば成功。初版の記録は同じプレイ中のRAM内だけで保持し、タイトルへ戻って再開すると初期化します。

HUDは残り秒数、太い時間バー、ループ回数、部屋番号、12個の封印の点灯状態です。残り3秒から音で知らせます。待っていても、移動中でも、効果音が鳴っていても時計は進みます。

![Chamber five](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/chamber-05.png)
![An opened seal and door](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/seal-open.png)
![The last second](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/last-second.png)
![Escape](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/ending.png)

## ビルドと検証

開発環境を用意して `make -C games/loop_ten` を実行します。出力は `build/loop-ten.prg`、開始番地は `$0300`。本体と定数は7,028 bytes。画面・状態・保存領域・512 bytesのスタックを含めて標準16KB内、PCGは32文字です。

`make -C games/loop_ten test` は時間切れ、長押し、封印の持越し、扉の開閉、アンカー、罠、時間計算の桁あふれを検証します。12回の巻き戻し区間を使う安全な入力手順で、180歩・全12封印をクリアしました。これは最短ループ数ではありません。

CPUクロック894,000Hzを基準に、無操作時と移動キー長押し・効果音ありの両方で、9.98〜10.04秒の範囲で論理上の時間切れを確認しています。画面の巻き戻し表示は、その後の描画処理の完了を待ちます。実機の時計精度・操作感は未確認です。

```sh
.venv/bin/python games/loop_ten/replay.py --rom /path/to/owned-rom.prg --capture
```

掲載画像は実BASICからPRGを起動したエミュレーターの実画面です。タイマーは描画時間を切り捨てず、VIA Timer 2の16bit差分を積算します。ポーリング間隔はカウンター1周より短い範囲で検証しています。Timer 2の連続した減算については、[WDCのVIAデータシート、2.9節](https://www.wdc65xx.com/wdc/documentation/w65c22.pdf)を参照しました。これはJR-100実機での確認を代用するものではありません。

効果音と32小節の独自タイトル曲を収録。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。ROMは含みません。
