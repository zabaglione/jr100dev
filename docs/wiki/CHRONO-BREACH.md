# CHRONO BREACH

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → CHRONO BREACH

**動けば、時間が動く。止まれば、弾も止まる。**

警備ドローンの射線を読み、接近攻撃と4マス射撃で突破する20面の戦術パズル。全敵を倒し、出口へ向かいます。動く時計と大きなタイトルロゴ、金属壁の戦場、次の発砲を示す計器、短い単音のタイトル曲と各種効果音を収録しています。

**[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chrono-breach)** · [ソース・ビルド手順](https://github.com/zabaglione/jr100dev/tree/main/games/chrono_breach)

同じブラウザーでBASIC ROMを事前登録していれば、プレイのクリックだけでゲームのタイトルまで起動します。タイトルではRETURNまたはパッドのボタンで開始します。通常の設定が32KBでも、このゲームは標準16KBで起動します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=chrono-breach)**

1ステージのクリアまでを収録。

## 操作

| 操作 | キーボード | 方向＋1ボタンパッド |
| --- | --- | --- |
| 上／下／左／右へ移動 | W / S / A / D | 各方向 |
| 戦術メニュー／決定 | RETURN | ボタン |
| 射撃 | F | メニューのFIRE |
| 待機 | X | メニューのWAIT |
| 戻る | SPACE | メニューのBACK |
| 照準 | メニュー中A / D | メニュー中左右 |
| BASICへ戻る | CTRL+C | キーボードを使用 |

方向は押すごとに1マス。メニューは上下で選び、ボタンで決定します。照準変更とメニュー操作では時間を消費しません。死亡後は決定ですぐ再挑戦できます。

やり直し／プレイ中のタイトル移動は実行前に確認します。NOが初期選択です。A/Dで選びRETURNで確定、SPACEで取り消します。

## 遊び方と画面

1操作ごとに敵弾が1マス進み、敵は3操作ごとに固定方向へ撃ちます。小さな輪郭の列が射線、大きな白いものが実際の弾です。敵のいるマスへ移動すると接近攻撃。自分の射撃は4マスまで届き、壁または最初の敵で止まります。

![射線と弾の回避](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/sector-02.png)

射線から外れて弾をやり過ごす場面。敵を倒しても、発射済みの弾は残ります。

| HUD | 意味 |
| --- | --- |
| GUARDS | 残り敵数 |
| ROUNDS | 残弾 |
| FIRE IN | 次の発砲までの操作数 |
| FACING | 照準方向 |
| ACTS / TARGET | 操作数とACE評価の目標 |

壁への移動や弾切れ時の射撃は時間を消費しません。弾のあるマスへ移動すると、弾が動く前に被弾します。敵同士の誤射も利用できます。

![複数の敵が待ち構える区画](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/sector-15.png)

全敵撃破後に出口`E`へ入るとクリア。TARGET以内ならACE、超えてもCLEARです。解禁済みの面はタイトルで左右を押して選べます。プレイ中の記録は電源断や再読込で消えます。

![全20面クリア](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/ending.png)
