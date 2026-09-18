# CHAIN SUIT

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/chain-suit.html)

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → CHAIN SUIT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chain-suit) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/chain_suit)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

5枚の手札を交換し、3回の採点で合計25点を目指します。役なし3点、1組のペア8点、複数のペア16点、同一スート5枚25点です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=chain-suit)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで札の上の矢印を動かし、Wでその札を交換します。交換は各手札につき2回まで。RETURNで採点して次の手札へ進みます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

交換する札は細くなって側面を見せ、新しい札として開きます。採点時は役を作る札の印が点滅し、役名・今回の点数・合計点を残して効果音と約2秒の間を挟んでから、次の手札へ進みます。演出が終わってから次のキーを押してください。

各札の枠内に1〜13の数字と、スペード・ハート・ダイヤ・クラブのスート記号を表示します。数字は最大2桁で、先頭の0は付けません。役に含まれる札の下には * 印が付き、盤面の下に現在の役名と点数が出ます。NO PAIRは役なし、ONE PAIRは1組、TWO PAIRSは2組、THREE / FOUR / FIVE OF A KINDは同じ数字3〜5枚、FULL HOUSEは3枚と2枚の組、FLUSHは同一スート5枚です。同じ数字の組が複数できる役はすべて16点で、同一スートが揃う場合は25点を優先します。下段のSCOREは合計点、GOALは目標点、REDRAWSは交換残数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/play-02.png)
