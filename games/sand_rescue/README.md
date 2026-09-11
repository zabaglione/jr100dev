# SAND RESCUE

[Wiki](https://github.com/zabaglione/jr100dev/wiki/SAND-RESCUE) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=sand-rescue)

水源が4滴ごとに移る灌漑装置で、3つの作物へ4滴ずつ届けます。水源のあふれ6回、または貯水量30を使い切ると失敗です。

![タイトル](images/title.png)

## 画面の奥行き

堰を土の断面、作物を幹と影のある木にし、水を短い波線で区別しました。流れの分岐と水門の位置は正方格子を保っています。

## ゲーム専用フォント

**石碑フォント**（上下の飾りを持つ刻印）を採用。タイトル／説明用に16文字、ゲーム用に12文字を割り当てています。ゲーム中の対象は `0123456789>+` です。空きPCG枠だけを使い、残りの文字は通常フォントで表示します。数字を変更する作品では0〜9を一式で揃えています。

## 操作と遊び方

A/Dで堰を選び、RETURNでその堰だけを開けます。古い水が通り抜けてから次の流路へ切り替えてください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

流れる水、堰、水源、3つの作物の給水数を表示します。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 7,107 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/sand_rescue
make -C games/sand_rescue test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py sand_rescue --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
