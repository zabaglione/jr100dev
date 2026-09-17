# IRON SCRIPT

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → IRON SCRIPT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=iron-script) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/iron_script)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

ロボットに12枠の命令列を渡し、壁を避けてダイヤの端末へ導きます。20の異なる地形に挑戦します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=iron-script)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで命令枠を選び、W/Sで命令を変更、RETURNで実行します。0は待機、1は上、2は下、3は左、4は右です。実行後も命令を修正できます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

ロボットが進行方向を向き、マスの中間を通って移動します。移動音に合わせ、命令を実行する順序を追えます。演出が終わってから次のキーを押してください。

右側に残りの命令数、壁に当たった回数、命令列を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/play-02.png)
