# RELIC DIVE

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → RELIC DIVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=relic-dive) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/relic_dive) · [詳しい説明書・敵と品物の図鑑](https://github.com/zabaglione/jr100dev/blob/main/games/relic_dive/README.md)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトル画面まで自動起動します。

標準RAM 16KBのJR-100向けローグライクです。毎回変わる64×32マスの迷宮で、食料、装備、正体不明の薬や巻物を使いながら階段を降り、最深部の遺物を探します。隠し通路、ダメージ罠、毒罠、15種類の敵が登場します。行動するまでターンは進まず、メニューも落ち着いて操作できます。

![タイトル・難易度選択](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=relic-dive)**

最初の階を踏破し、2階へ進むまでを収録。

## 操作と遊び方

```text
Q W E
A S D
Z X C
```

| 操作 | キーボード | 1ボタンパッド |
| --- | --- | --- |
| 8方向移動・隣の敵を攻撃 | QWE／AD／ZXC | 上下左右と斜め |
| 1ターン待機 | S | メニューのWAIT |
| メニュー・決定・開始 | RETURN | ボタン |
| 難易度・メニュー選択 | W／X | 上／下 |
| 一つ前へ戻る | SPACE | BACKを選択して決定 |
| 説明を読む | メニューのHELP | 同左 |
| BASICへ戻る | CTRL+C | キーボードを使用 |

下方向はX、中央のSは待機です。隣に敵がいる方向へ進むと攻撃します。壁の角を斜めにすり抜けることはできません。安全な探索済み直線通路では上下左右の長押しで歩けますが、敵・分岐・未探索地点・品物・階段などの前で止まります。

| 難易度 | 遺物のある階 | 初期HP | 初期食料 |
| --- | ---: | ---: | ---: |
| EASY | 5階 | 24 | 240 |
| NORMAL | 10階 | 20 | 200 |
| HARD | 20階 | 16 | 160 |

まずはEASYで始め、品物の上へ移動して拾います。持ち物は6枠。INVENTORYから食料・薬・巻物を使い、武器・防具を装備します。食料は拾うだけでは回復せず、使う必要があります。食料のない階もあるため、残量を見ながら進んでください。薬と巻物は冒険ごとに外見と効果の対応が変わり、使うと正体が判明します。

画面上部のHUDは、階、現在／最大HP、食料（FD）、レベル（LV）、攻撃力（ATK）、防御力（DEF）、所持金を表示します。下部には直前の出来事と操作案内が出ます。歩いて確認した地形は記憶しますが、敵は現在見えている範囲だけ表示します。

冒険の開始と被弾を効果音で知らせます。HPが減ったときは短い間が入り、直前の出来事を確認できます。成功・失敗の結果にはジングルを付けています。音と表示が終わってからキーを押し直してください。

![冒険開始・周辺の品物](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/play-01.png)

階段の上でメニューを開くとDESCENDが現れます。SEARCHは足元と周囲8マスの隠し通路・罠を調べます。INSPECTはカーソルで周辺を確認する操作です。SUSPENDで一時中断できます。電源を切ったりエミュレーターをリセットしたりすると、中断した記録は失われます。

![探索が進んだ迷宮](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/play-02.png)

![持ち物・装備選択](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/inventory.png)
