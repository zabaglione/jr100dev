# DICE RELIC

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → DICE RELIC

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=dice-relic) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/dice_relic)

同じブラウザーでBASIC ROMを事前に登録してください。

3個のダイスを振り、その出目を攻撃・防御・回復へ割り当てる、JR-100・標準RAM 16KB向けゲームです。8体の守護者と最後の王を倒し、勝利報酬でダイスの面を作り替えます。

![Title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/title.png)

## 紹介画像とプレイ動画

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=dice-relic)**

最初の戦闘に勝利するまでを収録。途中を省略せず、通常の速度で収録しています。画面を確認する間を入れた自動キー入力によるプレイです。

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/demo-start.png)

[![操作を進めた場面・クリックで動画](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/demo-play.png)](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=dice-relic)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/demo-clear.png)

## 操作

| 操作 | キーボード | 1ボタンパッド |
| --- | --- | --- |
| ダイスを選択 | A/D | 左右 |
| 割当先を選択 | W/S | 上下 |
| 使用／決定 | RETURN | ボタン |
| 工房で面を選択 | W/S | 上下 |
| 工房のサービスを選択 | A/D | 左右 |
| BASICへ戻る | CTRL+C | キーボードを使用 |

ATTACKは出目の値だけ攻撃、GUARDは同じ値の防御、HEALは同じ値のHP回復です。各ダイスは1ターンに1回使え、使用済みには×が付きます。REROLLは未使用のダイスを1ターンに1回だけ振り直します。

3個すべてを使うと敵が攻撃します。防御で軽減した残りがHPへ入り、防御は消えます。敵は4ターンごとに攻撃が2増えます。NEXTには今回の攻撃値を表示します。HP上限は42。敵を倒せばそのターンの反撃を受けません。

![First battle](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/battle-01.png)

勝利でHPが2回復し、金貨を3枚得ます。工房では、左右でダイス、上下で6面のどれを作り替えるかを選び、ボタンでサービスメニューを開きます。

- FORGE：金貨3枚で選んだ面の値を2増加。上限9。
- HEAL：金貨2枚でHPを6回復。満タンなら購入しません。
- NEXT：次の戦闘へ。
- BACK：面の選択へ戻る。

作り替えた面は以後の戦闘でも使われます。工房の表に全18面、下の大きなダイスに選択中の面の値を表示します。

![Workshop](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/workshop.png)
![The First King](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/battle-09.png)
