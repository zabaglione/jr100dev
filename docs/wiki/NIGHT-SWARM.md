# NIGHT SWARM

[ホーム](Home) → [アクション](Genre-Action) → NIGHT SWARM

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=night-swarm) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/night_swarm)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

8方向へ逃げながら18体の敵を倒します。ごく近い敵への射撃は自動で、範囲攻撃には再使用までの待ち時間があります。接触4回で失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-clear.png)

**[音付きプレイ動画を見る（約60秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=night-swarm)**

1ステージのクリアまでを収録。

## 操作と遊び方

QWE／AD／ZXCで8方向移動、RETURNで準備済みのパルスを放ちます。Sは移動に使いません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

主人公と敵の中間移動、広がるパルス、再使用可能の表示を追加しました。装甲のある敵は2回の命中が必要で、被弾点滅と撃破時の破片を区別します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/play-02.png)
