# PRISM TRACE

[ホーム](Home) → [パズル](Genre-Puzzle) → PRISM TRACE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=prism-trace) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/prism_trace)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

6枚の鏡を回転し、左から入る光を右上の受光器へ届けます。光路は鏡を回すたびに更新されます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/title.png)

## 画面の奥行き

鏡に細い側面と台座、受光器にくぼみを付けました。反射する斜線と光の経路は従来の角度・位置を保っています。

## 操作と遊び方

WASDで鏡の位置を選び、RETURNで / と反対向きの鏡を切り替えます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

点線で光路を示し、側面に回転回数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/play-02.png)

## ビルドと検証

バージョン 1.1.0。開始番地 `$0300`、ゲーム本体と定数は 6,379 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/prism_trace
make -C games/prism_trace test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py prism_trace --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
