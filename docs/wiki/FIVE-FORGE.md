# FIVE FORGE

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → FIVE FORGE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=five-forge) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/five_forge)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

8×8の盤で相手より先に縦・横・斜めのいずれかに5個の石を並べます。相手は自分の連続を伸ばし、目前の勝ち筋を阻止します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/title.png)

## 操作と遊び方

WASDで位置を選び、RETURNで石を置きます。自分はO、相手はXです。満杯まで勝てなければ失敗です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

自分と相手が石を置く様子を一手ずつ表示します。着手音と短い間で、相手が置いた位置を確認できます。演出が終わってから次のキーを押してください。

石数と自分・相手の記号を盤の右に表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/play-02.png)
