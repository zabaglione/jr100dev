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

[タイトル順の全作品](All-Games) · [タイトル画面ギャラリー](#タイトル画面ギャラリー) · [共通操作と起動方法](Controls)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

基本の方向キーは **W/A/S/D**、8方向の作品は **QWE／AD／ZXC** です。作品ごとの操作は各ページに掲載しています。

エミュレーターで確認済みです。実機での動作・音声は未確認です。

[ビルド可能なソースと開発手順](https://github.com/zabaglione/jr100dev/tree/main/games)

**2026年9月18日更新：** タイトルの立体表現、開始・被弾・結果の音と間を更新しました。石返し、大きな駒の移動、敵の消滅にも途中の動きを加えています。[動きと音を動画で見る](Presentation)。

## タイトル画面ギャラリー

### [パズル](Genre-Puzzle)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/title.png" width="300" alt="FROST STEPS">](FROST-STEPS) | **[FROST STEPS](FROST-STEPS)**<br>氷上を止まれず滑り、全結晶を拾う。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=frost-steps) · [遊び方を見る](FROST-STEPS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/title.png" width="300" alt="FUSE BOX">](FUSE-BOX) | **[FUSE BOX](FUSE-BOX)**<br>行と列の個数を読んで配線図を復元する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=fuse-box) · [遊び方を見る](FUSE-BOX) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/title.png" width="300" alt="GLYPH SHIFT">](GLYPH-SHIFT) | **[GLYPH SHIFT](GLYPH-SHIFT)**<br>物体の通行ルールを書き換えて脱出する。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=glyph-shift) · [遊び方を見る](GLYPH-SHIFT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/title.png" width="300" alt="GRAVITY WELL">](GRAVITY-WELL) | **[GRAVITY WELL](GRAVITY-WELL)**<br>盤面を傾けて複数の球を同時に収める。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gravity-well) · [遊び方を見る](GRAVITY-WELL) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lumen-cross/title.png" width="300" alt="LUMEN CROSS">](LUMEN-CROSS) | **[LUMEN CROSS](LUMEN-CROSS)**<br>十字の反転で光の格子を消す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lumen-cross) · [遊び方を見る](LUMEN-CROSS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/title.png" width="300" alt="MAGNET VAULT">](MAGNET-VAULT) | **[MAGNET VAULT](MAGNET-VAULT)**<br>押せない金属塊を磁力で引いて収納する。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=magnet-vault) · [遊び方を見る](MAGNET-VAULT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/title.png" width="300" alt="NUMBER VAULT">](NUMBER-VAULT) | **[NUMBER VAULT](NUMBER-VAULT)**<br>一致数の手掛かりから暗証番号を解く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=number-vault) · [遊び方を見る](NUMBER-VAULT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/peg-garden/title.png" width="300" alt="PEG GARDEN">](PEG-GARDEN) | **[PEG GARDEN](PEG-GARDEN)**<br>飛び越しで石を取り除く庭園パズル<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=peg-garden) · [遊び方を見る](PEG-GARDEN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/title.png" width="300" alt="PHASE PAIRS">](PHASE-PAIRS) | **[PHASE PAIRS](PHASE-PAIRS)**<br>隣り合う数を10にして盤面を消す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=phase-pairs) · [遊び方を見る](PHASE-PAIRS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/title.png" width="300" alt="PRISM TRACE">](PRISM-TRACE) | **[PRISM TRACE](PRISM-TRACE)**<br>鏡の向きを変えて光を受光器へ導く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=prism-trace) · [遊び方を見る](PRISM-TRACE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/seed-merge/title.png" width="300" alt="SEED MERGE">](SEED-MERGE) | **[SEED MERGE](SEED-MERGE)**<br>同じ芽を合成して大樹を育てる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=seed-merge) · [遊び方を見る](SEED-MERGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/title.png" width="300" alt="TIDE BRIDGE">](TIDE-BRIDGE) | **[TIDE BRIDGE](TIDE-BRIDGE)**<br>潮位の連動する橋を切り替えて渡る<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tide-bridge) · [遊び方を見る](TIDE-BRIDGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/title.png" width="300" alt="TRACE BLADE">](TRACE-BLADE) | **[TRACE BLADE](TRACE-BLADE)**<br>一筆の経路を計画して連続撃破する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=trace-blade) · [遊び方を見る](TRACE-BLADE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/title.png" width="300" alt="WORD FOUNDRY">](WORD-FOUNDRY) | **[WORD FOUNDRY](WORD-FOUNDRY)**<br>一文字ずつ置き換えて指定の単語へ至る<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=word-foundry) · [遊び方を見る](WORD-FOUNDRY) |

### [カード・ボード](Genre-Tabletop)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/title.png" width="300" alt="CHAIN SUIT">](CHAIN-SUIT) | **[CHAIN SUIT](CHAIN-SUIT)**<br>手札交換と役の選択で得点ノルマに挑む<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chain-suit) · [遊び方を見る](CHAIN-SUIT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/title.png" width="300" alt="CORNER CROWN">](CORNER-CROWN) | **[CORNER CROWN](CORNER-CROWN)**<br>挟み取りと角の支配を競う盤面対戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=corner-crown) · [遊び方を見る](CORNER-CROWN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/title.png" width="300" alt="DICE RELIC">](DICE-RELIC) | **[DICE RELIC](DICE-RELIC)**<br>出目を使い、ダイスの面そのものを鍛える<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=dice-relic) · [遊び方を見る](DICE-RELIC) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/title.png" width="300" alt="FIVE FORGE">](FIVE-FORGE) | **[FIVE FORGE](FIVE-FORGE)**<br>妨害と四連の脅威を読む五目対戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=five-forge) · [遊び方を見る](FIVE-FORGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/title.png" width="300" alt="MEMORY MOSAIC">](MEMORY-MOSAIC) | **[MEMORY MOSAIC](MEMORY-MOSAIC)**<br>失敗回数を抑えて模様の対を探す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=memory-mosaic) · [遊び方を見る](MEMORY-MOSAIC) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/title.png" width="300" alt="ORBIT DRAFT">](ORBIT-DRAFT) | **[ORBIT DRAFT](ORBIT-DRAFT)**<br>九つの軌道に札を配り三連の共鳴を作る<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-draft) · [遊び方を見る](ORBIT-DRAFT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/title.png" width="300" alt="SIGIL DECK">](SIGIL-DECK) | **[SIGIL DECK](SIGIL-DECK)**<br>カードを組み合わせて虚空の王を封じる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sigil-deck) · [遊び方を見る](SIGIL-DECK) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/title.png" width="300" alt="STONE BALANCE">](STONE-BALANCE) | **[STONE BALANCE](STONE-BALANCE)**<br>三つの山の取り方を読み切る石取り<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=stone-balance) · [遊び方を見る](STONE-BALANCE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/title.png" width="300" alt="TWENTY ONE">](TWENTY-ONE) | **[TWENTY ONE](TWENTY-ONE)**<br>追加・停止を判断する21点カード勝負<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=twenty-one) · [遊び方を見る](TWENTY-ONE) |

### [戦術・自動化](Genre-Tactics)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/title.png" width="300" alt="CHRONO BREACH">](CHRONO-BREACH) | **[CHRONO BREACH](CHRONO-BREACH)**<br>弾道を読んで突破する20面の時間停止戦術<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chrono-breach) · [遊び方を見る](CHRONO-BREACH) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/title.png" width="300" alt="CIRCUIT WORKS">](CIRCUIT-WORKS) | **[CIRCUIT WORKS](CIRCUIT-WORKS)**<br>導線を接続し順序回路を完成させる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=circuit-works) · [遊び方を見る](CIRCUIT-WORKS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/title.png" width="300" alt="IRON SCRIPT">](IRON-SCRIPT) | **[IRON SCRIPT](IRON-SCRIPT)**<br>命令列を組んでロボットをゴールへ導く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=iron-script) · [遊び方を見る](IRON-SCRIPT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png" width="300" alt="METRO WEAVE">](METRO-WEAVE) | **[METRO WEAVE](METRO-WEAVE)**<br>分岐と信号を操作して乗客を運ぶ<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) · [遊び方を見る](METRO-WEAVE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/title.png" width="300" alt="SAND RESCUE">](SAND-RESCUE) | **[SAND RESCUE](SAND-RESCUE)**<br>堰を開閉して水を作物へ導く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sand-rescue) · [遊び方を見る](SAND-RESCUE) |

### [アクション](Genre-Action)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/title.png" width="300" alt="BRICK PULSE">](BRICK-PULSE) | **[BRICK PULSE](BRICK-PULSE)**<br>装甲ブロック・アイテム・ドローンに挑む12面のブロック崩し<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=brick-pulse) · [遊び方を見る](BRICK-PULSE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/title.png" width="300" alt="ECHO PARRY">](ECHO-PARRY) | **[ECHO PARRY](ECHO-PARRY)**<br>敵の予備動作を読んで反撃する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) · [遊び方を見る](ECHO-PARRY) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/title.png" width="300" alt="GATE RUNNER">](GATE-RUNNER) | **[GATE RUNNER](GATE-RUNNER)**<br>三本の走路で障壁と穴を突破する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gate-runner) · [遊び方を見る](GATE-RUNNER) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/title.png" width="300" alt="LUNAR TOUCHDOWN">](LUNAR-TOUCHDOWN) | **[LUNAR TOUCHDOWN](LUNAR-TOUCHDOWN)**<br>燃料と降下速度を調整する着陸挑戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lunar-touchdown) · [遊び方を見る](LUNAR-TOUCHDOWN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/title.png" width="300" alt="NIGHT SWARM">](NIGHT-SWARM) | **[NIGHT SWARM](NIGHT-SWARM)**<br>迫る群れを誘導し射線を開いて生還する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=night-swarm) · [遊び方を見る](NIGHT-SWARM) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/title.png" width="300" alt="ORBIT DODGE">](ORBIT-DODGE) | **[ORBIT DODGE](ORBIT-DODGE)**<br>円軌道を移動して放射状の攻撃を避ける<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-dodge) · [遊び方を見る](ORBIT-DODGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/title.png" width="300" alt="PENDULUM PORT">](PENDULUM-PORT) | **[PENDULUM PORT](PENDULUM-PORT)**<br>振り子の頂点で次の足場へ跳ぶ<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=pendulum-port) · [遊び方を見る](PENDULUM-PORT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/title.png" width="300" alt="RIBBON SNAKE">](RIBBON-SNAKE) | **[RIBBON SNAKE](RIBBON-SNAKE)**<br>伸びる軌跡を制御して食料を回収する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ribbon-snake) · [遊び方を見る](RIBBON-SNAKE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/title.png" width="300" alt="STAR LANCE">](STAR-LANCE) | **[STAR LANCE](STAR-LANCE)**<br>隊列の隙間を抜いて迎撃する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) · [遊び方を見る](STAR-LANCE) |

### [探索・アドベンチャー](Genre-Exploration)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/title.png" width="300" alt="ABYSS SIGNAL">](ABYSS-SIGNAL) | **[ABYSS SIGNAL](ABYSS-SIGNAL)**<br>ソナーと酸素計を頼りに海底遺構を観測<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=abyss-signal) · [遊び方を見る](ABYSS-SIGNAL) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/title.png" width="300" alt="COMPASS ROSE">](COMPASS-ROSE) | **[COMPASS ROSE](COMPASS-ROSE)**<br>方位の手掛かりを頼りに隠れた宝を探す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=compass-rose) · [遊び方を見る](COMPASS-ROSE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/title.png" width="300" alt="LOOP TEN">](LOOP-TEN) | **[LOOP TEN](LOOP-TEN)**<br>10秒の巻き戻しを越えて12の封印を解く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=loop-ten) · [遊び方を見る](LOOP-TEN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/title.png" width="300" alt="MIRROR RELIC">](MIRROR-RELIC) | **[MIRROR RELIC](MIRROR-RELIC)**<br>四つの視点を回して遺物の通路を開く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=mirror-relic) · [遊び方を見る](MIRROR-RELIC) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/quiet-route/title.png" width="300" alt="QUIET ROUTE">](QUIET-ROUTE) | **[QUIET ROUTE](QUIET-ROUTE)**<br>巡回の向きと足音を読んで機密を運ぶ<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=quiet-route) · [遊び方を見る](QUIET-ROUTE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/title.png" width="300" alt="RELIC DIVE">](RELIC-DIVE) | **[RELIC DIVE](RELIC-DIVE)**<br>64×32マスの迷宮で食料・装備・魔法を使い、最深部の遺物を探す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=relic-dive) · [遊び方を見る](RELIC-DIVE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/title.png" width="300" alt="RUIN LEXICON">](RUIN-LEXICON) | **[RUIN LEXICON](RUIN-LEXICON)**<br>碑文の対応から失われた記号を解読する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ruin-lexicon) · [遊び方を見る](RUIN-LEXICON) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/title.png" width="300" alt="SHADOW ARCHIVE">](SHADOW-ARCHIVE) | **[SHADOW ARCHIVE](SHADOW-ARCHIVE)**<br>証言と記録を照合して容疑者を特定する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=shadow-archive) · [遊び方を見る](SHADOW-ARCHIVE) |

### [経営・サバイバル](Genre-Management)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/title.png" width="300" alt="AUCTION HOUSE">](AUCTION-HOUSE) | **[AUCTION HOUSE](AUCTION-HOUSE)**<br>相場と残金を読んで競売に参加する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=auction-house) · [遊び方を見る](AUCTION-HOUSE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/title.png" width="300" alt="CARGO BALANCE">](CARGO-BALANCE) | **[CARGO BALANCE](CARGO-BALANCE)**<br>積荷の位置を選び船の傾きを抑える<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=cargo-balance) · [遊び方を見る](CARGO-BALANCE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/hearth-zero/title.png" width="300" alt="HEARTH ZERO">](HEARTH-ZERO) | **[HEARTH ZERO](HEARTH-ZERO)**<br>食料・薪・熱を配分して寒波を越える<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=hearth-zero) · [遊び方を見る](HEARTH-ZERO) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/title.png" width="300" alt="ORCHARD DAYS">](ORCHARD-DAYS) | **[ORCHARD DAYS](ORCHARD-DAYS)**<br>種まきと水やりを配分して果樹園を育てる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orchard-days) · [遊び方を見る](ORCHARD-DAYS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/title.png" width="300" alt="POTION PATH">](POTION-PATH) | **[POTION PATH](POTION-PATH)**<br>素材の移動量を組み合わせ注文を調合する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=potion-path) · [遊び方を見る](POTION-PATH) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/title.png" width="300" alt="TIDAL NETS">](TIDAL-NETS) | **[TIDAL NETS](TIDAL-NETS)**<br>潮の流れに網を置き魚群を捕らえる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tidal-nets) · [遊び方を見る](TIDAL-NETS) |
