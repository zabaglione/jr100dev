# CIRCUIT WORKS

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → CIRCUIT WORKS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=circuit-works) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/circuit_works)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

3段の論理ゲートを組み替え、4通りの入力に対する出力を目標の表へ一致させます。G1は入力AとB、G2はG1とA、G3はG2とBを計算します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/title.png)

## 操作と遊び方

W/Sでゲートを選択、A/DでAND・OR・XORを変更し、RETURNで試験します。画面のゲート記号A/B/Cは、それぞれAND/OR/XORです。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

左側に3段の回路、右側に入力・目標・実際の出力を並べます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/play-02.png)
