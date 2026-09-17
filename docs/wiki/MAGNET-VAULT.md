# MAGNET VAULT

[ホーム](Home) → [パズル](Genre-Puzzle) → MAGNET VAULT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=magnet-vault) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/magnet_vault)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

箱を押さず、磁力で手前に引いて2つの菱形ソケットに収めるパズルです。40面で箱・ソケット・開始位置を変え、後半には狭い通路や箱同士の移動順を考える部屋を用意しました。丸いルーンは箱を運ぶ途中に自分が歩いて回収します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/title.png)

## 紹介画像とプレイ動画

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=magnet-vault)**

1ステージのクリアまでを収録。途中を省略せず、通常の速度で収録しています。画面を確認する間を入れた自動キー入力によるプレイです。

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/demo-start.png)

[![操作を進めた場面・クリックで動画](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/demo-play.png)](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=magnet-vault)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/demo-clear.png)

## 操作と遊び方

WASDで歩行と向きを変え、RETURNで正面の箱を1マス引きます。引くと自分は1マス後退します。歩行・向きの変更・成功した引き寄せをそれぞれ1手と数えます。壁や箱に向いてその場で向きだけを変える操作も1手です。向きも位置も変わらない入力、失敗した引き寄せは数えません。箱ではルーンを回収できません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

ロボットは進行方向を向いて動きます。歩行と金属塊を引く動きには途中の位置と移動音があり、どの塊を動かしたか確認できます。演出が終わってから次のキーを押してください。

MAGNETのPULLSは成功した引き寄せ回数。FACINGは現在の向きN/S/W/Eです。下部のMOVは使用手数、PARは規定手数、RUNESは任意ルーンの回収数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/play-02.png)

## 手数と星評価

規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。

| 評価 | 条件 |
| --- | --- |
| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |
| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |
| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |

PARは、両方のルーンを回収してクリアできる最短手数です。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。

![3つ星クリア](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/three-stars.png)

## 40面の構成と再挑戦

| 面 | 難度の段階 | PARの範囲 |
| --- | --- | ---: |
| 1〜8 | 入門 | 10〜12 |
| 9〜16 | 基本 | 13〜19 |
| 17〜24 | 応用 | 21〜25 |
| 25〜32 | 上級 | 29〜36 |
| 33〜40 | 最終課題 | 39〜52 |

Fで面選択を開き、WASDまたはパッドで選び、RETURNまたはボタンで開始します。全40面を最初から選択でき、選択した面のPARと各面の最高評価を確認できます。面選択のSPACEはタイトルへ戻ります。

クリア後はSPACEで同じ面に再挑戦、RETURNで次の面へ進みます。BESTは最高評価、NOWは今回の評価です。低い評価で再クリアしてもBESTは下がりません。ゲーム終了後も続ける場合は、次のパスワードを記録してください。

![40面の最高評価一覧](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/stage-select.png)

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

![パスワード入力](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/password-entry.png)

![再起動後の記録復元](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/password-restored.png)
