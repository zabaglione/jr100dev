# PEG GARDEN

[ホーム](Home) → [パズル](Genre-Puzzle) → PEG GARDEN

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=peg-garden) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/peg_garden)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

隣の石を飛び越して取り除き、石を5個以下に減らす庭園パズルです。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/peg-garden/title.png)

## 画面の奥行き

石を高さのあるペグ、空き位置をくぼんだ受け皿にし、庭の縁に厚みを加えました。選択記号と飛び越せる位置は平面の格子で示します。

## 操作と遊び方

WASDで位置を選び、RETURNで石を選択し、2マス先の空き位置を選んでRETURNを押します。間の石が取り除かれます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

庭園の石、選択中の石、残数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/peg-garden/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/peg-garden/play-02.png)

## ビルドと検証

バージョン 1.1.0。開始番地 `$0300`、ゲーム本体と定数は 6,273 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/peg_garden
make -C games/peg_garden test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py peg_garden --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
