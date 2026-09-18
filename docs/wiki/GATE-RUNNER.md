# GATE RUNNER

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/gate-runner.html)

[ホーム](Home) → [アクション](Genre-Action) → GATE RUNNER

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gate-runner) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/gate_runner)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

奥から迫る障害物を越える、6コースのランニングゲームです。最初のコースは9組、以降は12組の障害物に挑みます。横位置を1文字ずつ細かく調整して走ります。壁は横へ避け、穴は跳び越え、低い梁は地上を通ります。各コースには道幅いっぱいの穴が3か所あり、ジャンプを使わないと突破できません。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/demo-clear.png)

**[音付きプレイ動画を見る（約37秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=gate-runner)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで左右へ1文字ずつ移動します。押し続けると連続して走り、空中でも左右へ動けます。WまたはRETURNでジャンプし、着地してから次のジャンプができます。

障害物は奥では小さく、手前へ来るほど大きくなります。次の障害も遠景に見えるため、今の障害を越えた後の横移動を考えておきます。壁はジャンプしても越えられません。低い梁では地上を通り、全幅の穴では踏み切るタイミングを合わせてください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

3車線を廃止し、横27段階を1文字ずつ移動する6コースへ作り直しました。タイトルと同じセミグラフィックスの遠景に、拡大して迫る壁・穴・低い梁を描きます。各コース3か所の全幅の穴はジャンプ必須です。危険な位置の結晶を集めると評価が上がり、走行・跳躍・被弾に動きとSEがあります。演出が終わってから次のキーを押してください。

HULLは残りの耐久力、GATESは越えた障害の数、CRYSTALSは回収した結晶の数です。3回ぶつかると失敗し、壁・穴・低い梁のどれで失敗したか表示します。

結晶は狭い通路や穴の上にも出現します。安全な経路で完走するか、危険な位置へ寄って結晶を取るかを選べます。最初のコースは5個でSILVER、7個でGOLD。以降は6個でSILVER、10個でGOLDです。コースが進むと障害の順番と左右の配置が変わり、3〜4コース、5〜6コースでは接近速度も上がります。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/play-02.png)
