# FUSE BOX

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/fuse-box.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → FUSE BOX

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=fuse-box) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/fuse_box)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

行と列に指定された個数だけスイッチを入れます。すべての個数が一致すれば、どの配置でも正解です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/demo-clear.png)

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=fuse-box)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDでスイッチを選び、RETURNで入／切を反転します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

マスは面が細くなり、側面を見せてから反対の面が開く順に切り替わります。入／切の両方向に途中の形と効果音があります。演出が終わってから次のキーを押してください。

上の数字は列、左の数字は行の目標個数です。スイッチの入っている数が目標と一致すると、その数字が白黒反転します。入れ過ぎたりスイッチを切ったりして一致しなくなると通常表示に戻ります。連続したマス数ではなく、行・列それぞれの合計を合わせます。

攻略では、必要数の多い行から埋めます。上の数字から、その列にすでに入れた数を引き、「あと何個必要か」を数えてください。残り個数の多い列を優先し、同じ個数なら近いマスを選びます。行の数字が反転したら次の行へ移り、列の残り個数を数え直します。反転した行・列には、それ以上入れません。

1面の動画では、左の「3」がある上から2行目と、上の「3」がある左端の列の交点から始めます。そこから同じ行にあと2個を入れて「3」を反転させ、残り個数を見ながらほかの行を埋めていきます。中央から始める必要はなく、すべての行・列の個数が合えば別の配置でもクリアできます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/play-02.png)
