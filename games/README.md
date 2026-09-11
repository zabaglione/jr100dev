# JR-100 Games

標準RAM 16KBで動く独立したゲームです。教材用の`samples/`とは分けて管理します。

| ゲーム | 内容 | 状態 |
| --- | --- | --- |
| [CHRONO BREACH](chrono_breach/) | 動くときだけ時間が進む20面の戦術パズル | 1.0.0、エミュレーター確認済み・実機未確認 |
| [SIGIL DECK](sigil_deck/) | 24種のカードで構築する10戦のバトル | 1.0.0、エミュレーター確認済み・実機未確認 |
| [ABYSS SIGNAL](abyss_signal/) | 海底の5地点を観測して帰還する探索ゲーム | 1.0.0、エミュレーター確認済み・実機未確認 |
| [TRACE BLADE](trace_blade/) | 一筆の経路で連続撃破する30面のパズル | 1.0.0、エミュレーター確認済み・実機未確認 |
| [DICE RELIC](dice_relic/) | ダイスの面を作り替える9戦のバトル | 1.0.0、エミュレーター確認済み・実機未確認 |
| [LOOP TEN](loop_ten/) | 10秒の巻き戻しを使う12部屋の探索パズル | 1.0.0、エミュレーター確認済み・実機未確認 |

今後の候補は[開発計画](../docs/public-games-plan.md)を参照してください。

## ビルド

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

`common/`は入力、PCG・文字描画、画面復帰、単音の効果音・BGMを提供します。VIA Timer 1を音、Timer 2を更新に使います。入力は描画中も読み、次の1操作を保持します。BGMと効果音の同時発音はせず、重要な効果音を優先します。

ターン制の5作品はTimer 2を約60Hzでポーリングします。LOOP TENは別の時計処理でカウンターの差分を積算し、描画中の時間も数えます。CPUクロックによる10秒の計測結果は作品の説明を参照してください。

`package_games.py <destination>`はビルド済みの自作PRGとライセンスだけをコピーし、版・SHA-256・RAM条件を持つ`catalog.json`を作ります。公開エミュレーターの`web/games/`への取り込みに使います。

このディレクトリのオリジナルコード・画像・曲・文章は[MIT License](LICENSE)です。BASIC ROMは含みません。

WASM配布物での起動確認は `node games/tests/wasm_launch.mjs <emulator-checkout> <owned-rom>` で実行できます。ブラウザーUIを操作せず、配布用WASMへ実ROM・PRGを読み込み、タイトル、標準16KB、開始入力、PCM出力を確認します。
