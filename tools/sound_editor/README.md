# JR-100 Sound Workbench

Timer 1のPB7矩形波を使う、単音BGMと最大500msのブロッキング効果音を編集するWebアプリです。BGMはゲーム側が指定周期で`SOUND_TICK`を呼ぶ協調更新方式で、効果音中はゲームとBGMの進行を停止します。

## 起動

```sh
cd tools/sound_editor
npm run serve
```

`http://127.0.0.1:8001`を開きます。サーバーはローカルホストだけで待受し、外部ライブラリは使用しません。

初期表示は日本語です。ヘッダー右上の表示言語でEnglishへ切り替えられ、選択はブラウザーに保存されます。

日本語の表示文字列は、利用者から明示された「日本語を既定にし英語にも対応する」要件のためのUI資源です。ダウンロードされる`sound_assets.inc`、PRG、BIN、MAPは従来どおりASCII英語ラベルだけを出力します。

## 操作と出力

- BGMとSFXを左側の一覧から選び、ピアノロールを左クリックして音を置く。右クリックは休符。
- BGMのセルはプロジェクトの`Game tick Hz`と`BGM grid ticks`で決まる。ゲーム側は同じ周期で`SOUND_TICK`を1回呼ぶ。
- SFXのセルは10msで、最大50セルである。SFXを再生している間はゲームを停止する。
- `Download sound_assets.inc`はゲームに取り込むアセンブリデータを出力する。
- `Build demo PRG`は選択プロジェクトの資産を含む確認用PRG、BIN、MAP、INCをZIPで出力する。既存ゲームのファイルは変更しない。

初期プロジェクトの2曲はパブリックドメインの原曲を基にした独自の単音縮約です。来歴と利用方針は[`docs/sound_samples.md`](../../docs/sound_samples.md)を参照してください。

UIの確認観点と自動回帰の範囲は[`UX_VERIFICATION.md`](UX_VERIFICATION.md)に記録しています。

## テスト

```sh
npm test
```
