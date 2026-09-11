# JR-100 Games

標準RAM 16KB向けのオリジナルゲーム51作品です。ジャンルから選ぶと、各作品の画面・遊び方・起動リンクを探せます。

| ジャンル | 作品数 | 内容 |
| --- | ---: | --- |
| [パズル](Genre-Puzzle) | 14 | 考える時間を楽しむ、経路・反転・数のゲーム |
| [カード・ボード](Genre-Tabletop) | 9 | 札・ダイス・盤面を使う読み合い |
| [戦術・自動化](Genre-Tactics) | 5 | 手順・配置・流れを組み立てるゲーム |
| [アクション](Genre-Action) | 9 | 移動・照準・タイミングを使うゲーム |
| [探索・アドベンチャー](Genre-Exploration) | 8 | 地図・手掛かり・環境を読み解くゲーム |
| [経営・サバイバル](Genre-Management) | 6 | 資源を配分し、状況の変化に備えるゲーム |

[タイトル順の全作品](All-Games) · [タイトル画面ギャラリー](#タイトル画面ギャラリー) · [共通操作と起動方法](Controls) · [画面表現の工夫](Visual-Design) · [専用フォント](Font-Design)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

基本の方向キーは **W/A/S/D**、8方向の作品は **QWE／AD／ZXC** です。作品ごとの操作は各ページに掲載しています。

エミュレーターで確認済みです。実機での動作・音声は未確認です。

[移動とクリア演出・動作動画](Motion-and-Clear)

[ビルド可能なソースと開発手順](https://github.com/zabaglione/jr100dev/tree/main/games)

## タイトル画面ギャラリー

すべてゲーム本体のPCGで描画します。標準RAM 16KB、PCG最大32文字の範囲内です。画像は所有するBASIC ROMから起動したエミュレーターの実画面で、実機での表示は未確認です。

### [パズル](Genre-Puzzle)

| タイトル画面 | デザインと起動 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/title.png" width="300" alt="FROST STEPS">](FROST-STEPS) | **[FROST STEPS](FROST-STEPS)**<br>右上へ続く氷の足場と結晶を描き、横長のFROSTに細かい切り口を入れています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=frost-steps) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/title.png" width="300" alt="FUSE BOX">](FUSE-BOX) | **[FUSE BOX](FUSE-BOX)**<br>大きな白い配電盤から右へ配線を引き、横長FUSEと下のBOXで機械の形を囲みます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=fuse-box) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/title.png" width="300" alt="GLYPH SHIFT">](GLYPH-SHIFT) | **[GLYPH SHIFT](GLYPH-SHIFT)**<br>白い石板の刻印が階段状に移り変わる構図です。ロゴにも石の刻みを入れています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=glyph-shift) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/title.png" width="300" alt="GRAVITY WELL">](GRAVITY-WELL) | **[GRAVITY WELL](GRAVITY-WELL)**<br>右下の重力井戸へ小さな球が落ちる構図にし、ロゴは左上の広い暗部にまとめています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gravity-well) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lumen-cross/title.png" width="300" alt="LUMEN CROSS">](LUMEN-CROSS) | **[LUMEN CROSS](LUMEN-CROSS)**<br>左半分の大きな十字と右の光の結晶を対置します。ロゴには結晶の切り口を加えています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lumen-cross) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/title.png" width="300" alt="MAGNET VAULT">](MAGNET-VAULT) | **[MAGNET VAULT](MAGNET-VAULT)**<br>巨大なU字磁石から金属片が吸い寄せられる構図です。MAGNETを下、VAULTを磁力の先に配置します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=magnet-vault) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/title.png" width="300" alt="NUMBER VAULT">](NUMBER-VAULT) | **[NUMBER VAULT](NUMBER-VAULT)**<br>左の大きな金庫と右の「314」の番号窓を主役にし、NUMBERとVAULTを上下に分けています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=number-vault) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/peg-garden/title.png" width="300" alt="PEG GARDEN">](PEG-GARDEN) | **[PEG GARDEN](PEG-GARDEN)**<br>駒を飛び越える軌跡と右の若葉を組み合わせ、盤上の遊びを庭の成長として描きます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=peg-garden) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/title.png" width="300" alt="PHASE PAIRS">](PHASE-PAIRS) | **[PHASE PAIRS](PHASE-PAIRS)**<br>4と6、3と7が10へつながる数字の組を描き、切り口を付けたロゴで計算の鋭さを表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=phase-pairs) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/title.png" width="300" alt="PRISM TRACE">](PRISM-TRACE) | **[PRISM TRACE](PRISM-TRACE)**<br>プリズムを通った光が三方向へ分かれる瞬間を描き、PRISMとTRACEを光路の上下に置きます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=prism-trace) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/seed-merge/title.png" width="300" alt="SEED MERGE">](SEED-MERGE) | **[SEED MERGE](SEED-MERGE)**<br>芽から大きな木までの成長を左から右へ並べ、下の種と地面の線で栽培の循環を示します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=seed-merge) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/title.png" width="300" alt="TIDE BRIDGE">](TIDE-BRIDGE) | **[TIDE BRIDGE](TIDE-BRIDGE)**<br>水面から持ち上がった橋と橋脚を大きく描き、横長のTIDEで川幅を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tide-bridge) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/title.png" width="300" alt="TRACE BLADE">](TRACE-BLADE) | **[TRACE BLADE](TRACE-BLADE)**<br>大きな斜めの刃が経路を横切る構図です。傾いた文字と標的の菱形を斬撃の方向に揃えています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=trace-blade) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/title.png" width="300" alt="WORD FOUNDRY">](WORD-FOUNDRY) | **[WORD FOUNDRY](WORD-FOUNDRY)**<br>コンベヤー上のA・B・Cの活字を白抜きと輪郭で並べ、横長WORDで文字を作る工場を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=word-foundry) |

