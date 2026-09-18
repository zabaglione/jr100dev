# COMPASS ROSE

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → COMPASS ROSE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=compass-rose) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/compass_rose)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

最後に測った方角と距離帯から、埋まった遺物を探す全10地点。位置が変わっても測定結果は自動では変わりません。測る場所を選び、候補を絞ります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=compass-rose)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで移動、Xで測定、RETURNで掘ります。移動は補給1、測定は2。開始時の測定は無料で、追加は4回までです。掘り外せるのは2回で、3回目の空振りで失敗します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

測定では輪が3段階に広がり、歩行は途中の位置を通ります。掘る動きと穴、発見時の光と音を表示し、過去の測定地点を残します。演出が終わってから次のキーを押してください。

BEARINGはN/S/W/Eの方角、NEARは距離0〜2、MIDは3〜5、FARは6以上。距離は上下左右の合計です。FROMは測定地点の列・行、SURVEYSは残り測定、STEPSは補給、DIGSは掘れる回数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/play-02.png)
