# TWENTY ONE

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → TWENTY ONE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=twenty-one) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/twenty_one)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

52枚の山札で遊ぶブラックジャック。7回の勝負を終えて、持ち金を10から12以上へ増やせばクリアです。同じ山札の途中でカードは重複せず、使い切ると切り直します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/demo-clear.png)

**[音付きプレイ動画を見る（約59秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=twenty-one)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/DでHIT・STAND・DOUBLEを選び、RETURNで決定。HITは1枚引き、STANDは勝負、DOUBLEは賭け金を4にして1枚だけ引き勝負します。DOUBLEは最初の2枚かつ持ち金4以上で選べます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

カードの枠内に数字・絵札とスートを並べ、伏せ札を区別します。配る途中の移動、相手の追加ドロー、勝敗と持ち金の増減を順番に見せ、各勝負の確認時間を設けます。演出が終わってから次のキーを押してください。

Aは1または11、絵札は10です。通常の賭け金は2、最初の2枚で21なら勝利時に3増えます。相手は17まで引きます。引き分けは持ち金が変わりません。相手の2枚目は勝負まで伏せられ、持ち金2未満で終了です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/play-02.png)
