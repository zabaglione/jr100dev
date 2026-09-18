# NIGHT SWARM

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/night-swarm.html)

[ホーム](Home) → [アクション](Genre-Action) → NIGHT SWARM

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=night-swarm) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/night_swarm)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

迫る群れを8方向へかわし、近距離の自動射撃と範囲パルスで生き延びる全6面。目標は12体から22体へ増え、後半は出現間隔も短くなります。装甲敵には2回の命中が必要です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/demo-clear.png)

**[音付きプレイ動画を見る（約54秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=night-swarm)**

1ステージのクリアまでを収録。

## 操作と遊び方

QWE／AD／ZXCで8方向移動、RETURNでパルス。パルスは周囲3マスまで届き、再使用には8カウント待ちます。丸い出現口が次の敵の入口です。敵を4体倒すごとに補給が落ち、踏むと体力が1回復し、パルスもすぐ使えます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

次の出現口を二重の輪で示し、自動射撃の弾、敵の中間移動、広がるパルスを表示します。装甲への命中は点滅、撃破は光から破片へ変わり、補給の回収音と被弾音を区別します。演出が終わってから次のキーを押してください。

HULLは残り体力、DOWNは撃破数と目標、PULSEは再使用までの残り、SALVAGEは回収した補給数です。体力は最大4。安全な距離を保つか、補給へ踏み込んで攻撃を続けるかを選びます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/play-02.png)
