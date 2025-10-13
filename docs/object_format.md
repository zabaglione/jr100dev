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
    {
      "name": "text",
      "kind": "code",
      "address": 32768,
      "content": "860139"
    }
  ],
  "symbols": [
    {"name": "START", "value": 32768, "scope": "global"}
  ],
  "relocations": [
    {
      "section": "text",
      "offset": 2,
      "type": "absolute16",
      "target": "LABEL",
      "addend": 0
    }
  ]
}
```

## 設計メモ
- `sections[*].content` は 16進（上記例）または Base64/BLOB などシリアライズしやすい形式でエンコードする。今後の `link` 実装で配列への復元を行う。
- `symbols` はラベルや `.equ` を含み、`scope` は `local`/`global` で将来の公開制御に備える。
- `relocations` は外部シンボル向けに生成される。現時点では未実装だが、リンク機能のフェーズで追加予定。
- `origin` と `entry_point` はアセンブル時点の値を保持する。リンク後に再配置・上書き可能。

## 次ステップ
1. `Assembler.assemble()` で `sections` と `relocations` の構造体を導入し、JSON 化を行うヘルパを実装する。
2. CLI で `--obj` オプションを受け取り、中間オブジェクトをファイル出力できるようにする。
3. リンカ（`jr100dev/link`）で JSON を読み込み複数オブジェクトを統合する処理を追加する。
