# 中間オブジェクトフォーマット（草案）

## 目的
アセンブラの出力をリンク段階へ引き渡すための JSON ベース中間フォーマットを定義する。単一ソースを `assemble` した結果を `jr100dev/link` モジュールで再配置できるよう、セクション、シンボル、未解決参照を保持する。

## フォーマット概要
```json
{
  "format": "jr100dev-object",
  "version": 1,
  "source": "sample.asm",
  "origin": 32768,
  "entry_point": 32768,
  "sections": [
    {"name": "text", "kind": "code", "address": 32768, "content": "860139", "bss_size": 0},
    {"name": "BUFFER", "kind": "bss", "address": 33024, "content": "", "bss_size": 16}
  ],
  "symbols": [{"name": "START", "value": 32768, "scope": "global"}],
  "relocations": []
}
```

## 設計メモ
- `sections[*]` は `kind` と `bss_size` を持ち、`kind="bss"` の場合は `content` を省略し `bss_size` で未初期化領域を確保する。
- `symbols` はラベルや `.equ` を含み、`scope` は `local`/`global` で将来の公開制御に備える。
- `relocations` は外部シンボル向けに生成される（MVP は `absolute16` / `absolute8` / `relative8` をサポート）。
- `origin` と `entry_point` はアセンブル時点の値を保持する。リンク後に再配置・上書き可能。

## 次ステップ
1. リンカ（`jr100dev/link`）で JSON を読み込み複数オブジェクトを統合する処理を追加する。

## CLI からの生成例
```bash
jr100dev assemble src/main.asm -o build/main.prg --obj build/main.json
```
