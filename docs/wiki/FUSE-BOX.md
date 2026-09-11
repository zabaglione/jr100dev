# FUSE BOX

[ホーム](Home) → [パズル](Genre-Puzzle) → FUSE BOX

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=fuse-box) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/fuse_box)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

行と列に指定された個数だけスイッチを入れます。すべての個数が一致すれば、どの配置でも正解です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/title.png)

## 操作と遊び方

WASDでスイッチを選び、RETURNで入／切を反転します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

盤の周囲に行・列の目標個数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/play-02.png)

## ビルドと検証

バージョン 1.0.0。開始番地 `$0300`、ゲーム本体と定数は 6,355 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/fuse_box
make -C games/fuse_box test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py fuse_box --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
