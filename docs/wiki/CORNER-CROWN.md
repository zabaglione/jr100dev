# CORNER CROWN

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → CORNER CROWN

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=corner-crown) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/corner_crown)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

相手の石を自分の石で挟んで裏返します。双方が置けなくなったときに自分の石が多ければ勝利です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/title.png)

## 画面の奥行き

明るい駒と中が暗い駒に縁の厚みを付けました。盤は正方格子のまま、角と挟み取りの範囲を判別しやすくしています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を活字フォント**（読みやすいセリフ体）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

WASDで位置を選び、RETURNで置きます。合法手がない場合はRETURNでパスします。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

盤面と双方の石数を表示します。角は裏返されないため重要です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/play-02.png)

## ビルドと検証

バージョン 1.2.1。開始番地 `$0300`、ゲーム本体と定数は 7,512 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/corner_crown
make -C games/corner_crown test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py corner_crown --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
