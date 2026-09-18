# TWENTY ONE

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → TWENTY ONE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=twenty-one) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/twenty_one)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

21を超えずにディーラーより大きな合計を目指すカードゲームです。札は2～10。5回の勝負後にコイン8枚以上を残せば成功です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/demo-clear.png)

**[音付きプレイ動画を見る（約48秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=twenty-one)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDでHITかSTANDを選び、RETURNで確定します。ディーラーは17以上まで引きます。勝敗でコインが2枚増減します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

個々のカードと合計を表示します。配札と追加カードが山から移動し、ディーラーも一枚ずつ引きます。勝ち・バスト・負け・引き分けと収支を残してから次の手へ進みます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/play-02.png)
