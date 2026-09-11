# BRICK PULSE

[ホーム](Home) → [アクション](Genre-Action) → BRICK PULSE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=brick-pulse) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/brick_pulse)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

パドルで球を反射し、18個のブロックをすべて壊します。3球落とすと失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/title.png)

## 画面の奥行き

反射フィールドの側壁と手前の縁に厚みを加えました。ボール・パドル・ブロックは軌道が読みやすい平面表示を保っています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字をスピードフォント**（右へ傾く太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

A/Dまたはパッドの左右を押し続けると、パドルが連続移動します。短押しでは2文字分ずつ動き、離すと止まります。中央で受けると急な角度、端で受けると浅い角度で反射します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

下部に残球数と残るブロック数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/play-02.png)

## ビルドと検証

バージョン 1.2.1。開始番地 `$0300`、ゲーム本体と定数は 6,443 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/brick_pulse
make -C games/brick_pulse test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py brick_pulse --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
