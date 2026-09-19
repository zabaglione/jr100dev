# 全ゲームのソースコードと再ビルド

`src/` の有無だけでは、ソースコードが揃っているかを判断できません。このゲーム集では、手書きアセンブリと、Python形式のゲームロジックを機械語へ変換する方式を使っています。どちらもJR-100上ではMB8861Hの機械語として動作します。

## 編集するファイル

| 方式 | 作品数 | ゲーム本体 | ビルド方法 |
| --- | ---: | --- | --- |
| 手書きアセンブリ | 7 | 各作品の `src/*.asm` と `src/*.inc` | アセンブルしてPRGを生成 |
| Python形式のルール | 44 | 各作品の `rules.py` | 専用コンパイラーでアセンブリへ変換してからPRGを生成 |

ECHO PARRYのゲーム本体は [`echo_parry/rules.py`](echo_parry/rules.py) です。`src/` はありませんが、このファイルが再ビルドに使うソースです。ABYSS SIGNALは [`abyss_signal/src/`](abyss_signal/src/) にアセンブリを置いています。

Python形式の44作品のうち、PRISM TRACE、GATE RUNNER、STAR LANCE、PHASE PAIRSは描画処理などの追加アセンブリを `src/` に置いています。残る40作品は `src/` を必要としません。

## 共有コードと生成物

- [`build_game.py`](build_game.py) と [`toolchain.mk`](toolchain.mk): RELIC DIVEを除く50作品のビルド処理。各作品の `game.json` にある `nativeRules` と `modules` から入力を選びます。
- [`native/compiler.py`](native/compiler.py): `rules.py` と [`native/support.py`](native/support.py) をアセンブリへ変換します。Pythonの全機能に対応する汎用コンパイラーではありません。
- [`native/`](native/): Python形式の44作品で使う実行処理、描画、効果、アセット生成。基本の実行処理は [`runtime.asm`](native/runtime.asm)、面選択・星評価対応作品は [`campaign_runtime.asm`](native/campaign_runtime.asm) です。
- [`common/`](common/): 入力、画面、PCG、フォント、音などの共有コード。タイトルなどの定義には [`library.json`](library.json) も使います。
- [`../src/jr100dev/`](../src/jr100dev/): アセンブラとPRG生成などのツールチェーン。
- 各作品の `game.json`、`levels.json`、`world.json`、`cards.json` など: その作品が使う設定・面・カードなどのデータ。ファイルの構成は作品ごとに異なります。
- [`relic_dive/Makefile`](relic_dive/Makefile) と [`relic_dive/build_source.py`](relic_dive/build_source.py): RELIC DIVEのビルド処理。ソースの連結と文字列・タイトルの生成を行います。

各作品の `build/game.asm` は、共有コードや定数を組み込んだ生成物です。Python形式の作品では `build/rules.inc` も生成されます。これらはビルド時に作り直されるため、上記の入力ソースを編集してください。完成したPRGとBINも各作品の `build/` に出力されます。

共有コードが必要なので、ゲームのフォルダーだけでなくリポジトリ全体を取得してください。リポジトリのルートで次を実行します。

```sh
make -C games/echo_parry
make games
```

