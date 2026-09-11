# TWENTY ONE

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → TWENTY ONE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=twenty-one) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/twenty_one)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

21を超えずにディーラーより大きな合計を目指すカードゲームです。札は2～10。5回の勝負後にコイン8枚以上を残せば成功です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/title.png)

## タイトルのデザイン

右上の大きな「21」を主役にし、左下の重なった札と右下のタイトルで卓上を構成します。

## 画面の奥行き

手札に厚みを付け、プレイヤーとディーラーの札を別々のトレーに配置しました。中央の所持金と選択肢には余白を残しています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を活字フォント**（読みやすいセリフ体）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 動きとクリア演出

クリア時は完成した盤面・結果を残し、約1.6秒のジングルと余韻を挟みます。その後、キーを押し直して次の操作に進みます。クリア直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。

## 操作と遊び方

WASDでHITかSTANDを選び、RETURNで確定します。ディーラーは17以上まで引きます。勝敗でコインが2枚増減します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

自分と相手の合計、コイン、ラウンドを表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/play-02.png)

## ビルドと検証

バージョン 1.4.0。開始番地 `$0300`、ゲーム本体と定数は 6,331 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/twenty_one
make -C games/twenty_one test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py twenty_one --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
