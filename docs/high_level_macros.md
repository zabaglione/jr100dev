# 高レベルマクロ利用ガイド

`jr100dev/std/ctl.inc` で提供する制御構造・算術マクロの使い方をまとめる。

## 取り込み

```asm
        .include "macro.inc"
        .include "ctl.inc"
```

- `macro.inc` と併用することで VRAM 出力や I/O マクロと組み合わせて記述できる。
- マクロ中で使用するラベル（`FOR0_TOP` など）はユーザーが一意に命名する必要がある。

## 変数宣言

| マクロ | 展開 | 例 |
| --- | --- | --- |
| `VAR8 name, init` | `.byte init` | `VAR8 LOOP_I, 0` |
| `VAR16 name, init` | `.word init` | `VAR16 PTR, $0300` |
| `VARZ name, size` | `.res size` | `VARZ BUFFER, 32` |

これらは `.data` / `.bss` セクションと併用できる。制御構造マクロと干渉しないようサンプルでも `.data` ブロック内にまとめて宣言する。

## 8bit 算術ヘルパー

- `ADD8 target, value` → `LDA target; ADDA value; STA target`
- `SUB8 target, value` → `LDA target; SUBA value; STA target`
- `INC8 target` → `INC target`
- `DEC8 target` → `DEC target`

`value` に即値を渡す場合は `#` を付与する。メモリアドレスも指定可能。

## 制御構造

### FOR ループ

```asm
FOR_BEGIN LOOP0_TOP, LOOP0_END, LOOP_I, 0, 9
        ; ループ本体
FOR_END LOOP0_TOP, LOOP0_END, LOOP_I
```

- ループ変数 `LOOP_I` を `start` で初期化し、`limit` 以上になると `LOOP0_END` へジャンプする。
- ネストする場合はラベル名を変えて使用する。

### WHILE ループ

```asm
WHILE_BEGIN LOOP1_TOP
        LDAA FLAG
        WHILE_IF_ZERO LOOP1_END, FLAG
        ; 本体
WHILE_END LOOP1_TOP, LOOP1_END
```

- 条件は利用者側で計算し、`WHILE_IF_ZERO` はゼロならループを抜ける。

### IF 文

```asm
IF_EQ IF0_END, LAST_KEY, $01
        BEEP
IF_END IF0_END
```

- `IF_NE` も利用可能（等しければ飛ばす）。他の条件は `CMPA` との組み合わせで表現する。

## サンプル

- `samples/io_demo/main.asm` : FOR/WHILE/IF と VRAM・サウンド・キースキャンマクロを組み合わせた例。
- `samples/counter/main.asm` : FOR マクロで 0-9 を描画し、キー入力でリセットする最小サンプル。

## テスト

- `pytest jr100dev/tests/unit/test_ctl_macros.py`
