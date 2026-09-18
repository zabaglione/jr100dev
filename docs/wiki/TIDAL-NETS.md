# TIDAL NETS

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/tidal-nets.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/tidal-nets.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [経営・サバイバル](Genre-Management) → TIDAL NETS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tidal-nets) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/tidal_nets)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

潮流を読んで網を投げる全3漁場。浅い魚は2点、深い魚は4点。ロープ12本・最大9回の投網で、30・33・36点を目指します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/demo-clear.png)

**[音付きプレイ動画を見る（約38秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=tidal-nets)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで位置を選び、W/SでFINE NETとWIDE NETを切り替え、RETURNで投げます。細い網は1列・ロープ1、広い網は隣接2列・ロープ2です。選んだ網は次の投網でも続きます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

水面の波、沈む網、潮に流れる2群、釣果を引き上げる動きを別々に表示し、投網・獲得・空振りの音を分けます。演出が終わってから次のキーを押してください。

TIDEは向きと強さ。投げると浅い魚はその分、深い魚は2倍流されてから網に掛かります。FISHは得点、CASTSは残り投網回数。2群を広い網で取れる機会にロープを回します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/play-02.png)
