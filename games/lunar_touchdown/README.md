# LUNAR TOUCHDOWN

[Wiki](https://github.com/zabaglione/jr100dev/wiki/LUNAR-TOUCHDOWN) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=lunar-touchdown)

燃料と降下速度を調整し、指定された着陸台へ降ります。着陸場所が異なる5面があります。

![タイトル](images/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](images/demo-start.png)

![操作を進めた場面](images/demo-play.png)

![最初の目標を達成した場面](images/demo-clear.png)

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=lunar-touchdown)**

最初の2ステージをクリアするまでを収録。

## タイトルのデザイン

横長LUNARの下に月着陸船と起伏を描き、着陸脚と噴射を白黒の抜きで示します。

## 画面の奥行き

着陸船を窓と脚のある機体にし、遠くの山と手前の月面を分けて描きました。接地判定に使う着陸台は明確な水平線で表示します。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を計器盤フォント**（角張った太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 動きとクリア演出

クリア時は完成した盤面・結果を残し、約1.6秒のジングルと余韻を挟みます。失敗時も原因を表示し、ジングルの後に短い間を置きます。その後、キーを押し直して次の操作に進みます。直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。

## 操作と遊び方

A/Dで横移動、WまたはRETURNで噴射します。1回の噴射は速度を2下げます。速度0～2で着陸台に触れると成功、噴射は24回までです。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

噴射炎、着陸台、燃料、降下速度、高度を表示します。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 1.5.0。開始番地 `$0300`、ゲーム本体と定数は 5,991 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/lunar_touchdown
make -C games/lunar_touchdown test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py lunar_touchdown --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
