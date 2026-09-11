# POTION PATH

[ホーム](Home) → [経営・サバイバル](Genre-Management) → POTION PATH

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=potion-path) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/potion_path)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

素材ごとの移動量を組み合わせ、調合の位置を注文のダイヤへ合わせます。6件の注文に各12回以内の投入で応えます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/title.png)

## タイトルのデザイン

左の大きな薬瓶から右上へ材料の経路を伸ばし、POTIONとPATHを道の入口と出口に置きます。

## 画面の奥行き

調合瓶に液面と反射、目標にくぼんだ受け皿を描きました。移動量を数えやすい格子と、水平なレシピ表示を保っています。

## ゲーム専用フォント

ゲーム中の**数字0〜9の10文字を栽培フォント**（丸みのある太線）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 動きとクリア演出

クリア時は完成した盤面・結果を残し、約1.6秒のジングルと余韻を挟みます。その後、キーを押し直して次の操作に進みます。クリア直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。

## 操作と遊び方

WASDで素材を選び、RETURNで加えます。灰は左2、苔は右1・下2、塩は上1、根は右3・下1です。盤外へ出る素材は加えられません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

調合位置、注文、素材の移動量、投入数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/play-02.png)

## ビルドと検証

バージョン 1.4.0。開始番地 `$0300`、ゲーム本体と定数は 6,495 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/potion_path
make -C games/potion_path test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py potion_path --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
