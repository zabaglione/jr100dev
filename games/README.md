# JR-100 Games

標準RAM 16KB向けの独立したオリジナルゲーム51作品です。教材用の `samples/` とは分けて管理します。

新しくゲームを作る場合は[Python ゲーム開発キット](../docs/python-games/README.md)を使います。雛形の初期化から検査・テスト・撮影・配布までの共通入口は `games/dev.py` です。

[Wikiのジャンル別一覧](https://github.com/zabaglione/jr100dev/wiki) · [共通操作](https://github.com/zabaglione/jr100dev/wiki/Controls)

## パズル

| ゲーム | 内容 |
| --- | --- |
| [TRACE BLADE](trace_blade/) | 一筆の経路を計画して連続撃破する |
| [LUMEN CROSS](lumen_cross/) | 反転範囲を読み、最短回数を狙う18面の消灯パズル |
| [MAGNET VAULT](magnet_vault/) | 押せない金属塊を磁力で引いて収納する。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。 |
| [FROST STEPS](frost_steps/) | 氷上を止まれず滑り、全結晶を拾う。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。 |
| [PRISM TRACE](prism_trace/) | 鏡の向きを変えて光を受光器へ導く |
| [TIDE BRIDGE](tide_bridge/) | 潮位の連動する橋を切り替えて渡る |
| [GLYPH SHIFT](glyph_shift/) | 物体の通行ルールを書き換えて脱出する。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。 |
| [GRAVITY WELL](gravity_well/) | 盤面を傾けて複数の球を同時に収める。40面・規定手数と任意ルーンによる3段階評価・パスワード対応。 |
| [SEED MERGE](seed_merge/) | 同じ芽を合成して大樹を育てる |
| [PEG GARDEN](peg_garden/) | 飛び越しで石を取り除く庭園パズル |
| [NUMBER VAULT](number_vault/) | 推理の履歴を読み、動く扉を開く暗証番号パズル |
| [PHASE PAIRS](phase_pairs/) | 隣り合う数を10にして盤面を消す |
| [FUSE BOX](fuse_box/) | 行と列の個数を読んで配線図を復元する |
| [WORD FOUNDRY](word_foundry/) | 中継単語を経由して辿る16の単語迷路 |

## カード・ボード

| ゲーム | 内容 |
| --- | --- |
| [SIGIL DECK](sigil_deck/) | カードを組み合わせて虚空の王を封じる |
| [DICE RELIC](dice_relic/) | 出目を使い、ダイスの面そのものを鍛える |
| [CHAIN SUIT](chain_suit/) | 手札交換と役の選択で得点ノルマに挑む |
| [ORBIT DRAFT](orbit_draft/) | 4×4・5種類の天体を、候補2枚と次の3枚を読んで揃える。回転と落下連鎖で得点を伸ばすエンドレスパズル |
| [FIVE FORGE](five_forge/) | 妨害と四連の脅威を読む五目対戦 |
| [CORNER CROWN](corner_crown/) | 挟み取りと角の支配を競う盤面対戦 |
| [STONE BALANCE](stone_balance/) | 最後の石が勝ちから負けへ変わる10局の取り合い |
| [MEMORY MOSAIC](memory_mosaic/) | 札の厚みと5段階の反転で遊ぶ10面の神経衰弱 |
| [TWENTY ONE](twenty_one/) | 52枚の山札とダブルを使い7勝負の収支を競う |

## 戦術・自動化

| ゲーム | 内容 |
| --- | --- |
| [CHRONO BREACH](chrono_breach/) | 弾道を読んで突破する20面の時間停止戦術 |
| [IRON SCRIPT](iron_script/) | 射撃・スイッチ・繰り返しの命令で24の工場を攻略 |
| [CIRCUIT WORKS](circuit_works/) | 配線を流れる0/1を見ながら組む22の論理回路 |
| [METRO WEAVE](metro_weave/) | 分岐と信号で複数列車をさばき、混雑を読んで急行を増発する |
| [SAND RESCUE](sand_rescue/) | 限られた水を6つの畑へ配分し、安全な収穫と追加の実りを選ぶ |

## アクション

| ゲーム | 内容 |
| --- | --- |
| [NIGHT SWARM](night_swarm/) | 補給へ踏み込む判断と装甲戦を加えた6夜の生存戦 |
| [ORBIT DODGE](orbit_dodge/) | 2軌道を渡り、同時光線と連続回収に挑む6面 |
| [GATE RUNNER](gate_runner/) | 横位置を細かく調整し、壁・全幅の穴・低い梁を越える疑似3Dランニング |
| [BRICK PULSE](brick_pulse/) | 装甲ブロック・アイテム・ドローンに挑む12面のブロック崩し |
| [STAR LANCE](star_lance/) | 攻撃予告を撃ち落として冷却。回避と熱管理で突破する6波の宇宙戦 |
| [RIBBON SNAKE](ribbon_snake/) | 岩の庭で逃げ道を作り、3回のブレーキを使う |
| [LUNAR TOUCHDOWN](lunar_touchdown/) | 横風と燃料を読み、狭い着陸場の追加点を狙う |
| [ECHO PARRY](echo_parry/) | フェイントを見抜き、後退と遅い受け流しを使い分ける |
| [PENDULUM PORT](pendulum_port/) | ロープ長と振りを合わせ、中央着地を狙う6区間 |

## 探索・アドベンチャー

| ゲーム | 内容 |
| --- | --- |
| [ABYSS SIGNAL](abyss_signal/) | ソナーと酸素計を頼りに海底遺構を観測 |
| [LOOP TEN](loop_ten/) | 10秒の巻き戻しを越えて12の封印を解く |
| [QUIET ROUTE](quiet_route/) | 静音歩行の電池を配分し、危険な寄り道で情報を取る |
| [RUIN LEXICON](ruin_lexicon/) | 石板を回し、条件の一致を確かめる20の碑文 |
| [SHADOW ARCHIVE](shadow_archive/) | 必要な調書を選び、少ない閲覧で解決する12事件 |
| [COMPASS ROSE](compass_rose/) | 測定する場所を選び、方角と距離帯から探し当てる |
| [MIRROR RELIC](mirror_relic/) | 左右の鏡回転と位相を合わせる6つの遺跡 |
| [RELIC DIVE](relic_dive/) | 64×32マスの迷宮で食料・装備・魔法を使い、最深部の遺物を探す |

## 経営・サバイバル

| ゲーム | 内容 |
| --- | --- |
| [HEARTH ZERO](hearth_zero/) | 3夜の予報を読んで食料・薪・暖房を備える |
| [ORCHARD DAYS](orchard_days/) | 雨と井戸を読み、早いベリーと高価なリンゴを育てる |
| [TIDAL NETS](tidal_nets/) | 深浅の流れを読み、細い網と広い網を使い分ける |
| [POTION PATH](potion_path/) | 毒の着地点と限られた4材料を使う20の調合 |
| [AUCTION HOUSE](auction_house/) | 大口入札・有料鑑定・見送りを使う3市場の競り |
| [CARGO BALANCE](cargo_balance/) | 先の荷物を読み、外側の高運賃と転覆を考える6航海 |

## ビルド

ソースの配置には2通りあります。ABYSS SIGNALなど7作品は `src/` のアセンブリ、ECHO PARRYなど44作品は各ゲーム直下の `rules.py` がゲーム本体です。後者のうち4作品には追加のアセンブリを収めた `src/` もあります。`src/` がない40作品も、`rules.py` と共有コードから再ビルドできます。編集するファイルと共有コードは[全ゲームのソース一覧](SOURCES.md)にまとめています。

以下のコマンドは、リポジトリのルートで実行します。各ゲームは `common/`、`native/`、リポジトリ直下の `src/jr100dev/` も参照するため、リポジトリ全体を取得してください。

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
make games
```

生成PRGは各ゲームの`build/`に出力します。ゲームの実行にはJR-100本体またはBASIC ROMを設定したエミュレーターが必要です。

## 検証

Python・C++20コンパイラーと[JR-100 emulator](https://github.com/zabaglione/pyjr100emu)のソースが必要です。

```sh
git clone https://github.com/zabaglione/pyjr100emu.git external/jr100emu
JR100EMU_ROOT="$PWD/external/jr100emu" make games-test
```

画面取得を行う場合は、追加で `python -m pip install -r games/requirements-qa.txt` を実行してください。

この検証は合成ROMを使うCPU・入力リプレイ試験です。実BASIC経由の起動と実画面の取得は、各作品の説明にある所有ROMを使うコマンドで別に行います。

## 共通処理

`common/`は入力、PCG・文字描画、画面復帰、単音の効果音・BGMを提供します。VIA Timer 1を音、Timer 2を更新に使います。通常の描画中は次の1操作を保持します。開始・被弾・連続移動・結果ジングルの演出中は追加入力を捨て、意図しない次の操作を防ぎます。BGMと効果音の同時発音はせず、重要な効果音を優先します。

開始時にはSEと中央の`GAME START`表示を挟み、地形やキャラクターの段階表示を適する作品に加えています。被弾時はその場を短く止め、失敗理由と結果ジングルを表示します。CORNER CROWNは石を一枚ずつ返し、FIVE FORGEは自分と相手の着手を順に見せます。

タイトルにはセミグラフィックスとPCGによる側面の網点を使い、8作品ではキャラクターの向きに合わせて4文字分のPCGをその場で更新します。対象作品、共有PCGの制約、検証手順は[画面と演出の実装記録](../docs/game-presentation.md)を参照してください。

共通処理はTimer 2を約60Hzでポーリングします。LOOP TENは別の時計処理でカウンターの差分を積算し、描画中の時間も数えます。CPUクロックによる10秒の計測結果は作品の説明を参照してください。

`package_games.py <destination>`はビルド済みの自作PRGとライセンスだけをコピーし、版・SHA-256・RAM条件を持つ`catalog.json`を作ります。公開エミュレーターの`web/games/`への取り込みに使います。

このディレクトリのオリジナルコード・画像・曲・文章は[MIT License](LICENSE)です。BASIC ROMは含みません。

WASM配布物での起動確認は `node games/tests/wasm_launch.mjs <emulator-checkout> <owned-rom>` で実行できます。ブラウザーUIを操作せず、配布用WASMへ実ROM・PRGを読み込み、タイトル、標準16KB、開始入力、PCM出力を確認します。

`native/` は新作44本のコンパイラー、画面構成、共通実行処理、ルール検査と全編リプレイを収めます。作品固有のルールと地形は各作品のディレクトリにあります。4方向はWASD、8方向はQWE／AD／ZXCです。
