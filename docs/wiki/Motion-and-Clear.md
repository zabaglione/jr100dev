# 移動とクリア演出

[ホーム](Home) → 移動とクリア演出

連続移動の途中経過を表示する演出を6作品に追加しました。途中のマス、合成、敵の応答など、入力から結果までの流れを追えるようにしています。全51作品にクリア時のジングルと結果を見せる間を設けています。

## FROST STEPSの実画面

![滑走から3つ星クリアまで](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/slide-clear.gif)

[音付き動画](https://github.com/zabaglione/jr100dev/blob/main/games/frost_steps/images/slide-clear.mp4) · [プレイ](https://zabaglione.github.io/pyjr100emu/?game=frost-steps)

## 移動の途中経過

| 作品 | 演出 |
| --- | --- |
| [FROST STEPS](FROST-STEPS) | 氷上を1マスずつ滑り、途中でクリスタルやルーンを拾う様子を表示します。1回の方向入力は、滑走距離にかかわらず1手です。 |
| [GRAVITY WELL](GRAVITY-WELL) | 重力を変えると、球が1マスずつ転がって止まるまでを表示します。複数の球が移動する順序も追えます。 |
| [SEED MERGE](SEED-MERGE) | 種の移動、同じ種の合成、隙間を詰める移動、新しい種の出現を順に表示します。 |
| [PRISM TRACE](PRISM-TRACE) | 鏡を回した後、光が通るマスを順に表示します。反射して進む経路を追えます。 |
| [PEG GARDEN](PEG-GARDEN) | 選んだ駒が隣の駒を飛び越え、空いた穴に着地する様子を表示します。 |
| [QUIET ROUTE](QUIET-ROUTE) | プレイヤーが動いた盤面を一度表示してから、警備員が応答します。自分の行動と敵の行動を区別できます。 |

元から1マスずつ進む移動、時間を区切って進むアクション、カーソル選択、LOOP TENの意図したワープは、それぞれのテンポを保っています。追加した演出中の入力は捨て、次の行動が勝手に出ないようにしています。

## クリア後の余韻

最初の50作品は、完成した盤面と結果を残し、約1.6秒のジングルと余韻を挟んでから次の操作を受け付けます。曲は明るい結晶系、探索系、標準の3種類を作品に合わせて使います。押しっぱなしや演出中の入力では結果を飛ばしません。RELIC DIVEは容量に合わせた専用の約1.9秒のジングルを最終クリア時に鳴らします。通常プレイ中の効果音・BGMはありません。

## 検証と録画

すべて標準RAM 16KB内で、JR-100のCPUと音源を使って実行します。手数・盤面・評価、全ステージの入力リプレイ、途中フレーム、結果表示の保持、ジングルの音声出力と入力の抑止をエミュレーターで検査しています。掲載動画は所有するBASIC ROMから起動し、ゲームの状態を書き換えずに入力だけで録画しました。実機での表示・動作・音声は未確認です。

```sh
make games-test
.venv/bin/python games/frost_steps/capture_motion.py --rom /path/to/owned-rom.prg
```
