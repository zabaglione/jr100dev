# NIGHT SWARM

[ホーム](Home) → [アクション](Genre-Action) → NIGHT SWARM

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=night-swarm) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/night_swarm)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

8方向へ逃げながら18体の敵を倒します。ごく近い敵への射撃は自動で、範囲攻撃には再使用までの待ち時間があります。接触4回で失敗です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/title.png)

## 紹介画像とプレイ動画

**[音付きプレイ動画を見る（約33秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=night-swarm)**

1ステージのクリアまでを収録。途中を省略せず、通常の速度で収録しています。画面を確認する間を入れた自動キー入力によるプレイです。

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-start.png)

[![操作を進めた場面・クリックで動画](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-play.png)](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=night-swarm)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-clear.png)

## 操作と遊び方

QWE／AD／ZXCで8方向移動、RETURNで準備済みのパルスを放ちます。Sは移動に使いません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

倒した敵は、発光して破片が外側へ散る順に消えます。接触時は被弾音と点滅が入り、危険な位置を確認できます。演出が終わってから次のキーを押してください。

右側に耐久力、撃破数、パルスの再使用待ちを表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/play-02.png)
