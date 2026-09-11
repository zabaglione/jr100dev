# POTION PATH

[Wiki](https://github.com/zabaglione/jr100dev/wiki/POTION-PATH) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=potion-path)

素材ごとの移動量を組み合わせ、調合の位置を注文のダイヤへ合わせます。6件の注文に各12回以内の投入で応えます。

![タイトル](images/title.png)

## 操作と遊び方

WASDで素材を選び、RETURNで加えます。灰は左2、苔は右1・下2、塩は上1、根は右3・下1です。盤外へ出る素材は加えられません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

調合位置、注文、素材の移動量、投入数を表示します。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 1.0.0。開始番地 `$0300`、ゲーム本体と定数は 5,983 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/potion_path
make -C games/potion_path test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py potion_path --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
