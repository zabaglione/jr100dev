# STAR LANCE

[ホーム](Home) → [アクション](Genre-Action) → STAR LANCE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/star_lance)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

左右へ動く18機の編隊を縦のランスで撃ち落とします。落下するミサイルを避け、飛行カウント220以内に全滅させます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/title.png)

## 画面の奥行き

機体に面の明暗、敵に輪郭と影を付け、大小の星を離して配置しました。敵弾と自機の位置は平面のままです。

## 操作と遊び方

A/Dで自機を移動、RETURNで発射します。連射には待ち時間があります。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

自機・編隊・ミサイルに加え、耐久力、残敵数、時間を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/play-02.png)

## ビルドと検証

バージョン 1.1.0。開始番地 `$0300`、ゲーム本体と定数は 6,127 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/star_lance
make -C games/star_lance test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py star_lance --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
