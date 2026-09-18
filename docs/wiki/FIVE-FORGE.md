# FIVE FORGE

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → FIVE FORGE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=five-forge) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/five_forge)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

8×8の盤で相手より先に縦・横・斜めのいずれかに5個の石を並べます。相手は自分の連続を伸ばし、目前の勝ち筋を阻止します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/demo-clear.png)

**[音付きプレイ動画を見る（約35秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=five-forge)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで位置を選び、RETURNで石を置きます。自分はO、相手はXです。満杯まで勝てなければ失敗です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

石が落下し、着地してつぶれ、元の形に戻る四段階の動きとSEを付けました。自分と相手の着手を一手ずつ表示し、五連の石だけを3回点滅させてから結果を表示します。演出が終わってから次のキーを押してください。

右側に自分と相手の石数を表示します。CELLは現在選んでいる位置で、着手中は石を置いている位置に変わります。五連ができると該当する石だけが3回点滅し、その後で結果メッセージとジングルが流れます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/play-02.png)
