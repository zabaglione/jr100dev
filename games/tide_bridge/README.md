# TIDE BRIDGE

[Wiki](https://github.com/zabaglione/jr100dev/wiki/TIDE-BRIDGE) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=tide-bridge)

行または列の橋をまとめて上下させ、左下の岸と右上の門をつなぎます。3種類の橋の配置に挑戦します。

![タイトル](images/title.png)

## タイトルのデザイン

水面から持ち上がった橋と橋脚を大きく描き、横長のTIDEで川幅を表します。

## 画面の奥行き

橋を水面より高い板張りの足場、出口を門として描きました。水面との高低差で、渡れる場所を区別できます。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を結晶フォント**（細い角形と斜めの切り口）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

W/Sで対象の線を選び、A/Dで行と列を切り替え、RETURNで反転します。1面30回まで変更できます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

水面と橋、選択している線、変更回数を表示します。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 1.3.0。開始番地 `$0300`、ゲーム本体と定数は 6,814 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/tide_bridge
make -C games/tide_bridge test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py tide_bridge --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
