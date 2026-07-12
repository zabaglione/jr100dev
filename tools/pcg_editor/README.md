# JR-100 PCG Workbench

JR-100 のユーザー定義文字 32 スロットを編集する、依存ライブラリ不要の Web アプリです。各文字は 8×8 ドット・8 バイトで、`$C000-$C0FF` に対応します。

## 起動

リポジトリルートから次を実行します。

```sh
cd tools/pcg_editor
npm run serve
```

ブラウザーで `http://localhost:8000` を開きます。外部パッケージのインストールは不要です。

## 主な操作

- 左ドラッグ: ドットを描画
- 右ドラッグ: ドットを消去
- `1x1`、`2x2`、`3x3`: 連続スロットを一枚のキャンバスとして編集
- Saved group: 大型キャラクターの名前、寸法、先頭スロットをプロジェクトへ保存
- Pencil / Eraser / Line / Rectangle / Fill: 描画ツール切替
- Shift / Flip / Invert / Clear: 編集中キャンバス全体の変形
- Undo / Redo: ストロークまたは一括操作単位で復元
- Arcade Digit Preset: ATARI / NAMCO 系アーケードフォントを参考にした数字 0〜9 とコロンを11スロットへ配置
- ASM Output: 32文字・256バイトを `.byte` 形式でコピーまたはダウンロード
- Save JSON / Import: 編集プロジェクトを保存・復元

プロジェクトはブラウザーの `localStorage` にも自動保存されます。

## テスト

```sh
cd tools/pcg_editor
npm test
```

座標からPCGスロットへの変換、複合キャンバス境界、シフト、プリセット、JSON、アセンブリ出力をテストします。
