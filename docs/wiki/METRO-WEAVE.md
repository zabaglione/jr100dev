# METRO WEAVE

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → METRO WEAVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/metro_weave)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

2つの分岐を切り替え、点灯した駅へ12本の列車を届けます。列車は1本ずつ出発し、行先はA・B・Cから指定されます。誤配3回で終了です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-clear.png)

**[音付きプレイ動画を見る（約80秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=metro-weave)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sで分岐を選び、A/DまたはRETURNで切り替えます。上の分岐がAならA駅、下向き矢印なら下の分岐で指定したB/C駅へ進みます。出発から3歩目に進む前に経路を設定してください。到着後は分岐が1つ切り替わるので、次の目的地に合わせて再確認します。READY表示中は列車が出発を待ち、分岐を設定できます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

今回の目的地は、盤面右端の大きなA・B・Cのうち、白く点灯して枠が点滅する駅です。A・B・Cすべてを使い、同じ駅が続く配車もあります。到着演出中は目的地とNEXTの3本の予告を固定し、次の出発時に一度だけ更新します。到着は光と音、誤配は原因表示と停止で示し、最後の列車は到着したホームに残ります。演出が終わってから次のキーを押してください。

SERVEDは成功数、LIVESは残りライフです。NEXTは左から順に、今回の列車の後に来る3本の行先です。同じ駅が続く場合も、列車ごとに1本ずつ届いたことを確認してから次へ進みます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-02.png)