### [カード・ボード](Genre-Tabletop)

| タイトル画面 | デザインと起動 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/title.png" width="300" alt="CHAIN SUIT">](CHAIN-SUIT) | **[CHAIN SUIT](CHAIN-SUIT)**<br>三枚のカードを高さを変えて鎖でつなぎ、上のCHAINと右下のSUITで連鎖を囲みます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chain-suit) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/title.png" width="300" alt="CORNER CROWN">](CORNER-CROWN) | **[CORNER CROWN](CORNER-CROWN)**<br>角を強調した盤と大きな王冠を左右に分け、CORNERとCROWNをそれぞれに対応させます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=corner-crown) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/title.png" width="300" alt="DICE RELIC">](DICE-RELIC) | **[DICE RELIC](DICE-RELIC)**<br>大きなダイスと遺物の紋章を並べ、上のDICEと右下のRELICが両者を結びます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=dice-relic) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/title.png" width="300" alt="FIVE FORGE">](FIVE-FORGE) | **[FIVE FORGE](FIVE-FORGE)**<br>金床に並ぶ五つの駒と振り下ろすハンマーを描き、石の刻印風のロゴで鍛冶場を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=five-forge) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/title.png" width="300" alt="MEMORY MOSAIC">](MEMORY-MOSAIC) | **[MEMORY MOSAIC](MEMORY-MOSAIC)**<br>横に並ぶ札と離れた一枚を結ぶ構図で、記憶して組を探す遊びを表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=memory-mosaic) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/title.png" width="300" alt="ORBIT DRAFT">](ORBIT-DRAFT) | **[ORBIT DRAFT](ORBIT-DRAFT)**<br>三枚のカードを軌道上に配置し、ORBITを左上、DRAFTを左下に置いて円を挟みます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-draft) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/title.png" width="300" alt="SIGIL DECK">](SIGIL-DECK) | **[SIGIL DECK](SIGIL-DECK)**<br>縦長のDECKロゴと重なったカードを左右に分け、魔法陣でカードの儀式を表しています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sigil-deck) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/title.png" width="300" alt="STONE BALANCE">](STONE-BALANCE) | **[STONE BALANCE](STONE-BALANCE)**<br>大きさも数も違う石が釣り合う天秤を中央に置き、石の刻印風の文字で上下を囲みます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=stone-balance) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/title.png" width="300" alt="TWENTY ONE">](TWENTY-ONE) | **[TWENTY ONE](TWENTY-ONE)**<br>右上の大きな「21」を主役にし、左下の重なった札と右下のタイトルで卓上を構成します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=twenty-one) |

