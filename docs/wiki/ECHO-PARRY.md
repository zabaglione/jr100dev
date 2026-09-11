# ECHO PARRY

[ホーム](Home) → [アクション](Genre-Action) → ECHO PARRY

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/echo_parry)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

相手の予備動作を読み、攻撃に合わせて8回の反撃を成功させます。3回のミスで決闘に敗れます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/title.png)

## 画面の奥行き

対戦場に奥へ向かう床線と手前の段差を付け、剣士と盾に厚みを加えました。上段・下段と反撃の合図は従来の位置に表示します。

## ゲーム専用フォント

**スピードフォント**（右へ傾く太線）を採用。タイトル／説明用に16文字、ゲーム用に20文字を割り当てています。ゲーム中の対象は `0123456789THECOKNIG>` です。空きPCG枠だけを使い、残りの文字は通常フォントで表示します。数字を変更する作品では0〜9を一式で揃えています。

## 操作と遊び方

Wで上段、Sで下段の構えを選び、攻撃中にRETURNで受け流します。予備動作と立て直しの間は待ちます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。

相手の攻撃位置、盾の高さ、攻撃段階、成功数を表示します。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/echo-parry/play-02.png)

## ビルドと検証

バージョン 1.2.0。開始番地 `$0300`、ゲーム本体と定数は 6,093 bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。

```sh
make -C games/echo_parry
make -C games/echo_parry test
```

出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。

キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。

```sh
.venv/bin/python games/native/replay.py echo_parry --rom /path/to/owned-rom.prg --capture --keyboard
```

タイトルには長めの単音曲、プレイ中には効果音を付けています。ソース・画像・曲は[MIT License](https://github.com/zabaglione/jr100dev/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。
