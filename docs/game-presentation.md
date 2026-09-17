# JR-100ゲームの画面と演出

## タイトルとキャラクター

50作品のタイトルは、それぞれの構図を保ち、ロゴの白い正面に網点の側面を加えた。ROMのセミグラフィックス16種で表せる部分はROM文字を使い、網点を含む部分だけPCGへ割り当てる。32文字に収めるために形を近似する処理は入れていない。RELIC DIVEは専用の石文字・門・輝きの構図を維持し、未使用PCGと画面データを圧縮した。

JR-100ではPB5を上げたPCGモードの上位文字コードを、反転ROM文字として同時使用できない。そのため、この画面ではROMの白黒図形とPCGを組み合わせ、疑似的な明暗を作る。

参考にしたのは、YAZIOH氏の[主線と面の描き分けの解説](https://note.com/yazioh/n/nfb3a8034aba2)である。紹介作品のキャラクターデータを転用せず、単色16×16ドットで輪郭、顔、装備、向きを読めるオリジナルの図案を作成した。MSXの色制約とJR-100の制約は区別している。

| 作品 | 動的に書き換えるキャラクター |
| --- | --- |
| IRON SCRIPT、MAGNET VAULT | ロボット |
| QUIET ROUTE | 探索者と巡回兵を別々の領域で管理 |
| FROST STEPS、GLYPH SHIFT、COMPASS ROSE、MIRROR RELIC | 探索者 |
| RIBBON SNAKE | 蛇の頭 |

1体は2×2文字、PCG上は32バイトだけを占有する。4方向の図案128バイトはプログラム側に置き、向きが変わったときだけ32バイトを転送する。同じ向きの再描画では転送しない。QUIET ROUTEの探索者と巡回兵は合計8文字を使い、それぞれ別の向きを表示できる。

同じPCG番号を共有する複数の敵に、異なる向きを同時表示することはできない。共有する敵群にはこの方法を一律には適用していない。被弾の点滅もPCG全体を書き換えず、対象位置のVRAMだけを一時的に変える。

## 開始、被弾、結果

- 開始時はSE、画面中央の`GAME START`、通常画面への復帰を挟む。移動・対戦系18作品では地形、目標、プレイヤー、敵などをPCGの役割ごとに4段階で出す。その他は短い全体表示を使う。RELIC DIVEには専用の開始音を加えた。
- アクションの被弾は、接触状態を描いてから対象位置を2回点滅させ、約0.3秒止める。装甲ブロックやドローン、ECHO PARRYの相手にも、残り体力がある間の命中表示を加えた。
- 落下、誤った防御、敵との接触などを結果画面に表示し、失敗ジングルの後に短い間を置く。成功時の既存ジングルも維持する。共通処理では失敗約1.4秒、成功約1.6秒が目安。
- 演出中も音源と入力を走査するが、通常のゲーム更新は呼ばない。押しっぱなしの開始キーや被弾中の入力で、終了画面を飛ばさない。新たに押し直すと次の操作を受け付ける。
- 開始と被弾の待ち時間はゲーム用カウンターへ加算しない。LOOP TENは開始演出を終えてから600刻み、約10秒の計時を始める。

CORNER CROWNは着手した石を見せ、挟まれた石を一枚ずつ回す。元の面から幅を2段階で狭め、薄い側面を挟み、反対の面を2段階で開く。前後の静止形を含め7段階で、白から黒、黒から白の順序も逆にする。回転用PCGは専用の4文字だけで、盤上のほかの石や文字は変わらない。接地影は盤に残している。

FIVE FORGEは自分と相手の着手をそれぞれ約0.3秒見せ、着手音を分ける。既存の合成、光路、ペグ移動の中間描画も維持する。

IRON SCRIPT、QUIET ROUTE、MAGNET VAULT、FROST STEPS、GLYPH SHIFT、COMPASS ROSE、MIRROR RELIC、GRAVITY WELLでは、16ドットのマス間に8ドットの中間位置を描く。磁力で引く金属塊とプレイヤー、重力で転がる球にも適用する。判定は元のマスの単位で行い、中間位置は描画にのみ使う。移動SEと短い待ち時間を挟む。

STAR LANCE、NIGHT SWARM、BRICK PULSE、ECHO PARRYの敵・ブロックには、発光、中心の破片、外側へ散る破片、消失の4段階を加えた。対象の2×2文字だけを変え、共有PCGを使う別の敵を巻き込まない。命中後に体力が残る場合は被弾点滅を使う。

## 容量と実装

コード・定数は`$0300–$2FFF`に収め、画面用RAMは`$3000–$32FF`、状態は既存の確保領域を使用する。静的なタイトル、HUD、説明画面はランレングス圧縮している。RELIC DIVEでは未使用のタイトル文字を除き、距離を確認できた内部ジャンプだけを同等の短い命令へ縮めた。標準RAM 16KBとPCG最大32文字の条件は変えていない。

主な実装は`games/common/title_styles.py`、`directional.py`、`disc_animation.py`、`pacing.asm`、`feedback.asm`、`games/native/facing.asm`、`impact.asm`、`mover.asm`、`vanish.asm`にある。ゲーム固有のタイミングと失敗理由は各作品の`rules.py`または`src/`で定義する。

## 検証

```sh
make games
make games-test PYTHON="$PWD/.venv/bin/python"
.venv/bin/python -m pytest tests
```

CPU試験では全作品のPCG・RAM配置、操作、リトライ、通しリプレイを検証する。`check_presentation.py`は4段階の表示、4方向の図案、別キャラクターのPCG保持、開始時間とLOOP TENの計時分離、対象だけの点滅・4段階の消滅、失敗理由、押しっぱなし入力の抑止を検査する。`check_motion.py`は9作品の実際の中間画面と最終盤面を検査し、石返しでは5種類のPCGを両方向に使うことと、ほかの28文字が変わらないことも確認する。

所有するBASIC ROMを指定すると、BASICからの起動とエミュレーターの実フレームバッファによる画面確認を行える。

```sh
.venv/bin/python games/capture_titles.py --rom /path/to/owned-rom.prg
.venv/bin/python games/tests/check_presentation.py \
  --rom /path/to/owned-rom.prg --capture games/build/visual-review
.venv/bin/python games/tests/check_motion.py \
  --rom /path/to/owned-rom.prg --capture games/build/visual-review
```

ROMデータは配布物に含めない。これらはエミュレーター上の検証であり、実機での表示、音量、操作感は未確認。
