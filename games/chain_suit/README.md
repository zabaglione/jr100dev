# CHAIN SUIT

[Wiki](https://github.com/zabaglione/jr100dev/wiki/CHAIN-SUIT) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=chain-suit)

5枚の手札を交換し、3回の採点で合計25点を目指します。役なし3点、1組のペア8点、複数のペア16点、同一スート5枚25点です。

![タイトル](images/title.png)

## 画面の奥行き

カードを薄い厚みのある札にし、手札と得点・目標・交換回数を別々の台座に配置しました。札の数値とスートは平面の文字で表示します。

## ゲーム専用フォント

**活字フォント**（読みやすいセリフ体）を採用。タイトル／説明用に16文字、ゲーム用に28文字を割り当てています。ゲーム中の対象は `0123456789THREANDS/BUILYOCGW` です。空きPCG枠だけを使い、残りの文字は通常フォントで表示します。数字を変更する作品では0〜9を一式で揃えています。

## 操作と遊び方

A/Dで札を選び、Wで交換します。交換は各手札につき2回まで。RETURNで採点して次の手札へ進みます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

札の下に数字とスート、下段に得点・目標・交換残数を表示します。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,345 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/chain_suit
make -C games/chain_suit test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py chain_suit --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
