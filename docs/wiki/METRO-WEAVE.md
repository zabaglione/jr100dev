# METRO WEAVE

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → METRO WEAVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/metro_weave)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

2つの分岐を切り替え、12本の列車を指定の駅へ送ります。分岐1が0ならA駅、1なら分岐2へ進み、分岐2の0/1でB/C駅へ向かいます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png)

## タイトルのデザイン

交差する三本の路線と駅、上部の車両で交通網を描き、路線の余白へロゴを配置しています。

## 画面の奥行き

列車と分岐スイッチを立体化し、線路の下に高架の側面と支柱を描きました。行先と信号の対応関係は水平の線路で保っています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を計器盤フォント**（角張った太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

W/Sで分岐を選び、A/DまたはRETURNで切り替えます。列車のカウント3より前に経路を設定してください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

路線、分岐状態、目的駅、列車の進行、輸送結果を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-02.png)

## ビルドと検証

バージョン 1.3.0。開始番地 `$0300`、ゲーム本体と定数は 6,399 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/metro_weave
make -C games/metro_weave test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py metro_weave --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