ビルドにはPythonとmakeが必要です。環境の準備と、追加のエミュレーターソースが必要な `test` の実行方法は [`README.md`](README.md#ビルド) を参照してください。

## 全51作品の配置

補助ソース欄は作品固有の描画・アセット生成などを示します。空欄の作品にも、上記の共有コードと各作品の設定・データが必要です。

| 作品 | ゲーム本体 | 描画・データ生成などの補助ソース |
| --- | --- | --- |
| [CHRONO BREACH](chrono_breach/) | [`src/`](chrono_breach/src/) | [`assets.py`](chrono_breach/assets.py) |
| [SIGIL DECK](sigil_deck/) | [`src/`](sigil_deck/src/) | [`assets.py`](sigil_deck/assets.py) |
| [ABYSS SIGNAL](abyss_signal/) | [`src/`](abyss_signal/src/) | [`assets.py`](abyss_signal/assets.py) |
| [TRACE BLADE](trace_blade/) | [`src/`](trace_blade/src/) | [`assets.py`](trace_blade/assets.py) |
| [DICE RELIC](dice_relic/) | [`src/`](dice_relic/src/) | [`assets.py`](dice_relic/assets.py) |
| [LOOP TEN](loop_ten/) | [`src/`](loop_ten/src/) | [`assets.py`](loop_ten/assets.py) |
| [IRON SCRIPT](iron_script/) | [`rules.py`](iron_script/rules.py) | [`presentation.py`](iron_script/presentation.py) |
| [CHAIN SUIT](chain_suit/) | [`rules.py`](chain_suit/rules.py) | [`presentation.py`](chain_suit/presentation.py) |
| [QUIET ROUTE](quiet_route/) | [`rules.py`](quiet_route/rules.py) |  |
| [CIRCUIT WORKS](circuit_works/) | [`rules.py`](circuit_works/rules.py) |  |
| [HEARTH ZERO](hearth_zero/) | [`rules.py`](hearth_zero/rules.py) |  |
| [NIGHT SWARM](night_swarm/) | [`rules.py`](night_swarm/rules.py) |  |
| [LUMEN CROSS](lumen_cross/) | [`rules.py`](lumen_cross/rules.py) |  |
| [MAGNET VAULT](magnet_vault/) | [`rules.py`](magnet_vault/rules.py) |  |
| [FROST STEPS](frost_steps/) | [`rules.py`](frost_steps/rules.py) |  |
| [PRISM TRACE](prism_trace/) | [`rules.py`](prism_trace/rules.py) | [`src/optics.asm`](prism_trace/src/optics.asm)、[`graphics.py`](prism_trace/graphics.py) |
| [TIDE BRIDGE](tide_bridge/) | [`rules.py`](tide_bridge/rules.py) | [`presentation.py`](tide_bridge/presentation.py) |
| [GLYPH SHIFT](glyph_shift/) | [`rules.py`](glyph_shift/rules.py) |  |
| [GRAVITY WELL](gravity_well/) | [`rules.py`](gravity_well/rules.py) |  |
| [SEED MERGE](seed_merge/) | [`rules.py`](seed_merge/rules.py) |  |
| [ORBIT DRAFT](orbit_draft/) | [`rules.py`](orbit_draft/rules.py) | [`presentation.py`](orbit_draft/presentation.py) |
| [FIVE FORGE](five_forge/) | [`rules.py`](five_forge/rules.py) | [`presentation.py`](five_forge/presentation.py) |
| [CORNER CROWN](corner_crown/) | [`rules.py`](corner_crown/rules.py) |  |
| [STONE BALANCE](stone_balance/) | [`rules.py`](stone_balance/rules.py) |  |
| [MEMORY MOSAIC](memory_mosaic/) | [`rules.py`](memory_mosaic/rules.py) |  |
| [TWENTY ONE](twenty_one/) | [`rules.py`](twenty_one/rules.py) |  |
| [ORBIT DODGE](orbit_dodge/) | [`rules.py`](orbit_dodge/rules.py) |  |
| [GATE RUNNER](gate_runner/) | [`rules.py`](gate_runner/rules.py) | [`src/scene.asm`](gate_runner/src/scene.asm)、[`presentation.py`](gate_runner/presentation.py) |
| [BRICK PULSE](brick_pulse/) | [`rules.py`](brick_pulse/rules.py) |  |
| [STAR LANCE](star_lance/) | [`rules.py`](star_lance/rules.py) | [`src/scene.asm`](star_lance/src/scene.asm)、[`presentation.py`](star_lance/presentation.py) |
| [RIBBON SNAKE](ribbon_snake/) | [`rules.py`](ribbon_snake/rules.py) |  |
| [LUNAR TOUCHDOWN](lunar_touchdown/) | [`rules.py`](lunar_touchdown/rules.py) |  |
| [ECHO PARRY](echo_parry/) | [`rules.py`](echo_parry/rules.py) |  |
| [PENDULUM PORT](pendulum_port/) | [`rules.py`](pendulum_port/rules.py) |  |
| [RUIN LEXICON](ruin_lexicon/) | [`rules.py`](ruin_lexicon/rules.py) |  |
| [SHADOW ARCHIVE](shadow_archive/) | [`rules.py`](shadow_archive/rules.py) |  |
| [COMPASS ROSE](compass_rose/) | [`rules.py`](compass_rose/rules.py) |  |
| [MIRROR RELIC](mirror_relic/) | [`rules.py`](mirror_relic/rules.py) |  |
| [ORCHARD DAYS](orchard_days/) | [`rules.py`](orchard_days/rules.py) |  |
| [TIDAL NETS](tidal_nets/) | [`rules.py`](tidal_nets/rules.py) |  |
| [POTION PATH](potion_path/) | [`rules.py`](potion_path/rules.py) |  |
| [AUCTION HOUSE](auction_house/) | [`rules.py`](auction_house/rules.py) |  |
| [METRO WEAVE](metro_weave/) | [`rules.py`](metro_weave/rules.py) | [`presentation.py`](metro_weave/presentation.py) |
| [CARGO BALANCE](cargo_balance/) | [`rules.py`](cargo_balance/rules.py) |  |
| [PEG GARDEN](peg_garden/) | [`rules.py`](peg_garden/rules.py) |  |
| [NUMBER VAULT](number_vault/) | [`rules.py`](number_vault/rules.py) |  |
| [PHASE PAIRS](phase_pairs/) | [`rules.py`](phase_pairs/rules.py) | [`src/hints.asm`](phase_pairs/src/hints.asm)、[`presentation.py`](phase_pairs/presentation.py) |
| [FUSE BOX](fuse_box/) | [`rules.py`](fuse_box/rules.py) |  |
| [SAND RESCUE](sand_rescue/) | [`rules.py`](sand_rescue/rules.py) | [`presentation.py`](sand_rescue/presentation.py) |
| [WORD FOUNDRY](word_foundry/) | [`rules.py`](word_foundry/rules.py) |  |
| [RELIC DIVE](relic_dive/) | [`src/`](relic_dive/src/) | [`build_source.py`](relic_dive/build_source.py)、[`pack_text.py`](relic_dive/pack_text.py)、[`title_art.py`](relic_dive/title_art.py) |

## 2026-09-19の確認結果

対象はコミット `6322478` の [`collection.json`](collection.json) に載る51作品です。`game.json` を持つ51ディレクトリとも一致し、一覧から漏れたゲームはありませんでした。

Git管理済みファイルだけを `git archive HEAD` で別ディレクトリに展開し、既存の `build/`、Pythonキャッシュ、未追跡ファイルを含めずに確認しました。ビルド用Pythonは3.12.11の新しい仮想環境で、追加パッケージをインストールせず、全作品で `make -C games/<directory> PYTHON=<その環境のpython>` を実行しました。

- 必要なゲーム本体・宣言済みアセンブリ・ビルド設定の欠落: 0件。すべてGit管理済みでした。
- 既存の生成物を使わない再ビルド: 51 / 51作品で成功。
- 再生成したPRGとBINの比較: どちらも元の作業ツリーにあった51作品すべてとバイト単位で一致。
- ECHO PARRYとABYSS SIGNAL: 同じ作業用コピーで `make ... test` に合格。ECHO PARRYの全6戦、ABYSS SIGNALの5記録回収と帰還を含む既存の入力リプレイを確認しました。

ソースの欠落がなかったため、補充・移動は行っていません。全51作品の結果は再ビルドの確認で、今回エミュレーター試験を実行したのは上記2作品です。実BASIC ROM経由の起動や実機確認は今回実施していません。
