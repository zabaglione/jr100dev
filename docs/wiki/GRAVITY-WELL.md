# GRAVITY WELL

[ホーム](Home) → [パズル](Genre-Puzzle) → GRAVITY WELL

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gravity-well) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/gravity_well)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

部屋を傾けて2つの球を同時に転がし、両方の菱形ソケットを埋める40面のパズルです。序盤で壁や球による止まり方を覚え、後半では片方を先に止める手順や位置関係の組み替えに挑戦します。丸いルーンはどちらの球でも回収できます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/title.png)

## 画面の奥行き

金属の盤、丸い球の明暗、くぼんだ受け皿で高さの違いを出しました。球と任意ルーンは丸みと十字の印で区別できます。

## 操作と遊び方

WASDで部屋を傾けます。少なくとも1つの球が動いた傾き1回を1手と数えます。球は壁か他方の球で止まり、通過したルーンを回収します。両方がソケットに入った傾きの終了時にクリアします。球がまったく動かない入力は手数に含みません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

GRAVITYのSOCKETSは球が入っているソケット数です。下部のMOVは使用手数、PARは規定手数、RUNESは任意ルーンの回収数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/play-02.png)

## 手数と星評価

規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。

| 評価 | 条件 |
| --- | --- |
| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |
| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |
| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |

PARは、両方のルーンを回収してクリアできる最短手数を探索して設定しています。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。

![3つ星クリア](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/three-stars.png)

## 40面の構成と再挑戦

| 面 | 難度の段階 | PARの範囲 |
| --- | --- | ---: |
| 1〜8 | 入門 | 4〜6 |
| 9〜16 | 基本 | 7〜9 |
| 17〜24 | 応用 | 10〜13 |
| 25〜32 | 上級 | 14〜17 |
| 33〜40 | 最終課題 | 19〜23 |

Fで面選択を開き、WASDまたはパッドで選び、RETURNまたはボタンで開始します。全40面を最初から選択でき、選択した面のPARと各面の最高評価を確認できます。面選択のSPACEはタイトルへ戻ります。

クリア後はSPACEで同じ面に再挑戦、RETURNで次の面へ進みます。BESTは最高評価、NOWは今回の評価です。低い評価で再クリアしてもBESTは下がりません。ゲーム終了後も続ける場合は、次のパスワードを記録してください。

![40面の最高評価一覧](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/stage-select.png)

## パスワードで続きから

タイトルと面選択の下部に表示される **PW** を書き留めてください。選択中の面番号と、全40面の最高評価を復元できます。盤面の途中経過は保存せず、復元後にRETURNでその面の最初から再開します。

コードは空白を除いて **4〜24文字**。先頭の3つ星達成済みの面と末尾の未クリア面を省略するため、順番に3つ星を取って進める場合は通常5〜6文字です。数字は使わず、次の16種類の大文字だけを使います。

```text
ACDEFGHJKMNPQRTW
```

1. タイトルまたは面選択でXを押します。
2. コードを入力し、RETURNで復元します。表示上の区切り空白は入力しても省略しても構いません。
3. 修正はBackspace（実機ではマイナスキー）、取り消しはXです。

入力画面ではパッドの方向で文字を選び、ボタンで追加する方法も使えます。最後にLOADを選んでボタンを押すと復元します。DELは1文字削除、BACKは取り消しです。入力ミスや別作品のコードを検査し、エラー時は現在の記録を変更しません。

![パスワード入力](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/password-entry.png)

![再起動後の記録復元](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/password-restored.png)

## ビルドと検証

バージョン 1.3.0。開始番地 `$0300`、ゲーム本体と定数は 10,598 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/gravity_well
make -C games/gravity_well test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

盤面はビルド時に2マスを1バイトへ圧縮します。`levels.json` が編集用の面データ、`challenges.json` がクリア経路とルーン回収経路、`solutions.json` が全40面の3つ星リプレイです。`native/campaign_levels.py` で再生成でき、`native/campaign_checks.py` は全盤面の解探索、評価条件、再挑戦、面選択、最高評価の保持、手数カウンターの上限を検査します。回転・鏡映だけの地形の重複は除外しています。`native/password_checks.py` はパスワードの圧縮・展開、誤入力の検出、別作品のコード拒否と、再起動後のキー／パッド入力による記録復元を検証します。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py gravity_well --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
