# 配布と公開

## 配布物を作る

```sh
.venv/bin/python games/dev.py release games/my_first_game --rom /path/to/owned-rom.prg
```

合格すると次の配置になります。作品名とバージョンは `game.json` から読みます。

```text
build/release/
  games/my-first-game/0.1.0/my-first-game.prg
  game-media/catalog.json
  game-media/my-first-game/
    index.html
    title.png / play.png / clear.png / ending.png
    play.mp4
    source.zip
    LICENSE.txt
    evidence.json
    manifest.json
```

画像名はリプレイによって変わります。`source.zip` はプロジェクトのソース、面・画像・音、操作テスト、README、設計書、Makefile、AGENTS.md だけを列挙して収めます。ビルドログ、ROM、録画途中のデータ、環境設定、SDK 外のファイルはコピーしません。新作のコードを失わないための同梱であり、SDK 一式の ZIP ではありません。再ビルドする人には、この SDK の対応リビジョンも伝えてください。

`manifest.json` は配布ファイルの SHA-256、`evidence.json` は操作と検証範囲です。PRG と動画が違う版だったり、テスト後にソースが変わっていたりすると配布物の作成を止めます。

## ローカル Web ディレクトリへ配置する

```sh
.venv/bin/python games/dev.py release games/my_first_game --rom /path/to/owned-rom.prg --web-root /path/to/web
```

指定したディレクトリへ必要なファイルを配置し、書き込み後の内容を照合します。同じ作品のカタログ項目は更新し、ほかの作品の項目とファイルは保持します。既存カタログが壊れていれば変更前に止めます。ファイルの書き込み中に失敗した場合は、この処理で変更したファイルを以前の内容へ戻します。公開サービスに対するトランザクションやネットワーク公開を保証するものではありません。

配置先はこのコマンドが書いてよい **Web 配信用ディレクトリ** を指定します。ROM を置いた私的ディレクトリや、SDK のソースルートを指定しないでください。既存の配布物に同名ファイルがあれば更新されます。

## 既存 Web エミュレーターの一覧への登録

単独プロジェクトは最初、PRG の手動ロードと紹介ページを使います。既存の pyjr100emu はゲーム一覧にあるソース URL を `https://github.com/zabaglione/jr100dev/tree/` 配下へ制限しています。新作のローカル ZIP パスをここへ入れると一覧全体を読み込めなくなるため、自動で入れません。

このリポジトリへ作品のソースを公開する場合は、`game.json` に実際の URL を設定してから `release` します。

```json
"sourceUrl": "https://github.com/zabaglione/jr100dev/tree/main/games/my_first_game"
```

この場合は `games/catalog.json` も生成・結合します。URL の設定だけでは GitHub にソースは公開されません。実際にその場所へ公開し、URL を確認してから案内してください。別のリポジトリを公開元にする場合は、エミュレーター側の URL 方針を別途変更する必要があります。

既存の `games/collection.json` / `library.json`、Wiki、51 作品の一括ガイドに載せる作業は別です。雛形の生成や Web 配置で勝手に「公開ゲーム数」を増やしません。

## インターネットへの公開後

利用している Web サーバーや Pages の手順で `build/release/` または配置先の変更を公開します。Git の commit / push、ホスティングのアカウント操作は、このツールの実行には含めません。公開するファイルを確認し、ROM、秘密情報、私的メモを含めないでください。

```sh
.venv/bin/python games/dev.py verify-published games/my_first_game --base-url https://example.org/jr100/
```

HTTP で PRG、画像、動画、ソース ZIP、ライセンス、紹介ページ、記録を取得し、ローカルのリリースとハッシュを比較します。共有カタログはファイル全体ではなく、その作品の項目を比較します。localhost の HTTP サーバーでも同じ確認ができます。

公開完了は push の成否だけで判断せず、公開 URL から必要なファイルが取得できることを確認します。紹介ページを開き、動画も再生してください。エミュレーター確認と、SS1・オリジナル JR-100 の実機確認は分けて記録します。
