# STONE BALANCE

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → STONE BALANCE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=stone-balance) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/stone_balance)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

3つの山から1〜3個ずつ取り合う全10局です。前半5局は最後の石を取った側が勝ち、後半5局は取った側が負けになります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/demo-clear.png)

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=stone-balance)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sで山、A/Dで取る数を選び、RETURNで取ります。複数の山から同時には取れません。相手も勝てる手を選ぶので、残す山の形を考えます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

厚みのある棚に石を並べ、選んだ石が1個ずつ盤外へ飛びます。自分と相手の手を別の間と音で示し、最後の石を確認してから結果を出します。演出が終わってから次のキーを押してください。

LAST STONE WINS／LOSESが今回の勝敗条件、TAKEが取る数、RIVAL TOOKが相手の直前の個数。取る対象の石に矢印が付きます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/play-02.png)
