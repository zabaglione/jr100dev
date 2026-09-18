# ORBIT DODGE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/orbit-dodge.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/orbit-dodge.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [アクション](Genre-Action) → ORBIT DODGE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-dodge) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/orbit_dodge)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

外周と内周の2軌道を渡り、照準からの光線を避ける全6面です。12波から22波へ増え、後半は両軌道への同時照射と短い予告時間に挑みます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/demo-clear.png)

**[音付きプレイ動画を見る（約49秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=orbit-dodge)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/DまたはW/Sで軌道上を左右に移動し、RETURNで内外の軌道を切り替えます。照射の瞬間に菱形のエネルギーへ乗ると加点。連続取得は1点、2点、3点と増えます。照準位置に残ると被弾します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

セミグラフィックスで2本の軌道を描き、移動の軌跡、照準から伸びる光線、回収の光とSEを加えました。小さな軌道点・照準・エネルギーは別の形です。演出が終わってから次のキーを押してください。

HULLは体力、IMPACTは発射までのカウント、WAVEは消化した波と目標、ENERGYは得点。目標の波数以上のエネルギーでGOLD ORBITになります。取得を狙う移動と、安全な軌道への退避を選びます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/play-02.png)
