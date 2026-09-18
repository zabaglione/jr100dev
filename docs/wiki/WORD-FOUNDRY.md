# WORD FOUNDRY

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/word-foundry.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/word-foundry.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → WORD FOUNDRY

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=word-foundry) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/word_foundry)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

3文字の単語を1文字ずつ変え、VIAの中継単語を通ってTARGETへ到達する全16問です。最短5〜9手の経路に、2手の余裕があります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/demo-clear.png)

**[音付きプレイ動画を見る（約33秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=word-foundry)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで単語を選び、RETURNで変更します。現在の単語と1文字だけ違う候補には星印が付きます。VIAに到達すると印が付き、その後にTARGETへ進めばクリアです。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

単語を厚みのある札に並べ、差し替わる文字が浮いて移る様子を表示します。中継点の到達音と光、経路の履歴で進行を追えます。演出が終わってから次のキーを押してください。

CURRENTは現在の単語、VIAは中継点、TARGETは到着点、PARは最短手数、LEFTは残り手数。画面下に直近8語の経路が残ります。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/play-02.png)
