# MEMORY MOSAIC

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/memory-mosaic.html)

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → MEMORY MOSAIC

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=memory-mosaic) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/memory_mosaic)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

16枚の札から8組を見つける、毎回配札が変わる全10面の神経衰弱です。許される不一致は序盤12回、終盤9回。続けて組を当てるとCHAINが伸びます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/demo-clear.png)

**[音付きプレイ動画を見る（約86秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=memory-mosaic)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで札を選び、RETURNでめくります。2枚を確認した後はRETURNでもう一度進めます。不一致の札は裏へ戻り、一致した札は表のまま残ります。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

札ごとの枠と厚みを加え、表面が細くなり、側面を経て反対側が開く5段階の反転を使います。一致・不一致の音と確認の間があり、連続一致を数えます。演出が終わってから次のキーを押してください。

PAIRSは揃った組、MISSESは不一致の回数と上限、CHAINは連続で当てた組の数です。開いた絵柄と位置を覚え、見覚えのある組から確定していきます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/play-02.png)
