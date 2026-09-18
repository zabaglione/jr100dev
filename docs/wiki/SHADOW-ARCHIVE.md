# SHADOW ARCHIVE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/shadow-archive.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/shadow-archive.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → SHADOW ARCHIVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=shadow-archive) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/shadow_archive)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

帽子・眼鏡・ネクタイの特徴から6人の容疑者を絞る全12事件。必要な調書を選び、2件以下の閲覧で解決するとGOLD DETECTIVEになります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/demo-clear.png)

**[音付きプレイ動画を見る（約32秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=shadow-archive)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sで調書と告発を切り替え、A/Dで対象を選び、RETURNで開く・告発します。調書と容疑者は別々の選択位置を保持します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

容疑者の枠と調書の区切りを整え、紙が開く途中の形と音を加えました。選択先を明示し、告発した相手と結果を残して停止します。演出が終わってから次のキーを押してください。

容疑者の下の3文字は帽子・眼鏡・ネクタイの順にY＝あり、N＝なし。開いた調書と矛盾する容疑者にはXが付きます。読んだ調書を再び選んでも閲覧数は増えません。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/play-02.png)
