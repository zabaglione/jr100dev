# POTION PATH

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/potion-path.html)

[ホーム](Home) → [経営・サバイバル](Genre-Management) → POTION PATH

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=potion-path) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/potion_path)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

4種の材料で薬を移動させ、菱形の調合点へ届ける全20問です。材料は各4回まで、合計12回まで。毒のX印へ着地できないため、材料の残数と順序を考えます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/demo-clear.png)

**[音付きプレイ動画を見る（約35秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=potion-path)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで材料を選び、RETURNで注ぎます。ASHは左へ2、MOSSは右へ1・下へ2、SALTは上へ1、ROOTは右へ3・下へ1です。盤外・毒・在庫切れの操作では材料を消費しません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

毒の着地点を枠付きのXで示し、材料が容器から飛び、薬が次の位置へ移る過程を表示します。在庫切れと毒への着地を異なる短い原因表示で知らせます。演出が終わってから次のキーを押してください。

右側の各材料に残数、DOSESに使用回数、PARに最短回数を表示します。毒を飛び越えることはできますが、着地点にはできません。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/play-02.png)
