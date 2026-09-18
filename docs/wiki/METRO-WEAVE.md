# METRO WEAVE

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → METRO WEAVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/metro_weave)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

分岐と信号を操作し、列車を同じ文字の駅へ届ける運行ゲームです。各シフトは8本。通常便は自動で出発し、RETURNで次の1本を急行として早く出せます。同時運行は最初が2本、後半は3本まで。行先の順番はプレイごとに変わり、次の3本を予告します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/demo-clear.png)

**[音付きプレイ動画を見る（約38秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=metro-weave)**

1ステージのクリアまでを収録。

## 操作と遊び方

W/Sでポイント1・2を選び、Dで進路、AでSTOP／GOを切り替えます。ポイント1はA駅への直進かポイント2への下り、ポイント2はB駅への直進かC駅への下りです。太い線路が現在の経路です。列車は到達した時点の設定に従い、設定は手で変えるまで保ちます。列車のそばの番号と行先、点灯した駅看板を見て運行してください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

3シフトで自動配車が速まり、同時運行数が2本から3本へ増えます。毎回変わる次の3本を読み、急行を手動増発できます。急行は得点が高い一方、信号待ち・荷下ろし待ちで遅延し、HPと連続成功を失います。車体は1マスずつ動き、自動で車間を保ちます。常設の操作説明はタイトル・ヘルプへ移し、本編は列車・進路・行先・待ち時間・得点を表示します。演出が終わってから次のキーを押してください。

通常便は2点、時間内の急行は4点。連続成功で得点が2倍、3倍になります。急行のWAIT欄は停車できる残りの猶予で、!00になった列車は遅延です。駅のBUSY中は荷下ろし待ちになり、後続列車も自動で間隔を空けて停まります。同じ駅へ急行を詰めると遅れやすいため、次の行先と混雑を見て通常便を待つか急行を出すか判断します。誤配や遅延はHPが1減り、連続成功も途切れます。HPが0になる前に8本を運行し、1・2・3シフトでそれぞれ24・30・36点を取るとクリア。44点でSILVER、60点でGOLDです。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/play-02.png)
