# RUIN LEXICON

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → RUIN LEXICON

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ruin-lexicon) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/ruin_lexicon)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

4つの碑文と大小関係から、A〜Dへ1〜4を一度ずつ割り当てる全20問です。各問題の答えは一意です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=ruin-lexicon)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで文字を選び、W/Sで数字を変え、RETURNで碑文と照合します。試行は5回まで。同じ数字を複数の文字に割り当てたままでは正解になりません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

碑文を石板の枠に収め、回す数字に途中の形とSEを加えました。条件を一つずつ照合し、正誤をその場に残します。演出が終わってから次のキーを押してください。

左のA+B、B+C、C+Dの和とA/Dの大小関係を使います。試すと成立した条件に星、外れた条件にXが付きます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/play-02.png)
