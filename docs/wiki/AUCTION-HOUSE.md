# AUCTION HOUSE

[ホーム](Home) → [経営・サバイバル](Genre-Management) → AUCTION HOUSE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=auction-house) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/auction_house)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

鑑定額と相手の入札を読み、6品の競りで持ち金40を増やす全3市場です。目標は58、60、61。品物の価値は開始ごとに変わります。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/demo-clear.png)

**[音付きプレイ動画を見る（約36秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=auction-house)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/DでBID +2・BID +6・INSPECT・PASSを選び、RETURNで決定します。小刻みな入札に対し、大きな入札は相手が降りる基準を4下げます。INSPECTは持ち金1で正確な価値を知り、PASSはその品を見送ります。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

競売卓と計器の区切りを加え、自分の入札、相手の応答、鑑定結果、3段階の落札ハンマーを順に表示します。売買後の収支を残してから次の品へ進みます。演出が終わってから次のキーを押してください。

APPRAISALは価値の見積もり幅、BIDは現在額、CASHは持ち金、WONは落札数です。落札すると代金を払い、品物の価値を受け取ります。最低見積もりでも利益が出るか、鑑定代を払う価値があるかを考えます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/play-02.png)
