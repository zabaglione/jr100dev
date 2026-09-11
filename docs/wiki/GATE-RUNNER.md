# GATE RUNNER

[ホーム](Home) → [アクション](Genre-Action) → GATE RUNNER

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gate-runner) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/gate_runner)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

3本の走路で18個の障害物を突破します。壁は別の走路へ避け、穴は避けるか跳び越えます。衝突3回で終了します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/title.png)

## 画面の奥行き

3本の走路が奥へ収束する遠近表示にしました。障害物は遠くでは小さく、接近すると大きくなり、手前では自機と同じレーン位置に揃います。衝突判定とジャンプのタイミングは変更していません。

## 操作と遊び方

A/Dで走路を変更、WまたはRETURNでジャンプします。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

迫る障害物、ジャンプ状態、残りの耐久力、突破数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/play-02.png)

## ビルドと検証

バージョン 1.1.0。開始番地 `$0300`、ゲーム本体と定数は 5,890 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/gate_runner
make -C games/gate_runner test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py gate_runner --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
