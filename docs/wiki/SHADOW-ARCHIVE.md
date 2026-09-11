# SHADOW ARCHIVE

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → SHADOW ARCHIVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=shadow-archive) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/shadow_archive)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

記録を読み、階とバッジ番号の条件から容疑者を特定する6件の小さな推理です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/title.png)

## 画面の奥行き

人物に接地影を付け、名簿と調査メモを厚みのある別のパネルにまとめました。人物の記号と証言は平面の文字で表示します。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を活字フォント**（読みやすいセリフ体）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

W/Sで閲覧と告発を切り替え、A/Dで資料または容疑者を選び、RETURNで実行します。A～Fのバッジは0～5、A～Cは1階、D～Fは2階です。誤った告発は即失敗です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

ファイルの手掛かりと、選択中の容疑者・操作モードを表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,222 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/shadow_archive
make -C games/shadow_archive test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py shadow_archive --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
