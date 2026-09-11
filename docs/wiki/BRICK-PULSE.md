# BRICK PULSE

[ホーム](Home) → [アクション](Genre-Action) → BRICK PULSE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=brick-pulse) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/brick_pulse)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

12面のブロック崩しです。各面のブロックとドローンをすべて壊すとクリア。各面は3球で開始し、3球を落とすと同じ面から再挑戦できます。序盤は隙間の多い配置、後半は2〜3回の打撃が必要な装甲ブロックが増えます。3面目からドローン、6面目からその落下爆弾が登場します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/title.png)

## 操作と遊び方

A/Dまたはパッドの左右を押し続けると連続移動し、短押しでは2文字分ずつ動き、離すと止まります。中央で受けると急な角度、端で受けると浅い角度になります。ブロックを3個壊すごとにW・S・Gのいずれかが落下します。Wは一定時間パドル拡大、Sは一定時間ボール減速、Gは落球または爆弾を1回防ぎます。ドローン撃破でもGが落ちます。同時に出るアイテムは1個です。爆弾を受けるとパドルが一定時間短くなります。Wを取ると解除できます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。プレイ中のSPACEは無効です。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

下部のBALLは残球、BRICKは残ブロック数、DRONEは敵の残耐久です。WIDE・SLOW・GUARDは有効な効果、JAMは爆弾による縮小を示します。ブロックの模様は残る耐久を表します。クリア後のRETURNは次の面、失敗後のRETURNは確認付きの再挑戦です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/play-02.png)

![落下アイテム](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/items.png)

![後半のドローンと装甲ブロック](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/drone.png)

![やり直し確認](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/reset.png)
