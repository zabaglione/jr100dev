# 日英ゲームガイド

公開先は https://zabaglione.github.io/pyjr100emu/guide/ です。51作品と共通操作を静的HTMLへ生成します。画像・動画は既存の公開素材を参照し、ゲーム本体を変更しません。

初回はブラウザーの優先言語が `ja` / `ja-*` なら日本語、それ以外は英語です。`?lang=en` / `?lang=ja` による指定を最優先し、手動選択を `jr100-guide-language` に保存します。保存できない場合もガイド内のリンクへ言語を引き継ぎます。JavaScriptが無効なら英語を表示します。

## 原稿と更新

- 日本語の原稿は `docs/wiki/`。共通ナビゲーションと紹介画像ブロックを除き、個別の遊び方をそのまま使います。
- 英語は `en/<game-id>.md` と `en/controls.md`。カタログの英語要約は `en/catalog.json` です。
- 共通操作と40面の評価・パスワード説明はビルド時に挿入します。PARの範囲は同じステージデータから生成します。
- `translation-sources.json` は翻訳時の日本語本文のSHA-256です。日本語を変えるとビルドを止め、英語の更新忘れを検出します。英語を修正・照合した項目だけ、下記の方法で記録を更新してください。

```sh
uv pip install --python .venv/bin/python -r docs/guide/requirements.txt
.venv/bin/python docs/guide/build.py /path/to/public-emulator/web/guide
.venv/bin/python -m pytest docs/guide/tests/test_build.py
node --test docs/guide/tests/language.test.cjs
```

生成先は専用の `guide/` ディレクトリを指定します。生成した53ページ、CSS、JavaScript、ライセンスだけを `manifest.json` に登録し、Web版の配布ビルドはこの一覧とハッシュを検証してコピーします。

翻訳を照合した後の記録更新例（対象だけ指定）：

```sh
.venv/bin/python docs/guide/review_translation.py frost-steps controls
```

公開時はソースとWeb版の差分をそれぞれ監査し、GitHub Pagesのデプロイ後に日英切替・保存・画像・起動リンクを確認します。Wikiは残し、各作品ページの冒頭から同じ作品のガイドへ案内します。
