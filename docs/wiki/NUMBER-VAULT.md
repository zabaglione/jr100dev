# NUMBER VAULT

[ホーム](Home) → [パズル](Genre-Puzzle) → NUMBER VAULT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=number-vault) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/number_vault)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

1～4の4桁の暗証番号を、重複を含めて推理します。10回以内に正解すると次の金庫へ進みます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=number-vault)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで桁を選び、W/Sで数を変え、RETURNで試します。EXACTは数も位置も一致、NEARは数だけ一致した個数です。同じ数を重複して数えません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

暗号を開始時に変えます。ダイヤルを回す途中と4桁の照合を描き、直近6回の入力と位置一致・数字一致の数を残します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/play-02.png)
