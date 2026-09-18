# RIBBON SNAKE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/ribbon-snake.html)

[ホーム](Home) → [アクション](Genre-Action) → RIBBON SNAKE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ribbon-snake) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/ribbon_snake)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

餌を食べて伸びる蛇を操作する全6庭。目標は8個から13個へ増え、岩も増えて通路が狭まります。頭を端・岩・胴体へ当てると失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/demo-clear.png)

**[音付きプレイ動画を見る（約40秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=ribbon-snake)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで向きを変え、RETURNでブレーキを使います。1面3回までで、4回の移動が半分の速さになります。今の進行方向と正反対の入力は受け付けません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

頭の向きと胴体を描き分け、マスの中間を通って全身が滑ります。ブレーキ中の表示、餌の回収音と光、衝突箇所での停止を加えました。演出が終わってから次のキーを押してください。

LENGTHは長さ、EATENは食べた数、BRAKESは残りブレーキ、GOALは目標です。餌へ直行するだけでなく、長くなる胴体の逃げ道を残します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/play-02.png)
