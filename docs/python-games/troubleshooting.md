# よくある失敗

コマンドは SDK ルートで実行します。まず `build/devkit/report.json` の段階を確認し、詳細は `run.log` を読みます。

| 症状 / コード | 原因 | 直す場所と再確認 |
| --- | --- | --- |
| `DEPENDENCY` | コンパイラー・エミュレーター・撮影ツール等が不足 | `doctor` の不足項目を導入し再実行。`JR100EMU_ROOT` は `cpp/src/` の親を含むチェックアウトへ |
| `SYNTAX` | インデント、括弧、コロンなどの誤り | 指定行の Python 構文を直して `check` |
| `LANGUAGE` | リスト、while、型注釈、256 以上など | `language.md` の対応構文に書き換えて `check` |
| `ENTRY` | init/act/tick/draw がない | 引数なしの 4 関数を定義。未使用なら `pass` |
| `CALL` | 関数名・引数数の誤り、キーワード引数 | API 表で確認し、位置引数へ直す |
| `NESTED_CALL` | 引数の中で別の関数を呼んだ | 内側の結果を先に作業変数へ代入 |
| `UNINITIALIZED` | 未代入の作業変数、分岐片側だけの代入 | 全経路で先に代入。永続状態なら init で s.name を初期化 |
| `STATE` | s.name の誤記、初期化忘れ | 状態名と init を確認 |
| `BOUNDS` / 配列 IndexError | 添字が 0〜127 等の範囲外 | 盤外・負の引き算・表の長さを確認。255 は普通の Python の -1 ではない |
| `DIVZERO` / ZeroDivisionError | 除数が 0 | 除算前に条件を付け、0 になるケースもテスト |
| `RECURSION` | 自己呼び出し、相互再帰、draw からの animate | 固定回数ループ等へ変更。演出は act/tick から |
| `LOOP` | ループ添字への代入、同じ添字の入れ子、動く上限 | 内側は別の添字にし、回数の計算をループ前に済ませる |
| `PROJECT` / `JSON` | メタデータ、面数、PCG、音の形式違い | 指定 JSON を直す。面数と levels、16×16 の行数、音の個数を照合 |
| `Code/data overlap display buffer` | コードと固定データが上限を超えた | layout と生成 ASM を調査。重複データ・長文・展開した処理を減らす |
| `Too many state/local bytes` | 状態と関数ローカルが多すぎる | 変数を減らす。RAM 上限を増やして解決しない |
| `REPLAY` | 入力列の結果、モデル、期待値の不一致 | 指定シナリオのステップを確認。ルールの誤りとテストの誤りを企画から判定 |
| `Reset needs an explicit test answer` | SPACE / 再挑戦で確認が開いた | ステップに `confirm: true` または `false` を指定 |
| `drawing outside screen` | 文字・タイル・数字が画面から出た | 座標に幅・高さを足して 32×24 内に収める |
| `CAPTURE_REPLAY` | 撮影中の実時間経過で期待した結果にならない | 入力猶予・時間制限・デモ経路を見直し、撮影を再実行 |
| `BASIC autostart did not enter the game` | ROM の形式・内容・エミュレーター起動が不適合 | 所有 ROM を既存エミュレーターで手動起動して確認。別 ROM に黙って代替しない |
| `stale` / ハッシュ不一致 | テスト・撮影・配布物が別の版 | 同じソースで `release` を最初から実行 |
| 公開ファイルのハッシュ違い | URL 間違い、古い配置、公開処理が未完了 | 配置先を確認し、公開完了後に `verify-published` |

`PIPELINE` は上表に分類されていない例外です。末尾の例外名だけで推測せず、`run.log` の該当行と直前の段階を確認してください。ツールの不具合を疑う場合は、エラー JSON、最小の再現ソース、Python / SDK / エミュレーターの版を添えて報告します。ROM や秘密情報は添付しません。

## やってはいけない復旧

- `build/game.asm` や生成 PRG を直接直して元ソースを放置する
- 失敗したテストを消して合格に見せる
- RAM、PCG、画面の上限を引き上げて「標準 16 KB」と説明する
- ROM なしの合成画面を実 ROM の撮影として公開する
- 撮影中に CPU の PC やゲーム RAM を書き換えてクリアする
- `sourceUrl` が存在しないのに公開完了と報告する
