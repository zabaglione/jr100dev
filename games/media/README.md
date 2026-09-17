# 紹介画像とプレイ動画

各ゲームの `images/` に、開始・進行・目標達成の3枚と、約30秒の `play.mp4` を置きます。既存のタイトル画像や解説画像も残します。

動画は所有するBASIC ROMからPRGを起動し、通常のキー入力で進めた自動リプレイです。判断の間と入力間隔を設け、CPUは894 kHz、動画は30 fps、音はエミュレーターが出力したPCMです。CPUやRAMを書き換えてクリアを作ることはありません。

原則として最初のステージをクリアするまでを収録します。戦闘ゲームは初戦、RELIC DIVEは最初の階の踏破を区切りとします。短いLUNAR TOUCHDOWNとLOOP TENは2ステージ分です。長いゲームは途中を省略し、切り替わった直後にLATERを表示します。再生速度は変えません。

`play.json` は入力時刻、クリア時刻、編集に使った区間、PRGのSHA-256、ホストからの状態書き換え回数を記録します。ROM・ローカルパスは保存しません。

```sh
.venv/bin/python games/media/capture.py --rom /path/to/owned-rom.prg --work /tmp/jr100-demo
.venv/bin/python games/write_library_docs.py
.venv/bin/python games/media/verify.py --output /tmp/jr100-demo-review
.venv/bin/python games/media/package.py /path/to/public-emulator/web/game-media
```

作品名を指定すれば、その作品だけ再録画できます。`--reencode` は保存済みの実フレーム・PCM・入力記録から再編集します。必要なツールはC++20コンパイラ、JR-100エミュレーターのC++ソース、Pillow、ffmpeg、ffprobeです。

公開先は[動画ギャラリー](https://zabaglione.github.io/pyjr100emu/gameplay.html)と各作品のWikiです。動画はROMなしで見られます。実機での動作・音声は未確認です。