### [戦術・自動化](Genre-Tactics)

| タイトル画面 | デザインと起動 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/title.png" width="300" alt="CHRONO BREACH">](CHRONO-BREACH) | **[CHRONO BREACH](CHRONO-BREACH)**<br>左の白い施設壁と中央の時間の亀裂を対置し、右上の時計から右下のロゴへ視線を導きます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chrono-breach) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/title.png" width="300" alt="CIRCUIT WORKS">](CIRCUIT-WORKS) | **[CIRCUIT WORKS](CIRCUIT-WORKS)**<br>二つの入力がANDゲートへ合流する配線図を主役にし、CIRCUITとWORKSを回路の上下に置きます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=circuit-works) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/title.png" width="300" alt="IRON SCRIPT">](IRON-SCRIPT) | **[IRON SCRIPT](IRON-SCRIPT)**<br>大きなロボットと命令ボタンを左右に置き、横に広いIRONで工場の重さを表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=iron-script) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png" width="300" alt="METRO WEAVE">](METRO-WEAVE) | **[METRO WEAVE](METRO-WEAVE)**<br>交差する三本の路線と駅、上部の車両で交通網を描き、路線の余白へロゴを配置しています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/title.png" width="300" alt="SAND RESCUE">](SAND-RESCUE) | **[SAND RESCUE](SAND-RESCUE)**<br>上の水路から砂丘と作物へ流れを引き、石の刻印風のロゴで乾いた土地の雰囲気を出します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sand-rescue) |

### [アクション](Genre-Action)

| タイトル画面 | デザインと起動 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/title.png" width="300" alt="BRICK PULSE">](BRICK-PULSE) | **[BRICK PULSE](BRICK-PULSE)**<br>上のブロック帯、弾む球と軌跡、下のパドルを一枚にまとめ、斜体ロゴにスリットで勢いを付けます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=brick-pulse) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/title.png" width="300" alt="ECHO PARRY">](ECHO-PARRY) | **[ECHO PARRY](ECHO-PARRY)**<br>大きな盾と斜めの剣を対置し、横長ECHOと下のPARRYで受け止める瞬間を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/title.png" width="300" alt="GATE RUNNER">](GATE-RUNNER) | **[GATE RUNNER](GATE-RUNNER)**<br>奥に収束する走路と迫るゲートを描き、横長GATEと傾いたRUNNERにスリットを入れています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gate-runner) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/title.png" width="300" alt="LUNAR TOUCHDOWN">](LUNAR-TOUCHDOWN) | **[LUNAR TOUCHDOWN](LUNAR-TOUCHDOWN)**<br>横長LUNARの下に月着陸船と起伏を描き、着陸脚と噴射を白黒の抜きで示します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lunar-touchdown) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/title.png" width="300" alt="NIGHT SWARM">](NIGHT-SWARM) | **[NIGHT SWARM](NIGHT-SWARM)**<br>ロゴを取り囲む敵の群れと下部の小さな自機で圧迫感を出し、文字に細いスリットを入れています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=night-swarm) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/title.png" width="300" alt="ORBIT DODGE">](ORBIT-DODGE) | **[ORBIT DODGE](ORBIT-DODGE)**<br>大きな三日月と軌道を左に、迫る射線を右に配置し、ロゴを軌道の手前に重ねています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-dodge) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/title.png" width="300" alt="PENDULUM PORT">](PENDULUM-PORT) | **[PENDULUM PORT](PENDULUM-PORT)**<br>細い振り子の線と大きな重りを主役にし、下の足場との間隔で渡る緊張感を出します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=pendulum-port) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/title.png" width="300" alt="RIBBON SNAKE">](RIBBON-SNAKE) | **[RIBBON SNAKE](RIBBON-SNAKE)**<br>画面を折り返す長い蛇を二重の輪郭で描き、体が作る空間にSNAKEの文字を収めています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ribbon-snake) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/title.png" width="300" alt="STAR LANCE">](STAR-LANCE) | **[STAR LANCE](STAR-LANCE)**<br>縦長STARと大型戦闘機、下から迫る敵の編隊を配置し、ビームとスリット入りの文字で速度を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) |

### [探索・アドベンチャー](Genre-Exploration)

