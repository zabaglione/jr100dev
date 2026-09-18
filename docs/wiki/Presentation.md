# 動きと音の紹介

[ホーム](Home) · [操作・起動方法](Controls)

**[全51作品のプレイ動画ギャラリー](https://zabaglione.github.io/pyjr100emu/gameplay.html)**

全作品の紹介ページに、開始・進行・目標達成の3枚以上の画像を並べ、その後に音付き動画へのリンクを掲載しています。動画を見るだけならROMは不要です。

[今回の35作品の改善内容と、これまでの指摘の要点](Quality-Review)

2026年9月18日の更新で、タイトルの立体感と、動き・効果音・結果を見届ける間を加えました。ゲームに合わせ、短い演出を使い分けています。

![開始、移動、被弾、石返し、撃破の実画面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/presentation/presentation.gif)

**[音付き動画を見る（24秒）](https://zabaglione.github.io/pyjr100emu/presentation.html)**。GIFには音がありません。動画はエミュレーターで実行したゲーム画面と音声です。

| 動画の場面 | 見どころ | 遊ぶ |
| --- | --- | --- |
| 0〜5秒：MAGNET VAULT | 地形やキャラクターが順に現れ、GAME STARTで開始。ロボットと金属塊は途中の位置を通って移動します。 | [プレイ](https://zabaglione.github.io/pyjr100emu/?game=magnet-vault) · [遊び方](MAGNET-VAULT) |
| 5〜11秒：ECHO PARRY | 被弾した対象が点滅し、短い停止と音で失敗を知らせます。敵の撃破には破片の演出があります。 | [プレイ](https://zabaglione.github.io/pyjr100emu/?game=echo-parry) · [遊び方](ECHO-PARRY) |
| 11〜19秒：CORNER CROWN | 挟んだ石が一枚ずつ回転。面が細くなり、側面を経て反対の面が開きます。 | [プレイ](https://zabaglione.github.io/pyjr100emu/?game=corner-crown) · [遊び方](CORNER-CROWN) |
| 19〜24秒：STAR LANCE | 倒した敵が発光し、中心から外側へ破片が散って消えます。 | [プレイ](https://zabaglione.github.io/pyjr100emu/?game=star-lance) · [遊び方](STAR-LANCE) |

## 石が返る途中の形

![石の面が狭まり、側面を経て反対の面が開く七段階](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/presentation/disc-turn.png)

白から黒、黒から白の両方向に回転します。ほかの石はそのまま盤面に残り、返る石だけが動きます。

## 開始・被弾・結果の間

開始演出が終わってから操作を受け付けます。被弾した場所や失敗した理由を確認できるよう、音と短い停止を挟みます。成功・失敗の結果はジングルが終わるまで表示し、その後にキーを押し直すと進めます。

同じブラウザーに自分のBASIC ROMを登録してから、各作品の「プレイ」を押してください。音が出ない場合はゲーム画面をクリックするか、キーを押してください。ROMは配布物に含みません。実機での動作・音声は未確認です。
