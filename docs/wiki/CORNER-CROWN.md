# CORNER CROWN

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/corner-crown.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/corner-crown.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → CORNER CROWN

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=corner-crown) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/corner_crown)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

相手の石を自分の石で挟んで裏返します。双方が置けなくなったときに自分の石が多ければ勝利です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=corner-crown)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで位置を選び、RETURNで置きます。合法手がない場合はRETURNでパスします。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

挟んだ石は一枚ずつ、面が細くなって側面を見せ、反対の面が開く順に回転します。白から黒、黒から白の両方に途中の形と石返しの音があります。演出が終わってから次のキーを押してください。

盤面と双方の石数を表示します。角は裏返されないため重要です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/play-02.png)
