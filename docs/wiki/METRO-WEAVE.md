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

**[音付きプレイ動画を見る（約100秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=metro-weave)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sでポイント[1]・[2]を選び、A/DまたはRETURNで切り替えます。[1]の右向き矢印はA駅、下向き矢印は斜めの連絡線で[2]へ進む設定です。[2]は右向きならB駅、下向きならC駅へ進みます。太い線路が現在つながっている経路です。列車が各ポイントを通る前に設定してください。通過後に変更したポイントは、今の列車の進路を変えません。READY表示中にも操作でき、到着しても設定は変わりません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

切替ポイント1はA駅への直進／ポイント2への下り、ポイント2はB駅への直進／C駅への下りを選びます。選んだ経路は太い線路でつながり、列車は連絡線を1マスずつ曲がって進みます。各ポイントは列車がそこへ来た時点で判定し、設定は手で変えるまで保ちます。目的駅の大型看板は点灯と枠の点滅で示し、到着中は行先と次の3本の予告を固定します。演出が終わってから次のキーを押してください。

白く点灯して枠が点滅する大型看板が今回の目的駅です。ROUTEは現在のポイント設定でつながる駅、SERVEDは成功数、LIVESは残りライフです。NEXTは今回の列車の後に来る3本の行先で、左から順に出発します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-02.png)