| タイトル画面 | デザインと起動 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/title.png" width="300" alt="ABYSS SIGNAL">](ABYSS-SIGNAL) | **[ABYSS SIGNAL](ABYSS-SIGNAL)**<br>横に広いABYSSと深い海底のシルエットで、潜水艇の小ささと探索の不安を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=abyss-signal) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/title.png" width="300" alt="COMPASS ROSE">](COMPASS-ROSE) | **[COMPASS ROSE](COMPASS-ROSE)**<br>左の大きな羅針盤から右の目標へ点線を伸ばし、航路を挟んでタイトルを分けています。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=compass-rose) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/title.png" width="300" alt="LOOP TEN">](LOOP-TEN) | **[LOOP TEN](LOOP-TEN)**<br>画面左を占める二重の巻き戻し矢印に「10」を収め、右の縦長TENで十手の制約を強調します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=loop-ten) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/title.png" width="300" alt="MIRROR RELIC">](MIRROR-RELIC) | **[MIRROR RELIC](MIRROR-RELIC)**<br>中央の縦長の鏡と左右の対称な紋章を描き、石の刻印風の文字で遺物の雰囲気を出します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=mirror-relic) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/quiet-route/title.png" width="300" alt="QUIET ROUTE">](QUIET-ROUTE) | **[QUIET ROUTE](QUIET-ROUTE)**<br>白い街のシルエットとサーチライトの中に黒い人影を隠し、上部に暗い空とロゴの余白を取ります。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=quiet-route) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/title.png" width="300" alt="RELIC DIVE">](RELIC-DIVE) | **[RELIC DIVE](RELIC-DIVE)**<br>左の縦長の石文字と右の巨大な遺跡の門を対置します。門の奥の遺物と小さくきらめく光が探索へ誘います。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=relic-dive) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/title.png" width="300" alt="RUIN LEXICON">](RUIN-LEXICON) | **[RUIN LEXICON](RUIN-LEXICON)**<br>割れた白い石板に黒い刻印を入れ、周囲の記号と石の質感を持つロゴで解読の世界を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ruin-lexicon) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/title.png" width="300" alt="SHADOW ARCHIVE">](SHADOW-ARCHIVE) | **[SHADOW ARCHIVE](SHADOW-ARCHIVE)**<br>白帯の黒文字SHADOW、黒塗りの資料、人物を拡大する虫眼鏡で、機密資料の表紙を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=shadow-archive) |

### [経営・サバイバル](Genre-Management)

| タイトル画面 | デザインと起動 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/title.png" width="300" alt="AUCTION HOUSE">](AUCTION-HOUSE) | **[AUCTION HOUSE](AUCTION-HOUSE)**<br>大きな木槌と積んだコインを左右に置き、落札の一打を強い白い形で表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=auction-house) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/title.png" width="300" alt="CARGO BALANCE">](CARGO-BALANCE) | **[CARGO BALANCE](CARGO-BALANCE)**<br>高さの違う荷物を積んだ船を描き、横長CARGOで船幅、BALANCEで積載の課題を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=cargo-balance) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/hearth-zero/title.png" width="300" alt="HEARTH ZERO">](HEARTH-ZERO) | **[HEARTH ZERO](HEARTH-ZERO)**<br>左の大きな暖炉と右の雪を対置します。石の刻印を思わせるロゴで、熱源を守る世界を表します。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=hearth-zero) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/title.png" width="300" alt="ORCHARD DAYS">](ORCHARD-DAYS) | **[ORCHARD DAYS](ORCHARD-DAYS)**<br>大きさの違う三本の果樹を白いシルエットで描き、果実を黒い抜きで示す明るい農園の表紙です。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orchard-days) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/title.png" width="300" alt="POTION PATH">](POTION-PATH) | **[POTION PATH](POTION-PATH)**<br>左の大きな薬瓶から右上へ材料の経路を伸ばし、POTIONとPATHを道の入口と出口に置きます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=potion-path) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/title.png" width="300" alt="TIDAL NETS">](TIDAL-NETS) | **[TIDAL NETS](TIDAL-NETS)**<br>大きな船体と海中に広がる網を描き、横長TIDALと右のNETSが漁の場面を挟みます。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tidal-nets) |
