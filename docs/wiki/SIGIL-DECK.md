# SIGIL DECK

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/sigil-deck.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/sigil-deck.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → SIGIL DECK

**紋章を集め、自分のデッキで虚空の王を封じる。**

手札4枚、エナジー3から始まる10戦のカードバトル。24種のカードから勝利報酬を選び、攻撃・防御・毒・回復を組み合わせます。通常敵6種とボス2種が登場します。JR-100・標準RAM 16KB用です。

![SIGIL DECK title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/title.png)

**[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sigil-deck)** · [ソースとビルド手順](https://github.com/zabaglione/jr100dev/tree/main/games/sigil_deck)

同じブラウザーにBASIC ROMを事前登録済みなら、クリックでタイトルまで起動します。音声は最初のキー入力または画面クリックで有効になります。

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=sigil-deck)**

最初の戦闘に勝利するまでを収録。

## 操作

| 操作 | キーボード | 方向＋1ボタンパッド |
| --- | --- | --- |
| カード／END TURN／報酬を選ぶ | A / D | 左／右 |
| 使用／決定 | RETURN | ボタン |
| END TURNへ選択を移す | SPACE | 左右でEND TURNを選ぶ |
| デッキを見る | W | 上 |
| デッキ表示から戻る | 任意のゲーム操作キー | 方向またはボタン |
| BASICへ戻る | CTRL+C | キーボードを使用 |

カードの上にある矢印が選択位置です。画面下に選択カードの効果を表示します。残りエナジーが足りないときや空の枠は使用できません。END TURNを選んで決定すると敵が行動します。

やり直し／プレイ中のタイトル移動は実行前に確認します。NOが初期選択です。A/Dで選びRETURNで確定、SPACEで取り消します。

## 戦闘とデッキ

- HPは最大60。各ターンにエナジーが3へ戻り、手札を4枚引きます。
- 使用したカードとターン終了時の残り手札は捨て札へ。山札が尽きると捨て札を山札に戻します。
- EXHAUSTのカードはその戦闘から除外され、次の戦闘で戻ります。効果を処理中のカードを自分自身のドローで引くことはありません。
- 敵の次の行動をNEXTに表示します。攻撃・防御・強攻撃の順に循環します。
- SHは防御値。まず防御で攻撃を受け、残りがHPに入ります。自分の防御は次の自分のターンで消えます。敵の防御も次の敵行動までです。
- POISONは敵行動の前に防御を無視してダメージを与え、1ずつ減ります。
- WEAKは敵の攻撃を3減らし、VULは自分の攻撃を50%増やします。端数は切り捨てます。
- STRは戦闘中の攻撃加算、ECHOは次の攻撃を2倍、THORNはそのターンの敵攻撃に対する反撃です。
- HUDのDRAWは山札、USEDは捨て札、Xは消滅札の枚数です。
- 勝利すると3枚から1枚を加えるか、RESTでHPを10回復します。どちらも追加でHPが4回復します。最後のボスを倒せばクリアです。

![The Oracle battle](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/battle-05.png)

5戦目のボス、THE ORACLE。敵の大きなシルエット、次の行動、自分の強化と手札を一画面で確認できます。

![Card reward](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/reward-05.png)

勝利報酬でデッキを伸ばすか、回復を選ぶかを判断します。取得したカードは以後の戦闘でも使えます。

## カード24種

| 表示名 | EN | 効果 |
| --- | ---: | --- |
| STRIKE | 1 | 攻撃6 |
| WARD | 1 | 防御5 |
| SPARK | 0 | 攻撃3 |
| MEND | 1 | 回復4 |
| FOCUS | 0 | エナジー+1 |
| VENOM | 1 | 毒+3 |
| CLEAVE | 2 | 攻撃12 |
| AEGIS | 2 | 防御12 |
| HASTE | 1 | 1枚引き、エナジー+1 |
| SIPHON | 2 | 攻撃6、回復3 |
| SCORCH | 1 | 攻撃4、毒+2 |
| THORN | 1 | 防御4、反撃3 |
| BASH | 2 | 攻撃9、その後VULを2ターン |
| ECHO | 1 | 次の攻撃を2倍 |
| FORTFY | 1 | 防御7、残った防御を次ターンへ1回保持 |
| RITUAL | 2 | 戦闘中の攻撃+2 |
| PURGE | 0 | WEAKを2ターン |
| INSIGT | 0 | 2枚引く。手札上限4 |
| SURGE | 0 | エナジー+2、EXHAUST |
| RESTOR | 2 | 回復9、EXHAUST |
| DOOM | 3 | 攻撃20 |
| BARRIR | 3 | 防御22 |
| PLAGUE | 2 | 毒+7 |
| FINISH | 1 | 攻撃4。敵HPが12以下なら攻撃+12 |

![Victory](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/victory.png)
