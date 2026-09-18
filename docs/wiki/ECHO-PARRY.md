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

**[音付きプレイ動画を見る（約42秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=echo-parry)**

1ステージのクリアまでを収録。

## 操作と遊び方

Wで上段、Sで下段の構えを選び、攻撃中にRETURNで受け流します。予備動作と立て直しの間は待ちます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

敵の攻撃、盾での受け止め、反撃の飛翔、命中を順に描きます。攻撃の高さは単純な交互から8手のパターンへ変えました。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-02.png)
