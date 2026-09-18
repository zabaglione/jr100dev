# LUNAR TOUCHDOWN

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/lunar-touchdown.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/lunar-touchdown.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [アクション](Genre-Action) → LUNAR TOUCHDOWN

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lunar-touchdown) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/lunar_touchdown)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

燃料を使って降下速度を抑え、月面へ着陸する全6地点です。幅広い着陸場のほか、星印の狭い着陸場では10点の追加点を得られます。後半は横風が反転します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=lunar-touchdown)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで1文字ずつ横移動。WまたはRETURNで噴射し、燃料1を使って降下速度を2減らします。着陸時の速度は2以下が必要です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

月の地形と遠景をセミグラフィックスで描き、降下の中間位置と噴射炎を表示します。速度超過・着陸場の外を区別して停止し、着陸には光とジングルを合わせます。演出が終わってから次のキーを押してください。

FUELは燃料、FALLは降下速度、ALTは高度、WINDは横風の向き。着陸点は残り燃料に、狭い着陸場なら10点、速度1以下なら4点を加えた値です。遠い着陸場へ挑むか、燃料を残して広い場所へ降りるかを選びます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/play-02.png)
