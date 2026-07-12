# PCGアニメーション

2×2文字のプレイヤーを、常駐PCGスロット4個だけで上下左右へ動かすサンプルです。方向ごとに2フレーム、合計8フレームの字形データを持ちますが、画面VRAMへ置くコードは常に`$80-$83`です。移動のたびに選択した32バイトを`$C000-$C01F`へ転送します。

## 操作

| キー | 動作 |
| --- | --- |
| `I` | 上へ移動 |
| `J` | 左へ移動 |
| `K` | 右へ移動 |
| `M` | 下へ移動 |

キーを押し続けると移動し、移動ごとに歩行フレームが切り替わります。

## ビルド

```sh
make -C samples/pcg_animation
```

生成物は`samples/pcg_animation/build/pcg_animation.prg`です。

## 再利用する箇所

- `ANIM_APPLY_FRAME`: `ANIM_SOURCE_PTR`が指す32バイトを常駐PCGへ転送
- `SELECT_PLAYER_FRAME`: 方向と歩行位相から`PLAYER_FRAME_POINTERS`の要素を選択
- `DRAW_PLAYER`: 画面へ常駐コード4個を2×2配置
- `src/player_frames.inc`: Web PCGエディタの「アニメーション」ASM出力と同じ、1フレーム4字形の配置

別の2×2キャラクターへ差し替える場合は、Web PCGエディタで先頭スロット0、2×2のクリップを作り、`LEFT_0`、`LEFT_1`、`RIGHT_0`、`RIGHT_1`、`UP_0`、`UP_1`、`DOWN_0`、`DOWN_1`の順でフレームを並べます。ASM出力ラベルを`PLAYER`にすると`PLAYER_FRAME_POINTERS`が生成されます。出力内容で`player_frames.inc`を置き換えれば、初期表示を含む選択処理を変更せずに差し替えられます。
