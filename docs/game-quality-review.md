# 公開ゲームの品質改善基準

初回の共通改修では、これまでの指摘を8項目に整理し、個別改修済みの16作品に続いて、残る35作品を改善しました。全51作品をビルド・検証しています。

2026年9月18日には、共通改修後に個別の発展が残っていた25作品をさらに改修しました。既存の6作品も再点検しています。[25作品の変更点と検証](https://github.com/zabaglione/jr100dev/wiki/Second-Review)を参照してください。

## 指摘の要点

1. **読む前に判別できる画面**：ゴール・収集対象・任意アイテム、選択枠、カードのスートと数字、成立した役、攻撃・防御・回復の割当を近接表示する。数値の桁数は用途に合わせる。
2. **本編の絵柄**：タイトルだけを豪華にせず、セミグラフィックス・反転・陰影・厚みで作品固有の盤面を作る。装飾は操作位置や意味を隠さない。
3. **途中の形と位置**：反転には表・側面・裏、移動には中間位置、合体には接近と結合、撃破には複数の消滅段階を用意する。
4. **動作と音と間**：開始時の順次登場、被弾・失敗原因の提示と短い停止、成功・失敗のジングルを使う。耐久力のある敵は命中と撃破を区別する。経営・推理でも一手の変化を順番に見せる。
5. **判断のある内容**：規則的な配札や作業だけの短い課題を見直す。予告・資源・配置・連鎖・相手の応答によって選択に意味を持たせる。単なる待ち時間や面数増加を難度と扱わない。
6. **操作の一貫性**：明示的に切り替えるモードは操作後も維持する。誤操作や実行不能な行動は原因を示す。演出中の入力で結果を飛ばさない。
7. **紹介と公開**：紹介画像は最低3枚、その後に動画を置く。基本は約30秒で最初の目標達成まで。長い課題を省略するより必要な長さを優先し、PEG GARDEN・SEED MERGEはフル収録を維持する。遊び方へ収録手段の説明を加えない。Wikiと公開PRG・画像・動画を一致させる。

8. **本編への集中**：常設の操作説明・攻略説明はタイトルやヘルプにまとめる。プレイ中は盤面、現在の選択、体力・得点・予告などの判断材料と、その場で起きた結果を表示する。

## 機種と確認の境界

標準16KB、32×24文字、PCG32文字、MB8861H命令を守る。2×2文字の単独キャラクターは向きに合わせて4文字だけを書き換える。同時に別の向きで表示する個体や敵全体の点滅ではPCG共有の副作用を避け、必要な画面位置だけを変える。

ビルド・ルール検証、所有ROMを使うエミュレーターの実画面と音声、公開ブラウザーの起動を分けて記録する。実機の動作・音声は未確認。

## 今回の35作品の変更

| 作品 | 改善内容 |
| --- | --- |
| [CHRONO BREACH](https://github.com/zabaglione/jr100dev/wiki/CHRONO-BREACH) | 移動の中間位置と発射後の線を表示し、倒した敵は発光・破片・細かな粒の順に消えます。 |
| [SIGIL DECK](https://github.com/zabaglione/jr100dev/wiki/SIGIL-DECK) | 使用した札の発光、攻撃によるHP変化、防御値の増加、回復、敵の応答を順に表示します。補充される手札も一枚ずつ確認できます。 |
| [ABYSS SIGNAL](https://github.com/zabaglione/jr100dev/wiki/ABYSS-SIGNAL) | 潜水艇はマスの中間を通って移動します。ソナーを使うと、観測範囲を横切る走査線と音で探査を示します。 |
| [TRACE BLADE](https://github.com/zabaglione/jr100dev/wiki/TRACE-BLADE) | 剣士が計画した経路を中間位置を通って進み、標的を一体ずつ、光・破片・粒に変えて斬ります。 |
| [LOOP TEN](https://github.com/zabaglione/jr100dev/wiki/LOOP-TEN) | 移動の中間位置、封印の反応、危険地形への接触、手動巻き戻しに途中の絵と音があります。移動演出の時間も10秒の制限に含まれます。 |
| [IRON SCRIPT](https://github.com/zabaglione/jr100dev/wiki/IRON-SCRIPT) | 射撃・スイッチ操作・直前2命令の繰り返しを追加し、通常／装甲敵、開閉扉、周期レーザーを組み合わせた24面へ刷新しました。ROM矢印、扉の開閉、命中点滅、4段階の撃破、原因を残す再編集に対応します。 |
| [QUIET ROUTE](https://github.com/zabaglione/jr100dev/wiki/QUIET-ROUTE) | 探索者と警備員が向きを変えて中間位置を通ります。静音・通常歩行と音の届く距離を明記し、機密取得と出口の解放を光と音で示します。 |
| [CIRCUIT WORKS](https://github.com/zabaglione/jr100dev/wiki/CIRCUIT-WORKS) | 3入力・8行の真理値表を使う22問です。各入力の信号が3段のゲートを通る過程を順番に見せ、正解した行数を表示します。 |
| [HEARTH ZERO](https://github.com/zabaglione/jr100dev/wiki/HEARTH-ZERO) | 3種類の寒波を、それぞれ12日間生き延びます。今夜と続く2夜の寒さを予告し、作業、食事、暖かさの消費を音と間を挟んで順に見せます。 |
| [NIGHT SWARM](https://github.com/zabaglione/jr100dev/wiki/NIGHT-SWARM) | 主人公と敵の中間移動、広がるパルス、再使用可能の表示を追加しました。装甲のある敵は2回の命中が必要で、被弾点滅と撃破時の破片を区別します。 |
| [LUMEN CROSS](https://github.com/zabaglione/jr100dev/wiki/LUMEN-CROSS) | 18種類の盤面で、操作した中心から周囲へ点灯・消灯が波及します。一灯ずつの反応を音と光で確認できます。 |
| [STONE BALANCE](https://github.com/zabaglione/jr100dev/wiki/STONE-BALANCE) | 自分と相手が取った石を、一つずつ盤面から移動させます。相手の応答を確認する間があり、最後の石を取った側が勝ちます。 |
| [MEMORY MOSAIC](https://github.com/zabaglione/jr100dev/wiki/MEMORY-MOSAIC) | 配札を開始時にシャッフルします。札は幅が細くなり側面を経て表裏が入れ替わります。一致は光と音、不一致は2枚を覚える間で示します。 |
| [TWENTY ONE](https://github.com/zabaglione/jr100dev/wiki/TWENTY-ONE) | 個々のカードと合計を表示します。配札と追加カードが山から移動し、ディーラーも一枚ずつ引きます。勝ち・バスト・負け・引き分けと収支を残してから次の手へ進みます。 |
| [ORBIT DODGE](https://github.com/zabaglione/jr100dev/wiki/ORBIT-DODGE) | 機体が軌道上の中間位置を通り、予告地点へ攻撃の線が伸びます。6回の回避後から2地点への攻撃が加わります。 |
| [GATE RUNNER](https://github.com/zabaglione/jr100dev/wiki/GATE-RUNNER) | 3車線を廃止し、横27段階を1文字ずつ移動する6コースへ作り直しました。タイトルと同じセミグラフィックスの遠景に、拡大して迫る壁・穴・低い梁を描きます。各コース3か所の全幅の穴はジャンプ必須です。危険な位置の結晶を集めると評価が上がり、走行・跳躍・被弾に動きとSEがあります。 |
| [STAR LANCE](https://github.com/zabaglione/jr100dev/wiki/STAR-LANCE) | 長押しで連続移動し、射撃と同時に操作できます。敵の攻撃予告を撃破で止めると冷却し、過熱すると一時的に撃てなくなります。命中と撃破の途中も戦闘が進みます。 |
| [RIBBON SNAKE](https://github.com/zabaglione/jr100dev/wiki/RIBBON-SNAKE) | 頭だけでなく胴体もマスの中間を通ります。食べると光と音が出て体が伸び、画面端と自分の体への衝突をそれぞれ説明します。 |
| [LUNAR TOUCHDOWN](https://github.com/zabaglione/jr100dev/wiki/LUNAR-TOUCHDOWN) | 降下の中間位置と噴射炎を描きます。着陸台の上へ速度0〜2で降りると、機体の停止を確認する間と着陸音を挟んでクリアします。 |
| [ECHO PARRY](https://github.com/zabaglione/jr100dev/wiki/ECHO-PARRY) | 敵の攻撃、盾での受け止め、反撃の飛翔、命中を順に描きます。攻撃の高さは単純な交互から8手のパターンへ変えました。 |
| [PENDULUM PORT](https://github.com/zabaglione/jr100dev/wiki/PENDULUM-PORT) | 振り子を離れた主人公が弧を描いて足場へ着地し、着地の光と音を確認してから次の足場へ進みます。 |
| [RUIN LEXICON](https://github.com/zabaglione/jr100dev/wiki/RUIN-LEXICON) | 1〜4を一度ずつ使う20問です。隣り合う文字の合計と不等式を手掛かりに解読し、確定時は4文字を順に照合します。 |
| [SHADOW ARCHIVE](https://github.com/zabaglione/jr100dev/wiki/SHADOW-ARCHIVE) | 帽子・眼鏡・ネクタイが異なる6人から、3つの資料で容疑者を絞る12事件です。資料を開く途中を描き、証拠と合わない人物にはXを付けます。 |
| [COMPASS ROSE](https://github.com/zabaglione/jr100dev/wiki/COMPASS-ROSE) | 岩を避けて方角を読みながら進みます。未探索の地面と岩を描き分け、掘る途中の動作と、発見の光・音を加えました。 |
| [MIRROR RELIC](https://github.com/zabaglione/jr100dev/wiki/MIRROR-RELIC) | 6つの遺物配置を用意しました。鏡で移る位置まで主人公が移動する過程を描き、回収と出口の解放を光とメッセージで示します。 |
| [ORCHARD DAYS](https://github.com/zabaglione/jr100dev/wiki/ORCHARD-DAYS) | 種・芽・木・果実を別の絵で示します。種まき、水やり、成長、収穫物の移動を順に描き、次の雨までの日数を表示します。 |
| [TIDAL NETS](https://github.com/zabaglione/jr100dev/wiki/TIDAL-NETS) | 浅い魚群と2倍流される深い魚群を、隣接2列を覆う網で狙います。9回で30匹が目標です。投入、魚の移動、網の引き揚げ、加点を順に描きます。 |
| [POTION PATH](https://github.com/zabaglione/jr100dev/wiki/POTION-PATH) | 異なる20の注文を用意しました。素材を投入し、フラスコが途中の位置を通って移動します。注文に到達すると光と音が出ます。 |
| [AUCTION HOUSE](https://github.com/zabaglione/jr100dev/wiki/AUCTION-HOUSE) | 鑑定額を範囲で示し、相手は高値まで競ることもあります。自分の入札、相手の上乗せ、落札と売却額を順に表示します。6品終了時に62コインが目標です。 |
| [METRO WEAVE](https://github.com/zabaglione/jr100dev/wiki/METRO-WEAVE) | 3シフトで自動配車が速まり、同時運行数が2本から3本へ増えます。毎回変わる次の3本を読み、急行を手動増発できます。急行は得点が高い一方、信号待ち・荷下ろし待ちで遅延し、HPと連続成功を失います。車体は1マスずつ動き、自動で車間を保ちます。常設の操作説明はタイトル・ヘルプへ移し、本編は列車・進路・行先・待ち時間・得点を表示します。 |
| [CARGO BALANCE](https://github.com/zabaglione/jr100dev/wiki/CARGO-BALANCE) | 次の2つの荷重を予告します。積荷が船倉へ落下し、重い側へ船体が傾きます。左右の重さに加え、危険な偏りまでの距離を目盛で示します。 |
| [NUMBER VAULT](https://github.com/zabaglione/jr100dev/wiki/NUMBER-VAULT) | 暗号を開始時に変えます。ダイヤルを回す途中と4桁の照合を描き、直近6回の入力と位置一致・数字一致の数を残します。 |
| [SAND RESCUE](https://github.com/zabaglione/jr100dev/wiki/SAND-RESCUE) | 6つの畑で108滴の水を共有します。手前の作物は少量、奥の作物は高得点ですが、乾いた水路で水を失います。貯水と放流、最低収穫での終了と追加収穫を選び、余った水と得点を次へ持ち越します。水門、連続する水の移動、芽から実への成長、収穫、あふれに動きとSEがあります。 |
| [WORD FOUNDRY](https://github.com/zabaglione/jr100dev/wiki/WORD-FOUNDRY) | 一文字だけ置き換えられる候補すべてに印を付けます。変更する文字の移動と、ここまでの単語の経路を表示します。 |
| [RELIC DIVE](https://github.com/zabaglione/jr100dev/wiki/RELIC-DIVE) | 敵を攻撃すると、命中した一文字だけが打撃・破片・粒の三段階に変わり、音を鳴らします。他の同種の敵には影響しません。既存の被弾音と結果のジングルも維持しています。 |

## 確認したこと

- 全51作品のビルド、RAM・PCG配置、各作品のルール、入力とクリア経路を確認しました。開発ツールの単体テスト47件も通過しました。
- 新しい配札64例、真理値表22問、碑文20問、容疑者の12事件、競りの選択肢、装甲への2回命中を検証しました。演出中の5,059フレームについて画面範囲を確認しました。
- 所有するBASIC ROMで今回の35作品を起動し、画像と音付き動画を更新しました。開始・進行・最初の目標達成の3枚を並べた後に、動画へのリンクを置いています。
- 35本の動画は最初の目標達成までを収録しました。約30秒を目安とし、長いゲームは途中を省略せず収録しています。
- SS1実機での作品別の確認範囲は[MiSTerガイド](https://zabaglione.github.io/pyjr100emu/guide/mister.html)に掲載しています。オリジナルのJR-100実機は未確認です。

## IRON SCRIPT 2.0の追加確認

24面を独立した経路探索と入力リプレイで検証しました。すべての面で移動以外の命令、または枠数を節約する繰り返しが必要です。9種類の停止・再実行、ROM矢印、扉が開く3段階、撃破の4段階、装甲への2回命中、レーザー周期を確認しています。紹介画像と約31秒の1面クリア動画も更新しました。

## 全51作品の表示整理とMETRO WEAVE 2.0

全51作品の常設キー一覧を本編から外し、タイトル・ヘルプへまとめました。選択中の項目、ゴール、予告、数値、行動結果は残しています。画像・音付き動画も新しいPRGで再収録しました。

METRO WEAVEは3シフト・各8本で、通常便を待つか、高得点の急行を増発するかを選びます。駅での荷下ろしと信号待ちが急行の猶予を使います。192通りの配車試験、24本の通し運行、連続成功の加点、遅延境界、駅の待ち列、停止信号を検証しました。1シフトのクリア動画は約38秒です。

## SAND RESCUE 2.0とGATE RUNNER 3.0

SAND RESCUEは全6面の持ち越し、給水・消費・あふれを含む水量の保存、小量と満水での放流、追加収穫の得点と残り水、キャンペーンのやり直しを検証しました。GATE RUNNERは横27位置、ジャンプの長さ、壁・穴・梁の境界、毎コース3か所のジャンプ必須区間、1回の時計更新に移動かジャンプを1回だけ行う条件で全結晶を取れる経路を検証しました。両作とも6面を通常のキー入力で完走し、ROM起動・PCG・音声・16KB配置を確認しています。SS1実機での作品別の確認範囲は[MiSTerガイド](https://zabaglione.github.io/pyjr100emu/guide/mister.html)に掲載しています。オリジナルのJR-100実機は未確認です。
