# プロジェクト雛形の作成

## コマンド
```
jr100dev new mygame
```

### 生成される内容
- `jr100.toml`: 標準設定（MB8861H / 894 kHz）。
- `src/main.asm`: `.org $0300` から開始し、先頭で `JMP MAIN` でマクロ実装を飛ばした後、`.include "macro.inc"` とサンプル本体を配置。
- `std/macro.inc`: 標準マクロのコピー（必要に応じてカスタマイズ可能）。
- `build/`: 出力先ディレクトリ（空）。
- `.gitignore`: ビルド生成物 (`build/`, `*.bin`, `*.prg`) を除外。

> 詳細は `docs/project_structure.md` を参照。

## 次のステップ
1. `cd mygame`
2. `jr100dev assemble src/main.asm -o build/main.prg`
3. 生成された `build/main.prg` をエミュレーターで起動。
