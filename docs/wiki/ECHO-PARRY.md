# ECHO PARRY

[ホーム](Home) → [アクション](Genre-Action) → ECHO PARRY

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/echo_parry)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

相手の予備動作を読み、攻撃に合わせて8回の反撃を成功させます。3回のミスで決闘に敗れます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=echo-parry)**

1ステージのクリアまでを収録。

## 操作と遊び方

Wで上段、Sで下段の構えを選び、攻撃中にRETURNで受け流します。予備動作と立て直しの間は待ちます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

攻撃が当たると対象が点滅し、撃破時は発光して破片が散ります。防御を誤ると被弾音と短い停止が入り、失敗した方向を確認できます。演出が終わってから次のキーを押してください。

相手の攻撃位置、盾の高さ、攻撃段階、成功数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-02.png)
