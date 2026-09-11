# SEED MERGE

[ホーム](Home) → [パズル](Genre-Puzzle) → SEED MERGE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=seed-merge) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/seed_merge)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

同じ数字の種を重ねて64を作る4×4のパズルです。盤面が動いたときに新しい2が現れ、動かせなくなると失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/seed-merge/title.png)

## タイトルのデザイン

芽から大きな木までの成長を左から右へ並べ、下の種と地面の線で栽培の循環を示します。

## 画面の奥行き

数字が3桁でも収まる幅の栽培槽を並べ、縁と手前の厚みを描きました。数字は水平に保ち、合成の判断を妨げない構成です。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を栽培フォント**（丸みのある太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 操作と遊び方

WASDで盤面全体をスライドします。同じ数字同士は1回の操作につき一度だけ合体します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

各マスの数字と最大値、移動回数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/seed-merge/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/seed-merge/play-02.png)

## ビルドと検証

バージョン 1.3.0。開始番地 `$0300`、ゲーム本体と定数は 7,160 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/seed_merge
make -C games/seed_merge test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py seed_merge --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
