# 命令抽出・同期ワークフロー（ドラフト）

## 概要
`tools/sync_opcodes.py` は `pyjr100emu` の CPU 実装から MB8861H 命令セットを抽出し、`jr100dev/asm/opcodes_mb8861h.py` と JSON マニフェストを自動生成する。

## 使い方
```bash
gh repo clone zabaglione/pyjr100emu external/pyjr100emu
python tools/sync_opcodes.py \
  --emu-root external/pyjr100emu \
  --output jr100dev/asm/opcodes_mb8861h.py \
  --json build/opcodes.json
```
- `external/pyjr100emu` は `pyjr100emu` のチェックアウト先の一例。
- `--output` を省略すると `jr100dev/asm/opcodes_mb8861h.py` に上書きする。
- `--json` を指定すると同じ内容を JSON マニフェストとして出力する（差分確認や CI ログ向け）。

## 現在の実装状況とタスク
- AST 解析で `MB8861` クラスの `OP_*` 定数、`_register_opcode` 呼び出し、オペランド長を自動抽出済み。
- `jr100dev/tests/opcodes/test_opcode_table.py` で `external/pyjr100emu` と同期を検証。
- CI での自動チェック、複数エミュレーターサブモジュール対応などは今後の拡張として検討する。
