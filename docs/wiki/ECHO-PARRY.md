# ECHO PARRY

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/echo-parry.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/echo-parry.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [アクション](Genre-Action) → ECHO PARRY

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/echo_parry)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

上段・下段の攻撃を見て受け流す全6戦。相手の体力は6から11へ増え、3戦目からは構えを途中で変えるフェイントが加わります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=echo-parry)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sで構えを選び、ATTACK中にRETURNで受け流します。攻撃の後半、COUNTER!の表示中なら2ダメージ。3連続の受け流しも2ダメージです。Aで後退すると、反撃を捨ててその攻撃を安全に避けられます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

立体的な決闘場を描き、攻撃の飛来、後退、反撃、装甲の点滅、撃破の破片を表示します。予告・フェイント・攻撃・反撃・回復時間を音と姿勢で追えます。演出が終わってから次のキーを押してください。

HEARTSは自分の体力、ARMORは相手の残り体力、CHAINは連続成功です。READY中や違う高さで受け流すと被弾。フェイントの後も攻撃の高さを見直します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-02.png)
