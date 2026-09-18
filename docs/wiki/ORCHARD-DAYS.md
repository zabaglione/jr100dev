# ORCHARD DAYS

[ホーム](Home) → [経営・サバイバル](Genre-Management) → ORCHARD DAYS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orchard-days) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/orchard_days)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

4×4の畑で作物を育てる全3季。28日以内に18・24・30点の収穫を目指します。早いベリーは2回育てて3点、遅いリンゴは4回育てて7点です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/demo-clear.png)

**[音付きプレイ動画を見る（約33秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=orchard-days)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで畑や下段の道具を選び、RETURNで作業します。BERRY／APPLEで植える種類を選択。空き畑には種まき、育成中なら水やり、実った作物なら収穫です。WAITは1日待機、WELLは1日を使って水を3補給します。種類の選択では日数を使いません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

畑の囲いと計器を整え、種・水滴が飛び、雨や水やりで対象の作物が1段ずつ育つ様子を表示します。収穫物が得点へ移る動きとSEも加えました。演出が終わってから次のキーを押してください。

種は8、水は6で開始。種まきで種1、水やりで水1を使い、収穫すると種1が戻ります。雨は4・5・6日ごとで、全作物が1段育ち、水が4増えます。水は最大9。RAIN INで次の雨を読み、井戸へ行く日と作物を選びます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/play-02.png)
