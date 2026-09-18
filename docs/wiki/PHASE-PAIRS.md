# PHASE PAIRS

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/phase-pairs.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/phase-pairs.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → PHASE PAIRS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=phase-pairs) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/phase_pairs)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

隣り合う2つの数を選び、合計10にして16マスをすべて消します。縦横の組み合わせを読み、孤立した数を残さないようにします。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/demo-clear.png)

**[音付きプレイ動画を見る（約34秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=phase-pairs)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで数を選び、RETURNで1個目と2個目を指定します。1個目の駒には上辺に印が付き、右側のPAIRに選んだ数を表示します。隣接して合計10になる候補は、すべて枠が点滅します。点滅する駒へ移動し、RETURNで2個目を決めます。斜めと同じ駒は組にできません。6回誤ると失敗です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

1枚目を選ぶと、隣接して合計10になる候補の枠がすべて点滅します。数字を読める状態で次の選択先を示します。合計10になる2枚は中央へ寄り合い、大きな「10」に合体してから光を散らして消えます。選択音と合体音で一組ずつの成立を確認できます。誤った組は盤面を残し、隣接していないのか、合計が10ではないのかを表示します。演出が終わってから次のキーを押してください。

MAKE 10は目標の合計、PAIRは選択中の2数、LEFTは残る駒、MISSは6回までのミス数です。盤面下の8個のゲージは、消した組の数だけ点灯します。NEIGHBORS ONLYは隣接していない組、SUM MUST BE 10は合計が10ではない組を選んだ印です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/play-02.png)
