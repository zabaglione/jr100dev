# CARGO BALANCE

[Wiki](https://github.com/zabaglione/jr100dev/wiki/CARGO-BALANCE) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=cargo-balance)

船の傾きを抑えながら12個の積荷を載せます。左右の傾きの差が8を超えると失敗です。

![タイトル](images/title.png)

## 画面の奥行き

船に甲板・船腹・水面の段差を付け、積荷には斜めの側面を描きました。荷重の数字と左右の釣り合いは従来の位置で確認できます。

## ゲーム専用フォント

**計器盤フォント**（角張った太線）を採用。タイトル／説明用に16文字、ゲーム用に28文字を割り当てています。ゲーム中の対象は `0123456789NEXTLOAD=CRGB>+/:U` です。空きPCG枠だけを使い、残りの文字は通常フォントで表示します。数字を変更する作品では0〜9を一式で揃えています。

## 操作と遊び方

A/Dでクレーンを動かし、RETURNで次の荷を落とします。外側の船倉は重みが3倍、各船倉には4個まで置けます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

積荷、次の重さ、左右の負荷、積載数を表示します。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,133 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/cargo_balance
make -C games/cargo_balance test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py cargo_balance --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
