# RELIC DIVE

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → RELIC DIVE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=relic-dive) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/relic_dive) · [詳しい説明書・敵と品物の図鑑](https://github.com/zabaglione/jr100dev/blob/main/games/relic_dive/README.md)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトル画面まで自動起動します。

標準RAM 16KBのJR-100向けローグライクです。毎回変わる64×32マスの迷宮で、食料、装備、正体不明の薬や巻物を使いながら階段を降り、最深部の遺物を探します。隠し通路、ダメージ罠、毒罠、15種類の敵が登場します。行動するまでターンは進まず、メニューも落ち着いて操作できます。

![タイトル・難易度選択](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/title.png)

石碑風の大型ロゴと、迷宮の奥に浮かぶ遺物を描いた専用タイトル画面です。周囲の光が明滅します。文字列の圧縮で900バイトを節約し、画面を追加した後もコード領域に149バイトの余裕を残しています。

## 画面の奥行き

8×8ドットの石壁に明るい上面と斜めの肩、暗い側面を付けました。視界・品物・敵の記号と広い迷宮の表示範囲を保ち、追加RAMは使っていません。専用タイトルの奥行き表現はそのまま活かしています。

## ゲーム専用フォント

今回はフォント変更を保留しました。タイトルはPCG全32枠、ゲーム中は31枠を使用し、コード・定数の空きも149バイトです。既存のロゴ・地形・アイテムの判別を優先しています。

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

![冒険開始・周辺の品物](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/play-01.png)

階段の上でメニューを開くとDESCENDが現れます。SEARCHは足元と周囲8マスの隠し通路・罠を調べます。INSPECTはカーソルで周辺を確認する操作です。SUSPENDはRAM内だけの中断で、電源を切ったりエミュレーターをリセットしたりすると失われます。

![探索が進んだ迷宮](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/play-02.png)

![持ち物・装備選択](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/inventory.png)

## ビルドと検証

バージョン：1.2.0。開始番地は `$0300`、ゲーム本体と定数は11,371 bytes、PCGはタイトルで32文字、ゲーム中は31文字を切り替えて使います。画面バッファー・地形・状態・復帰用保存領域・512 bytesのスタックを含めて標準RAM 16KB内に収めています。

```sh
make -C games/relic_dive
make -C games/relic_dive test
```

出力は `games/relic_dive/build/relic-dive.prg` です。手動ロード時はBASICから `A=USR($0300)` を実行します。

地形1,000種の接続・配置、8方向入力、品物・戦闘・視界・罠、描画と命令をC++エミュレーターで検査しています。保存入力だけを再生し、EASYの5階・NORMALの10階・HARDの20階で遺物取得を確認しました。

掲載画像は所有するBASIC ROMからPRGを自動起動し、キーボード入力で取得したエミュレーターの実フレームです。Web配布用WASMでも標準16KBでのタイトル表示とゲーム開始を確認しています。実機でのロード・表示・操作は未確認です。現在の版は効果音・BGMがありません。

```sh
.venv/bin/python games/relic_dive/capture.py --rom /path/to/owned-rom.prg
```

画像取得には `games/requirements-qa.txt` の追加依存が必要です。BASIC ROMは配布物に含めません。

[JR-800版RELIC DIVE](https://github.com/zabaglione/jr800-web-emulator/tree/main/sdk/examples/lcd/07-relic-dive)を基にJR-100用のアセンブリで実装しています。ソース・画像・文章は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/relic_dive/LICENSE)です。
