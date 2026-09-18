# WORD FOUNDRY

[Wiki](https://github.com/zabaglione/jr100dev/wiki/WORD-FOUNDRY) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=word-foundry)

3文字の単語を1文字ずつ変え、VIAの中継単語を通ってTARGETへ到達する全16問です。最短5〜9手の経路に、2手の余裕があります。

![タイトル](images/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](images/demo-start.png)

![操作を進めた場面](images/demo-play.png)

![最初の目標を達成した場面](images/demo-clear.png)

**[音付きプレイ動画を見る（約33秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=word-foundry)**

1ステージのクリアまでを収録。

## タイトルのデザイン

コンベヤー上のA・B・Cの活字を白抜きと輪郭で並べ、横長WORDで文字を作る工場を表します。

## 画面の奥行き

単語を厚みのある札に並べ、差し替わる文字が浮いて移る様子を表示します。中継点の到達音と光、経路の履歴で進行を追えます。

## ゲーム専用フォント

ゲーム中の**英大文字A〜Zの26文字を活字フォント**（読みやすいセリフ体）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。

## 動きとクリア演出

単語を厚みのある札に並べ、差し替わる文字が浮いて移る様子を表示します。中継点の到達音と光、経路の履歴で進行を追えます。被弾や結果を確認する間は、追加入力で表示を飛ばせません。

クリア時は完成した盤面・結果を残し、約1.6秒のジングルと余韻を挟みます。失敗時も原因を表示し、ジングルの後に短い間を置きます。その後、キーを押し直して次の操作に進みます。直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。

## 操作と遊び方

WASDで単語を選び、RETURNで変更します。現在の単語と1文字だけ違う候補には星印が付きます。VIAに到達すると印が付き、その後にTARGETへ進めばクリアです。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

単語を厚みのある札に並べ、差し替わる文字が浮いて移る様子を表示します。中継点の到達音と光、経路の履歴で進行を追えます。演出が終わってから次のキーを押してください。

CURRENTは現在の単語、VIAは中継点、TARGETは到着点、PARは最短手数、LEFTは残り手数。画面下に直近8語の経路が残ります。

![ゲーム開始時](images/play-01.png)

![プレイ中の場面](images/play-02.png)

## ビルドと検証

バージョン 2.0.0。開始番地 `$0300`、ゲーム本体と定数は 7,932 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/word_foundry
make -C games/word_foundry test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py word_foundry --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
