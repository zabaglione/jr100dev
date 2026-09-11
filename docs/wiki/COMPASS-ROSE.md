# COMPASS ROSE

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → COMPASS ROSE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=compass-rose) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/compass_rose)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

方位の手掛かりで、10か所の隠し財宝を順に探します。1か所につき移動32回、発掘3回までです。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/title.png)

## 画面の奥行き

未調査の土地を側面のある土のブロック、調査済みの土地を低い床として描きました。主人公と方位表示を手前に置いています。

## ゲーム専用フォント

**活字フォント**（読みやすいセリフ体）を採用。タイトル／説明用に16文字、ゲーム用に20文字を割り当てています。ゲーム中の対象は `0123456789EXPDITONSG` です。空きPCG枠だけを使い、残りの文字は通常フォントで表示します。数字を変更する作品では0〜9を一式で揃えています。

## 操作と遊び方

WASDで探索、RETURNで足元を発掘します。方位計がHEREなら目的の位置です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

探索済みの地図、方位、残りの移動と発掘回数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,328 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/compass_rose
make -C games/compass_rose test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py compass_rose --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
