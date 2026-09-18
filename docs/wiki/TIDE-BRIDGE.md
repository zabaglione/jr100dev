# TIDE BRIDGE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/tide-bridge.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → TIDE BRIDGE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tide-bridge) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/tide_bridge)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

行または列の橋をまとめて上下させ、左下の岸と右上の門をつなぎます。3種類の橋の配置に挑戦します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=tide-bridge)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sで対象の行・列を選び、A/Dで行と列を切り替え、RETURNで反転します。選択した行・列全体が白黒反転し、両端の矢印で範囲を示します。主人公と門はその上に表示されます。1面30回まで変更できます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

道がつながると、主人公が進行方向を向き、マスの中間を通って門まで歩きます。到着後は両手を上げて2回跳ね、喜びの効果音に続いてクリアのジングルが鳴ります。演出が終わってから次のキーを押してください。

SELECTの下にROW（行）またはCOL（列）と1〜6の番号を表示します。CHANGESは変更回数です。道がつながると主人公が門へ向かい、到着を喜んでからステージクリアになります。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/play-02.png)
