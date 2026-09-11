# AUCTION HOUSE

[ホーム](Home) → [経営・サバイバル](Genre-Management) → AUCTION HOUSE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=auction-house) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/auction_house)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

6つの品物の競売で、終了時の所持金52以上を目指します。落札品は表示価格で売却されます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/title.png)

## タイトルのデザイン

大きな木槌と積んだコインを左右に置き、落札の一打を強い白い形で表します。

## 画面の奥行き

出品物を厚い展示台に載せ、宝石と箱に面の明暗を付けました。相場・入札額・残金は右の帳簿パネルで確認できます。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を活字フォント**（読みやすいセリフ体）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 動きとクリア演出

クリア時は完成した盤面・結果を残し、約1.6秒のジングルと余韻を挟みます。その後、キーを押し直して次の操作に進みます。クリア直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。

## 操作と遊び方

WASDでBIDかPASSを選び、RETURNで確定します。入札は価格を2上げ、相手がさらに2上げる場合があります。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

品物、売却価格、入札額、所持金、落札数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/play-02.png)

## ビルドと検証

バージョン 1.4.0。開始番地 `$0300`、ゲーム本体と定数は 6,202 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/auction_house
make -C games/auction_house test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py auction_house --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
