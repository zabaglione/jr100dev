# PENDULUM PORT

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/pendulum-port.html)

[ホーム](Home) → [アクション](Genre-Action) → PENDULUM PORT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=pendulum-port) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/pendulum_port)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

振り子から手を離し、足場へ飛び移る全6区間。6回から11回の着地を続けます。足場の中央は2点、端は1点で、後半には中央しか着地できない足場も現れます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=pendulum-port)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dでロープの長さを1〜3に変え、RETURNで手を離します。移動している方向へロープの長さだけ進んで落ちます。V印が現在の着地点予告です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

岸壁と波をセミグラフィックスで描き、振り子、放物線の跳躍、着地と落下の途中の位置を表示します。中央への着地は光と音で区別します。演出が終わってから次のキーを押してください。

ROPEはロープの長さ、矢印は振れる方向、CENTREは着地点の得点、ROPESは残り挑戦回数、PORTSは渡った足場の数です。中央の菱形を狙うか、広い端で確実に進むかを選びます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/play-02.png)
