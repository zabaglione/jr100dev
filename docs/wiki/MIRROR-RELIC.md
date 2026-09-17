# MIRROR RELIC

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → MIRROR RELIC

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=mirror-relic) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/mirror_relic)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

自分の位置を部屋の中心に対して回転させ、壁で区切られた場所から3個の遺物を回収して出口へ進みます。壁は回転しません。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/demo-clear.png)

**[音付きプレイ動画を見る（約34秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=mirror-relic)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで歩き、RETURNで自分の位置を90度回転します。回転先が壁なら動けません。回転は20回までです。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

探索者の向きと、マスの中間を通る移動を表示します。鏡を使う前後の位置を音とともに確認できます。演出が終わってから次のキーを押してください。

部屋の区画、遺物と出口、残る遺物数、回転回数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/play-02.png)
