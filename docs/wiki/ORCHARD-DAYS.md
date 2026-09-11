# ORCHARD DAYS

[ホーム](Home) → [経営・サバイバル](Genre-Management) → ORCHARD DAYS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orchard-days) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/orchard_days)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

種まき、水やり、収穫に日数を配分し、28日以内に果実18個を収穫します。4日ごとに雨が降ります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/title.png)

## タイトルのデザイン

大きさの違う三本の果樹を白いシルエットで描き、果実を黒い抜きで示す明るい農園の表紙です。

## 画面の奥行き

畑に畝を敷き、木の幹・実・接地影を描き分けました。成長段階の数字は木の下に残しています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を栽培フォント**（丸みのある太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 動きとクリア演出

クリア時は完成した盤面・結果を残し、約1.6秒のジングルと余韻を挟みます。その後、キーを押し直して次の操作に進みます。クリア直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。

## 操作と遊び方

WASDで畑を選び、RETURNで作業します。空いた畑は種まき、育成中は水やり、実った木は収穫です。収穫すると種が2個戻ります。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

畑の成長段階、日数、種、収穫数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/play-02.png)

## ビルドと検証

バージョン 1.4.0。開始番地 `$0300`、ゲーム本体と定数は 6,735 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/orchard_days
make -C games/orchard_days test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py orchard_days --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
