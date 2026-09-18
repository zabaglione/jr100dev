# PRISM TRACE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/prism-trace.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/prism-trace.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → PRISM TRACE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=prism-trace) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/prism_trace)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

6枚の鏡を回転し、左から入る光を右上の受光器へ届けます。光路は鏡を回すたびに更新されます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=prism-trace)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで鏡の位置を選び、RETURNで / と反対向きの鏡を切り替えます。盤面の上と右にある矢印の交点が選択位置です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

鏡を回すと、光がつながった線として伸びていきます。鏡の面で線が折れ曲がり、反射音とともに受光器までの経路を追えます。演出が終わってから次のキーを押してください。

光路は途切れない線で示し、鏡の位置で折れ曲がります。側面に回転回数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/play-02.png)
