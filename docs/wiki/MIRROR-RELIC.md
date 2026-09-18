# MIRROR RELIC

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/mirror-relic.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/mirror-relic.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → MIRROR RELIC

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=mirror-relic) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/mirror_relic)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

移動と90度の鏡回転で3つの遺物を集め、門へ着く全6面です。遺物のA〜Dは必要な位相で、同じ位相のときに踏むと回収できます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/demo-clear.png)

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=mirror-relic)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで歩き、RETURNで時計回り、Xで反時計回りに位置を回転させます。回転するとPHASEも1段進むか戻ります。時計回りの移動先は矢印で予告され、壁の位置へは回転できません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

陰影のある壁と遺物の位相文字を描き分け、歩行と鏡移動に途中の位置、SE、回収の光を使います。回転前の予告で到着位置を確認できます。演出が終わってから次のキーを押してください。

RELICSは残る遺物、ROTATIONSは回転回数、PHASEは現在の位相。回転は20回まで。通路で回転後の位置関係を変え、遺物の位相に合わせて回収します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/play-02.png)
