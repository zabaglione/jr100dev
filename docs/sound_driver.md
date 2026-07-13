# 協調型サウンドドライバー

`sound.inc`はJR-100のVIA Timer 1によるPB7矩形波出力だけを使う、単音・固定音量のサウンドドライバーです。BGM用の割り込みやCPU PWMループは使用しません。Timer 1はこのドライバー専用です。

## 取り込みとAPI

```asm
        .include "sound.inc"
        .include "sound_assets.inc"

        JSR SOUND_INIT
        LDX #SOUND_BGM_TITLE
        JSR SOUND_PLAY_BGM

MAIN_LOOP:
        JSR SOUND_TICK
        ; Game update work.
        BRA MAIN_LOOP
```

全APIはA、B、X、CCRを破壊します。

| API | 入力 | 動作 |
| --- | --- | --- |
| `SOUND_INIT` | なし | PB7を出力化し、音声状態を停止する。 |
| `SOUND_PLAY_BGM` | X = BGM記述子 | 曲の先頭イベントをただちに再生する。 |
| `SOUND_TICK` | なし | ゲーム側の1更新分だけBGMを進める。 |
| `SOUND_PLAY_SFX_BLOCKING` | X = SFX記述子 | 最大500ms、ゲームを停止して効果音を再生する。 |
| `SOUND_STOP` | なし | BGMを停止し、PB7をLowにする。 |

`SOUND_TICK`はエディターの`SOUND_TICK_HZ`と同じ周期で、ゲーム側から必ず1回だけ呼びます。更新周期が変われば曲のテンポも変わります。

## データ形式

```asm
SOUND_BGM_TITLE:
        .word SOUND_BGM_TITLE_EVENTS
        .byte 3, 0
SOUND_BGM_TITLE_EVENTS:
        .byte $11, $06
        .byte $00, $03
        .byte $14, $06

SOUND_SFX_BLIP:
        .byte 2
        .byte $25, $01
        .byte $00, $01
```

BGM記述子はイベント列ポインタ、イベント数、ループ開始イベント番号です。最後の値が`$FF`なら曲末で停止します。各イベントは音高と継続tickです。音高0は休符、1から48はC3からB6です。

SFX記述子はイベント数の後に、音高と10ms単位の継続時間を並べます。ドライバーは実行時にも50単位で停止するため、不正な効果音データでも500msを超えてブロックしません。効果音中はBGMのtickを進めず、再生後に効果音直前のBGM音と残り時間を再開します。

## VIAの扱い

音高は`round(894886.25 / (2 × Hz)) - 2`で求めるTimer 1のリロード値です。周波数を変えるときはPB7出力を止めてからTimer 1の下位・上位バイトを順に書き、連続矩形波モードへ戻します。

`SOUND_WAIT_10MS`は、MB8861Hの`LDX #imm`が3サイクル、`DEX`と`BNE`が各4サイクル、`RTS`が5サイクルとして計算しています。カウント`$045D`では `3 + 1117 × (4 + 4) + 5 = 8944` サイクル、894kHz時に10.004msです。SFXの実時間上限は、この最悪値で50単位、500.3ms未満です。

ドライバーは`DDRB`のPB7だけを出力に加え、`ORB`のPB7と`ACR`のTimer 1モードビットだけを変更します。PB0からPB4のキーボード入力とPB5のPCG選択を維持します。Timer 1の割り込みを有効化しません。

## メモリ予算

`sound_demo`を現行ツールチェーンで組み立てた場合、サウンド本体の実行コードは345バイト、48音の周波数表は96バイト、作業領域は19バイトです。BGMは記述子4バイトに加えて圧縮後イベントあたり2バイト、SFXは先頭のイベント数1バイトに加えてイベントあたり2バイトを使います。

この構成は、ゲーム側の更新関数から短いサウンド処理を呼び、音高表と長さ・音高のイベント列だけを常駐させる設計です。曲の複雑さは主にイベント数へ反映され、通常フレームのCPU負荷や固定コード量は増えません。確認用PRG全体は1KiB未満を回帰条件とします。
