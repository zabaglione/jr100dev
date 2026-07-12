# 詳細ドキュメント

`rules/`がJR-100開発時の判断基準であるのに対し、このディレクトリはツールチェーンの仕様と個別サンプルの設計詳細を扱います。

## ツールチェーン

- [`project_structure.md`](project_structure.md): リポジトリと生成プロジェクトの構成
- [`project_quickstart.md`](project_quickstart.md): `jr100dev new`で始める手順
- [`std_macros.md`](std_macros.md): VRAM、キー、簡易ビープなどの標準マクロ
- [`high_level_macros.md`](high_level_macros.md): 制御構造と算術マクロ
- [`object_format.md`](object_format.md): JSON中間オブジェクト形式
- [`prg_packaging_notes.md`](prg_packaging_notes.md): `.prg`梱包形式
- [`opcode_sync_workflow.md`](opcode_sync_workflow.md): MB8861H命令表の同期方法

## サンプル設計

- [`maze_design.md`](maze_design.md): 現在のmazeサンプルの構成とアルゴリズム
- [`maze_sample_notes.md`](maze_sample_notes.md): maze開発時の実装・デバッグ記録

## 過去の記録

完了したMVP計画や、現在は存在しない試作サンプルの文書は[`archive/`](archive/)へ分離しています。現在の構成や開発ルールとして参照しないでください。
