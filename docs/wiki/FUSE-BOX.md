# FUSE BOX

[ホーム](Home) → [パズル](Genre-Puzzle) → FUSE BOX

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=fuse-box) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/fuse_box)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

行と列に指定された個数だけスイッチを入れます。すべての個数が一致すれば、どの配置でも正解です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=fuse-box)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDでスイッチを選び、RETURNで入／切を反転します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

マスは面が細くなり、側面を見せてから反対の面が開く順に切り替わります。入／切の両方向に途中の形と効果音があります。演出が終わってから次のキーを押してください。

上の数字は列、左の数字は行の目標個数です。スイッチの入っている数が目標と一致すると、その数字が白黒反転します。入れ過ぎたりスイッチを切ったりして一致しなくなると通常表示に戻ります。連続したマス数ではなく、行・列それぞれの合計を合わせます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/play-02.png)
