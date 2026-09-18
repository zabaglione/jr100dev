# STAR LANCE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/star-lance.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/star-lance.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [アクション](Genre-Action) → STAR LANCE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/star_lance)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

攻撃予告を見て、撃ち落として反撃を止めるか、弾を避けて冷やすかを選ぶ全6波のシューティング。1波18機、後半は三方向弾と装甲列が増えます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=star-lance)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dまたはパッド左右の長押しで1文字ずつ連続移動します。RETURNまたはパッドのボタンで通常弾、Wまたはパッド上で重い弾。押し続けると連射でき、移動と射撃を同時に行えます。通常弾は1ダメージ・熱3、重い弾は2ダメージ・熱5で、発射間隔も長くなります。熱が12に達するとCOOLINGが表示され、一定時間撃てなくなります。移動は続けられます。撃つのを休み、冷えてから次の攻撃に備えます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

編隊は1文字ずつ移動し、自弾・敵弾の飛翔中も戦闘が進みます。装甲への命中は点滅、撃破は発光・破片・散開・消失の順に表示します。攻撃予告、発射、命中、冷却成功、過熱を異なるSEで知らせます。自機の被弾時は短く止まり、その後しばらく点滅して連続被弾を防ぎます。射撃・命中・撃破の演出中も移動と射撃を続けられます。

点滅する敵は攻撃の準備中です。発射前に倒すとその攻撃を止め、熱が4下がってCOOL +4を表示します。装甲機は通常弾2発、重い弾1発で撃破できます。敵弾は発射時に狙った方向へ進むので、発射を見て横へ避けましょう。画面下端のHULLは体力3、ENEMIESは残敵、HEATは発射熱です。体力0、または徐々に降下する編隊が突破すると失敗。3波目から三方向弾、4波目から2列目にも装甲が付き、攻撃間隔と予告時間も短くなります。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/play-02.png)
