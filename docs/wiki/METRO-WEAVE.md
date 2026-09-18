# METRO WEAVE

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → METRO WEAVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/metro_weave)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

2つの分岐を切り替え、12本の列車を指定の駅へ送ります。分岐1が0ならA駅、1なら分岐2へ進み、分岐2の0/1でB/C駅へ向かいます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-clear.png)

**[音付きプレイ動画を見る（約69秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=metro-weave)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sで分岐を選び、A/DまたはRETURNで切り替えます。列車のカウント3より前に経路を設定してください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

列車が途中の位置を通って線路を分岐し、到着すると光と音で乗降を示します。誤ったホームでは原因を表示して停止します。続く列車の行先も予告します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-02.png)
