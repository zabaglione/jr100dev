# CIRCUIT WORKS

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/circuit-works.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/circuit-works.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → CIRCUIT WORKS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=circuit-works) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/circuit_works)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

3段の論理ゲートを組み替え、3入力A・B・Cの8通りすべてで目標Wを満たす全22問です。G1はAとB、G2はG1とC、G3はG2とAを計算します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=circuit-works)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sでゲートを選び、A/DでAND・OR・XORを変更、RETURNで8行を試験します。ANDは両方が1、ORは一方以上が1、XORは片方だけが1のとき1です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

ゲートをつなぐ配線とソケットを加え、信号の0/1が3段のゲートを通る途中の位置を見せます。各行の照合結果を音と印で残します。演出が終わってから次のキーを押してください。

右の表はA・B・C・W・NOWの順。Wが目標、NOWが今回の出力です。各行の星印は一致、Xは不一致。MATCHEDは一致した行数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/play-02.png)
