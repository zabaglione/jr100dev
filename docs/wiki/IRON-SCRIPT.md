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

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=iron-script)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで命令枠を選び、W/Sで上下左右の矢印か「-」（待機）へ変更し、RETURNで実行します。実行後も命令を修正できます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

実行している命令を矢印で示し、ロボットの向きと中間移動を表示します。壁に当たると接触地点が点滅し、未到達で命令を使い切った場合は編集を促します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/play-02.png)
