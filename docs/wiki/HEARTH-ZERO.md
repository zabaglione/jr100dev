# HEARTH ZERO

[ホーム](Home) → [経営・サバイバル](Genre-Management) → HEARTH ZERO

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=hearth-zero) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/hearth_zero)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

食料・薪・暖かさを配分し、寒い8日間を生き延びます。毎日食料と暖かさを消費し、3日ごとに寒さが強まります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/hearth-zero/title.png)

## 画面の奥行き

炉の開口部を奥に引っ込め、斜めの内壁と灰受けを描きました。炎の中心を抜いて明暗を付け、資源の数値は右の操作盤にまとめています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を石碑フォント**（上下の飾りを持つ刻印）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

WASDで仕事を選び、RETURNで1日を過ごします。薪と食料の採集は各+7。火は薪3で暖かさ+9、断熱は薪4を使い日々の熱損失を減らします。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

炉の火と、食料・薪・暖かさ・断熱段階・日数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/hearth-zero/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/hearth-zero/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,217 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/hearth_zero
make -C games/hearth_zero test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py hearth_zero --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
