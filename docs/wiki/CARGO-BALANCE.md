# CARGO BALANCE

[ホーム](Home) → [経営・サバイバル](Genre-Management) → CARGO BALANCE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=cargo-balance) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/cargo_balance)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

船の傾きを抑えながら12個の積荷を載せます。左右の傾きの差が8を超えると失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/title.png)

## 画面の奥行き

船に甲板・船腹・水面の段差を付け、積荷には斜めの側面を描きました。荷重の数字と左右の釣り合いは従来の位置で確認できます。

## 操作と遊び方

A/Dでクレーンを動かし、RETURNで次の荷を落とします。外側の船倉は重みが3倍、各船倉には4個まで置けます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

積荷、次の重さ、左右の負荷、積載数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/play-02.png)

## ビルドと検証

バージョン 1.1.0。開始番地 `$0300`、ゲーム本体と定数は 5,967 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/cargo_balance
make -C games/cargo_balance test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py cargo_balance --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
