# FROST STEPS

[ホーム](Home) → [パズル](Genre-Puzzle) → FROST STEPS

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=frost-steps) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/frost_steps)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

壁にぶつかるまで滑る氷の洞窟パズル。必須の菱形クリスタルをすべて回収するとクリアです。40面を5段階に分け、序盤は短い滑走、後半は回収順序と壁で止まる位置を考える構成にしています。丸いルーンは任意の回収物です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/title.png)

## 操作と遊び方

WASDで滑走方向を選びます。実際に滑れた1回を1手と数え、途中で通過したクリスタルとルーンを回収します。壁に向かって動かなかった入力は手数に含みません。最後の必須クリスタルを取った滑走が終わるとクリアになるため、ルーンを狙うときは回収順に注意してください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

ICE COMPASSのCRYSTALSは残っている必須クリスタル数。下部のMOVは使用手数、PARは規定手数、RUNESは任意ルーンの回収数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/play-02.png)

## 手数と星評価

規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。

| 評価 | 条件 |
| --- | --- |
| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |
| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |
| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |

PARは、両方のルーンを回収してクリアできる最短手数を探索して設定しています。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。

![3つ星クリア](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/three-stars.png)

## 40面の構成と再挑戦

| 面 | 難度の段階 | PARの範囲 |
| --- | --- | ---: |
| 1〜8 | 入門 | 3〜6 |
| 9〜16 | 基本 | 7〜10 |
| 17〜24 | 応用 | 11〜13 |
| 25〜32 | 上級 | 15〜18 |
| 33〜40 | 最終課題 | 20〜23 |

Fで面選択を開き、WASDまたはパッドで選び、RETURNまたはボタンで開始します。全40面を最初から選択でき、選択した面のPARと各面の最高評価を確認できます。面選択のSPACEはタイトルへ戻ります。

クリア後はSPACEで同じ面に再挑戦、RETURNで次の面へ進みます。BESTは最高評価、NOWは今回の評価です。低い評価で再クリアしてもBESTは下がりません。評価はゲーム実行中のRAMだけに保存し、BASICへ終了・エミュレーターのリセット・PRGの再読み込みで消えます。

![40面の最高評価一覧](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/stage-select.png)

## ビルドと検証

バージョン 1.1.0。開始番地 `$0300`、ゲーム本体と定数は 8,759 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/frost_steps
make -C games/frost_steps test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

盤面はビルド時に2マスを1バイトへ圧縮します。`levels.json` が編集用の面データ、`challenges.json` がクリア経路とルーン回収経路、`solutions.json` が全40面の3つ星リプレイです。`native/campaign_levels.py` で再生成でき、`native/campaign_checks.py` は全盤面の解探索、評価条件、再挑戦、面選択、最高評価の保持、手数カウンターの上限を検査します。回転・鏡映だけの地形の重複は除外しています。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py frost_steps --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
