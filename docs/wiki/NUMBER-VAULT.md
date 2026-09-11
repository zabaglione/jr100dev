# NUMBER VAULT

[ホーム](Home) → [パズル](Genre-Puzzle) → NUMBER VAULT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=number-vault) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/number_vault)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

1～4の4桁の暗証番号を、重複を含めて推理します。10回以内に正解すると次の金庫へ進みます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/title.png)

## 画面の奥行き

暗証番号のダイヤルと一致数の計器を厚い金庫の操作盤に配置しました。数字と選択矢印は読みやすさを優先しています。

## ゲーム専用フォント

**計器盤フォント**（角張った太線）を採用。タイトル／説明用に16文字、ゲーム用に28文字を割り当てています。ゲーム中の対象は `0123456789FOURDIALS/YMBEXCTN` です。空きPCG枠だけを使い、残りの文字は通常フォントで表示します。数字を変更する作品では0〜9を一式で揃えています。

## 操作と遊び方

A/Dで桁を選び、W/Sで数を変え、RETURNで試します。EXACTは数も位置も一致、NEARは数だけ一致した個数です。同じ数を重複して数えません。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

4つのダイヤル、EXACT・NEAR、試行残数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/number-vault/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,328 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/number_vault
make -C games/number_vault test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py number_vault --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
