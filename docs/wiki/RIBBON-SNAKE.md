# RIBBON SNAKE

[ホーム](Home) → [アクション](Genre-Action) → RIBBON SNAKE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ribbon-snake) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/ribbon_snake)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

自動で進む蛇を操り、12個のダイヤを食べます。伸びた体や画面端にぶつかると失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/title.png)

## タイトルのデザイン

画面を折り返す長い蛇を二重の輪郭で描き、体が作る空間にSNAKEの文字を収めています。

## 画面の奥行き

頭と胴を丸みのある形にし、光沢と下側の影を付けました。盤面の厚みを加えつつ、通れるマスは正方格子で示します。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字をスピードフォント**（右へ傾く太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

WASDで進む向きを変更します。真後ろへの反転は受け付けません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

頭と伸びた体、食料、成長数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/play-02.png)

## ビルドと検証

バージョン 1.3.0。開始番地 `$0300`、ゲーム本体と定数は 6,791 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/ribbon_snake
make -C games/ribbon_snake test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py ribbon_snake --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
