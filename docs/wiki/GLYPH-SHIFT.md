# GLYPH SHIFT

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/glyph-shift.html)

[ホーム](Home) → [パズル](Genre-Puzzle) → GLYPH SHIFT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=glyph-shift) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/glyph_shift)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

「箱が壁」「敵が壁」という通行ルールを切り替え、菱形の出口を目指す40面のパズルです。後半はルールの切替位置と分岐の巡回順を組み合わせて考えます。丸いルーンを回収する寄り道はクリアに必須ではありません。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=glyph-shift)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで移動し、RETURNで通行ルールを切り替えます。移動できた1マスとルール切替をそれぞれ1手と数えます。通れないマスへの入力は手数に含みません。出口に入るとすぐクリアするため、3つ星を狙う場合は先に2つのルーンを回収します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

探索者が進行方向を向き、マスの中間を通って移動します。移動音とともに一手の結果を確認できます。演出が終わってから次のキーを押してください。

RULE TABLEの矢印は現在有効な壁ルール、REWRITESは切替回数です。下部のMOVは移動と切替を合計した使用手数、PARは規定手数、RUNESは任意ルーンの回収数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/play-02.png)

## 手数と星評価

規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。

| 評価 | 条件 |
| --- | --- |
| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |
| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |
| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |

PARは、両方のルーンを回収してクリアできる最短手数です。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。

![3つ星クリア](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/three-stars.png)

## 40面の構成と再挑戦

| 面 | 難度の段階 | PARの範囲 |
| --- | --- | ---: |
| 1〜8 | 入門 | 8〜10 |
| 9〜16 | 基本 | 11〜16 |
| 17〜24 | 応用 | 17〜22 |
| 25〜32 | 上級 | 23〜27 |
| 33〜40 | 最終課題 | 31〜39 |

Fで面選択を開き、WASDまたはパッドで選び、RETURNまたはボタンで開始します。全40面を最初から選択でき、選択した面のPARと各面の最高評価を確認できます。面選択のSPACEはタイトルへ戻ります。

クリア後はSPACEで同じ面に再挑戦、RETURNで次の面へ進みます。BESTは最高評価、NOWは今回の評価です。低い評価で再クリアしてもBESTは下がりません。ゲーム終了後も続ける場合は、次のパスワードを記録してください。

![40面の最高評価一覧](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/stage-select.png)

## パスワードで続きから

タイトルと面選択の下部に表示される **PW** を書き留めてください。選択中の面番号と、全40面の最高評価を復元できます。盤面の途中経過は保存せず、復元後にRETURNでその面の最初から再開します。

コードは空白を除いて **4〜24文字**。順番に3つ星を取って進める場合は通常5〜6文字です。数字は使わず、次の16種類の大文字だけを使います。

```text
ACDEFGHJKMNPQRTW
```

1. タイトルまたは面選択でXを押します。
2. コードを入力し、RETURNで復元します。表示上の区切り空白は入力しても省略しても構いません。
3. 修正はBackspace（実機ではマイナスキー）、取り消しはXです。

入力画面ではパッドの方向で文字を選び、ボタンで追加する方法も使えます。最後にLOADを選んでボタンを押すと復元します。DELは1文字削除、BACKは取り消しです。入力ミスや別作品のコードを検査し、エラー時は現在の記録を変更しません。

![パスワード入力](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/password-entry.png)

![再起動後の記録復元](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/password-restored.png)
