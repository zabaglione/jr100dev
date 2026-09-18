# JR-100 Games

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/) · [All 51 games ZIP / 全51作品](https://zabaglione.github.io/pyjr100emu/guide/downloads/jr100-games-mister.zip) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

標準RAM 16KB向けのオリジナルゲーム51作品です。ジャンルから選ぶと、各作品の画面・遊び方・起動リンクを探せます。

各作品に3枚以上の紹介画像と、最初の目標達成までの音付きプレイ動画を掲載しています。[全51作品の動画ギャラリー](https://zabaglione.github.io/pyjr100emu/gameplay.html)からも選べます。

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

エミュレーターで確認済みです。SS1実機での作品別の確認範囲は[MiSTerガイド](https://zabaglione.github.io/pyjr100emu/guide/mister.html)に掲載しています。オリジナルのJR-100実機は未確認です。

[ビルド可能なソースと開発手順](https://github.com/zabaglione/jr100dev/tree/main/games)

**2026年9月18日更新：** さらに25作品を個別に改修しました。2軌道を渡るORBIT DODGE、熱を管理するSTAR LANCE、2種類の作物を育てるORCHARD DAYSなど、見た目と音に加えて攻略の選択肢を増やしています。[25作品の変更点](Second-Review)／[これまでの改善](Quality-Review)／[動きと音の紹介](Presentation)。

## タイトル画面ギャラリー

### [パズル](Genre-Puzzle)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/frost-steps/title.png" width="300" alt="FROST STEPS">](FROST-STEPS) | **[FROST STEPS](FROST-STEPS)**<br>氷上を止まれず滑り、全結晶を拾う。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=frost-steps) · [遊び方を見る](FROST-STEPS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/fuse-box/title.png" width="300" alt="FUSE BOX">](FUSE-BOX) | **[FUSE BOX](FUSE-BOX)**<br>行と列の個数を読んで配線図を復元する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=fuse-box) · [遊び方を見る](FUSE-BOX) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/glyph-shift/title.png" width="300" alt="GLYPH SHIFT">](GLYPH-SHIFT) | **[GLYPH SHIFT](GLYPH-SHIFT)**<br>物体の通行ルールを書き換えて脱出する。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=glyph-shift) · [遊び方を見る](GLYPH-SHIFT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gravity-well/title.png" width="300" alt="GRAVITY WELL">](GRAVITY-WELL) | **[GRAVITY WELL](GRAVITY-WELL)**<br>盤面を傾けて複数の球を同時に収める。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gravity-well) · [遊び方を見る](GRAVITY-WELL) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lumen-cross/title.png" width="300" alt="LUMEN CROSS">](LUMEN-CROSS) | **[LUMEN CROSS](LUMEN-CROSS)**<br>反転範囲を読み、最短回数を狙う18面の消灯パズル<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lumen-cross) · [遊び方を見る](LUMEN-CROSS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/magnet-vault/title.png" width="300" alt="MAGNET VAULT">](MAGNET-VAULT) | **[MAGNET VAULT](MAGNET-VAULT)**<br>押せない金属塊を磁力で引いて収納する。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=magnet-vault) · [遊び方を見る](MAGNET-VAULT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/title.png" width="300" alt="NUMBER VAULT">](NUMBER-VAULT) | **[NUMBER VAULT](NUMBER-VAULT)**<br>推理の履歴を読み、動く扉を開く暗証番号パズル<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=number-vault) · [遊び方を見る](NUMBER-VAULT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/peg-garden/title.png" width="300" alt="PEG GARDEN">](PEG-GARDEN) | **[PEG GARDEN](PEG-GARDEN)**<br>飛び越しで石を取り除く庭園パズル<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=peg-garden) · [遊び方を見る](PEG-GARDEN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/phase-pairs/title.png" width="300" alt="PHASE PAIRS">](PHASE-PAIRS) | **[PHASE PAIRS](PHASE-PAIRS)**<br>隣り合う数を10にして盤面を消す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=phase-pairs) · [遊び方を見る](PHASE-PAIRS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/prism-trace/title.png" width="300" alt="PRISM TRACE">](PRISM-TRACE) | **[PRISM TRACE](PRISM-TRACE)**<br>鏡の向きを変えて光を受光器へ導く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=prism-trace) · [遊び方を見る](PRISM-TRACE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/seed-merge/title.png" width="300" alt="SEED MERGE">](SEED-MERGE) | **[SEED MERGE](SEED-MERGE)**<br>同じ芽を合成して大樹を育てる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=seed-merge) · [遊び方を見る](SEED-MERGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tide-bridge/title.png" width="300" alt="TIDE BRIDGE">](TIDE-BRIDGE) | **[TIDE BRIDGE](TIDE-BRIDGE)**<br>潮位の連動する橋を切り替えて渡る<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tide-bridge) · [遊び方を見る](TIDE-BRIDGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/trace-blade/title.png" width="300" alt="TRACE BLADE">](TRACE-BLADE) | **[TRACE BLADE](TRACE-BLADE)**<br>一筆の経路を計画して連続撃破する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=trace-blade) · [遊び方を見る](TRACE-BLADE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/word-foundry/title.png" width="300" alt="WORD FOUNDRY">](WORD-FOUNDRY) | **[WORD FOUNDRY](WORD-FOUNDRY)**<br>中継単語を経由して辿る16の単語迷路<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=word-foundry) · [遊び方を見る](WORD-FOUNDRY) |

### [カード・ボード](Genre-Tabletop)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chain-suit/title.png" width="300" alt="CHAIN SUIT">](CHAIN-SUIT) | **[CHAIN SUIT](CHAIN-SUIT)**<br>手札交換と役の選択で得点ノルマに挑む<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chain-suit) · [遊び方を見る](CHAIN-SUIT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/corner-crown/title.png" width="300" alt="CORNER CROWN">](CORNER-CROWN) | **[CORNER CROWN](CORNER-CROWN)**<br>挟み取りと角の支配を競う盤面対戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=corner-crown) · [遊び方を見る](CORNER-CROWN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/dice-relic/title.png" width="300" alt="DICE RELIC">](DICE-RELIC) | **[DICE RELIC](DICE-RELIC)**<br>出目を使い、ダイスの面そのものを鍛える<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=dice-relic) · [遊び方を見る](DICE-RELIC) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/five-forge/title.png" width="300" alt="FIVE FORGE">](FIVE-FORGE) | **[FIVE FORGE](FIVE-FORGE)**<br>妨害と四連の脅威を読む五目対戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=five-forge) · [遊び方を見る](FIVE-FORGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/memory-mosaic/title.png" width="300" alt="MEMORY MOSAIC">](MEMORY-MOSAIC) | **[MEMORY MOSAIC](MEMORY-MOSAIC)**<br>札の厚みと5段階の反転で遊ぶ10面の神経衰弱<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=memory-mosaic) · [遊び方を見る](MEMORY-MOSAIC) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/title.png" width="300" alt="ORBIT DRAFT">](ORBIT-DRAFT) | **[ORBIT DRAFT](ORBIT-DRAFT)**<br>4×4・5種類の天体を、候補2枚と次の3枚を読んで揃える。回転と落下連鎖で得点を伸ばすエンドレスパズル<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-draft) · [遊び方を見る](ORBIT-DRAFT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sigil-deck/title.png" width="300" alt="SIGIL DECK">](SIGIL-DECK) | **[SIGIL DECK](SIGIL-DECK)**<br>カードを組み合わせて虚空の王を封じる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sigil-deck) · [遊び方を見る](SIGIL-DECK) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/stone-balance/title.png" width="300" alt="STONE BALANCE">](STONE-BALANCE) | **[STONE BALANCE](STONE-BALANCE)**<br>最後の石が勝ちから負けへ変わる10局の取り合い<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=stone-balance) · [遊び方を見る](STONE-BALANCE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/twenty-one/title.png" width="300" alt="TWENTY ONE">](TWENTY-ONE) | **[TWENTY ONE](TWENTY-ONE)**<br>52枚の山札とダブルを使い7勝負の収支を競う<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=twenty-one) · [遊び方を見る](TWENTY-ONE) |

### [戦術・自動化](Genre-Tactics)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/chrono-breach/title.png" width="300" alt="CHRONO BREACH">](CHRONO-BREACH) | **[CHRONO BREACH](CHRONO-BREACH)**<br>弾道を読んで突破する20面の時間停止戦術<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=chrono-breach) · [遊び方を見る](CHRONO-BREACH) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/circuit-works/title.png" width="300" alt="CIRCUIT WORKS">](CIRCUIT-WORKS) | **[CIRCUIT WORKS](CIRCUIT-WORKS)**<br>配線を流れる0/1を見ながら組む22の論理回路<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=circuit-works) · [遊び方を見る](CIRCUIT-WORKS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/title.png" width="300" alt="IRON SCRIPT">](IRON-SCRIPT) | **[IRON SCRIPT](IRON-SCRIPT)**<br>射撃・スイッチ・繰り返しの命令で24の工場を攻略<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=iron-script) · [遊び方を見る](IRON-SCRIPT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/metro-weave/title.png" width="300" alt="METRO WEAVE">](METRO-WEAVE) | **[METRO WEAVE](METRO-WEAVE)**<br>分岐と信号で複数列車をさばき、混雑を読んで急行を増発する<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=metro-weave) · [遊び方を見る](METRO-WEAVE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/title.png" width="300" alt="SAND RESCUE">](SAND-RESCUE) | **[SAND RESCUE](SAND-RESCUE)**<br>限られた水を6つの畑へ配分し、安全な収穫と追加の実りを選ぶ<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sand-rescue) · [遊び方を見る](SAND-RESCUE) |

### [アクション](Genre-Action)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/brick-pulse/title.png" width="300" alt="BRICK PULSE">](BRICK-PULSE) | **[BRICK PULSE](BRICK-PULSE)**<br>装甲ブロック・アイテム・ドローンに挑む12面のブロック崩し<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=brick-pulse) · [遊び方を見る](BRICK-PULSE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/title.png" width="300" alt="ECHO PARRY">](ECHO-PARRY) | **[ECHO PARRY](ECHO-PARRY)**<br>フェイントを見抜き、後退と遅い受け流しを使い分ける<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) · [遊び方を見る](ECHO-PARRY) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/gate-runner/title.png" width="300" alt="GATE RUNNER">](GATE-RUNNER) | **[GATE RUNNER](GATE-RUNNER)**<br>横位置を細かく調整し、壁・全幅の穴・低い梁を越える疑似3Dランニング<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=gate-runner) · [遊び方を見る](GATE-RUNNER) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/lunar-touchdown/title.png" width="300" alt="LUNAR TOUCHDOWN">](LUNAR-TOUCHDOWN) | **[LUNAR TOUCHDOWN](LUNAR-TOUCHDOWN)**<br>横風と燃料を読み、狭い着陸場の追加点を狙う<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=lunar-touchdown) · [遊び方を見る](LUNAR-TOUCHDOWN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/night-swarm/title.png" width="300" alt="NIGHT SWARM">](NIGHT-SWARM) | **[NIGHT SWARM](NIGHT-SWARM)**<br>補給へ踏み込む判断と装甲戦を加えた6夜の生存戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=night-swarm) · [遊び方を見る](NIGHT-SWARM) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-dodge/title.png" width="300" alt="ORBIT DODGE">](ORBIT-DODGE) | **[ORBIT DODGE](ORBIT-DODGE)**<br>2軌道を渡り、同時光線と連続回収に挑む6面<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-dodge) · [遊び方を見る](ORBIT-DODGE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/pendulum-port/title.png" width="300" alt="PENDULUM PORT">](PENDULUM-PORT) | **[PENDULUM PORT](PENDULUM-PORT)**<br>ロープ長と振りを合わせ、中央着地を狙う6区間<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=pendulum-port) · [遊び方を見る](PENDULUM-PORT) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ribbon-snake/title.png" width="300" alt="RIBBON SNAKE">](RIBBON-SNAKE) | **[RIBBON SNAKE](RIBBON-SNAKE)**<br>岩の庭で逃げ道を作り、3回のブレーキを使う<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ribbon-snake) · [遊び方を見る](RIBBON-SNAKE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/star-lance/title.png" width="300" alt="STAR LANCE">](STAR-LANCE) | **[STAR LANCE](STAR-LANCE)**<br>装甲・追尾射撃・熱管理に挑む6波の宇宙戦<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) · [遊び方を見る](STAR-LANCE) |

### [探索・アドベンチャー](Genre-Exploration)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/title.png" width="300" alt="ABYSS SIGNAL">](ABYSS-SIGNAL) | **[ABYSS SIGNAL](ABYSS-SIGNAL)**<br>ソナーと酸素計を頼りに海底遺構を観測<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=abyss-signal) · [遊び方を見る](ABYSS-SIGNAL) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/compass-rose/title.png" width="300" alt="COMPASS ROSE">](COMPASS-ROSE) | **[COMPASS ROSE](COMPASS-ROSE)**<br>測定する場所を選び、方角と距離帯から探し当てる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=compass-rose) · [遊び方を見る](COMPASS-ROSE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/loop-ten/title.png" width="300" alt="LOOP TEN">](LOOP-TEN) | **[LOOP TEN](LOOP-TEN)**<br>10秒の巻き戻しを越えて12の封印を解く<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=loop-ten) · [遊び方を見る](LOOP-TEN) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/mirror-relic/title.png" width="300" alt="MIRROR RELIC">](MIRROR-RELIC) | **[MIRROR RELIC](MIRROR-RELIC)**<br>左右の鏡回転と位相を合わせる6つの遺跡<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=mirror-relic) · [遊び方を見る](MIRROR-RELIC) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/quiet-route/title.png" width="300" alt="QUIET ROUTE">](QUIET-ROUTE) | **[QUIET ROUTE](QUIET-ROUTE)**<br>静音歩行の電池を配分し、危険な寄り道で情報を取る<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=quiet-route) · [遊び方を見る](QUIET-ROUTE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/relic-dive/title.png" width="300" alt="RELIC DIVE">](RELIC-DIVE) | **[RELIC DIVE](RELIC-DIVE)**<br>64×32マスの迷宮で食料・装備・魔法を使い、最深部の遺物を探す<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=relic-dive) · [遊び方を見る](RELIC-DIVE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/ruin-lexicon/title.png" width="300" alt="RUIN LEXICON">](RUIN-LEXICON) | **[RUIN LEXICON](RUIN-LEXICON)**<br>石板を回し、条件の一致を確かめる20の碑文<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=ruin-lexicon) · [遊び方を見る](RUIN-LEXICON) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/shadow-archive/title.png" width="300" alt="SHADOW ARCHIVE">](SHADOW-ARCHIVE) | **[SHADOW ARCHIVE](SHADOW-ARCHIVE)**<br>必要な調書を選び、少ない閲覧で解決する12事件<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=shadow-archive) · [遊び方を見る](SHADOW-ARCHIVE) |

### [経営・サバイバル](Genre-Management)

| タイトル画面 | ゲーム・概要 |
| --- | --- |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/auction-house/title.png" width="300" alt="AUCTION HOUSE">](AUCTION-HOUSE) | **[AUCTION HOUSE](AUCTION-HOUSE)**<br>大口入札・有料鑑定・見送りを使う3市場の競り<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=auction-house) · [遊び方を見る](AUCTION-HOUSE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/title.png" width="300" alt="CARGO BALANCE">](CARGO-BALANCE) | **[CARGO BALANCE](CARGO-BALANCE)**<br>先の荷物を読み、外側の高運賃と転覆を考える6航海<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=cargo-balance) · [遊び方を見る](CARGO-BALANCE) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/hearth-zero/title.png" width="300" alt="HEARTH ZERO">](HEARTH-ZERO) | **[HEARTH ZERO](HEARTH-ZERO)**<br>3夜の予報を読んで食料・薪・暖房を備える<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=hearth-zero) · [遊び方を見る](HEARTH-ZERO) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orchard-days/title.png" width="300" alt="ORCHARD DAYS">](ORCHARD-DAYS) | **[ORCHARD DAYS](ORCHARD-DAYS)**<br>雨と井戸を読み、早いベリーと高価なリンゴを育てる<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orchard-days) · [遊び方を見る](ORCHARD-DAYS) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/potion-path/title.png" width="300" alt="POTION PATH">](POTION-PATH) | **[POTION PATH](POTION-PATH)**<br>毒の着地点と限られた4材料を使う20の調合<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=potion-path) · [遊び方を見る](POTION-PATH) |
| [<img src="https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/tidal-nets/title.png" width="300" alt="TIDAL NETS">](TIDAL-NETS) | **[TIDAL NETS](TIDAL-NETS)**<br>深浅の流れを読み、細い網と広い網を使い分ける<br>[プレイ](https://zabaglione.github.io/pyjr100emu/?game=tidal-nets) · [遊び方を見る](TIDAL-NETS) |
