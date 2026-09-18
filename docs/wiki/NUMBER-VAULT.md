# NUMBER VAULT

[ホーム](Home) → [パズル](Genre-Puzzle) → NUMBER VAULT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=number-vault) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/number_vault)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

1〜4の数字を4桁並べ、金庫の暗証番号を10回以内に推理する全10問。数字は重複することがあり、開始ごとに暗証番号が変わります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=number-vault)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで桁を選び、W/Sで数字を回し、RETURNで試します。EXACTは数字と位置の一致、NEARは数字が合っていて位置が違う個数です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

4つのダイヤルが回り、判定が1桁ずつ進みます。全桁一致では扉が幅を変える3段階の開閉を行い、開錠音と光からジングルへ続きます。演出が終わってから次のキーを押してください。

直近6回の入力と回答を画面に残します。同じ暗証番号の1桁を二重には数えません。候補が減る入力を選び、残り回数を節約します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/play-02.png)
