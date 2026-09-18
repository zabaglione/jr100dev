# STAR LANCE

[ホーム](Home) → [アクション](Genre-Action) → STAR LANCE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/star_lance)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

移動する18機の編隊を倒す全6波のシューティング。装甲機は耐久力2、後半は装甲列が増え、自機を狙う弾も増えます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/demo-clear.png)

**[音付きプレイ動画を見る（約52秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=star-lance)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで横移動、RETURNで通常弾、Wで重い弾を撃ちます。通常弾は1ダメージ・熱2、重い弾は2ダメージ・熱4。熱の上限は8で、時間とともに冷えます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

星の遠景、飛ぶ通常弾と太い重弾、敵の弾を表示します。装甲が剥がれる点滅と、撃破時の発光・破片を別にし、過熱と被弾も音で知らせます。演出が終わってから次のキーを押してください。

HULLは体力、ENEMIESは残りの敵、HEATは発射熱。重い弾で装甲を一撃で倒すか、熱を抑えて続けて撃つかを選びます。体力0、または編隊が逃げ切ると失敗です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/play-02.png)
