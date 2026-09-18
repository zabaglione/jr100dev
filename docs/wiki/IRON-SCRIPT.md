# IRON SCRIPT

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → IRON SCRIPT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=iron-script) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/iron_script)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

移動・射撃・スイッチ操作・繰り返しを組み合わせ、ロボットをダイヤ形の端末へ導く24ステージのプログラミングパズルです。最大12枠の命令と限られた弾数で、警備ロボット、扉、周期レーザーを突破します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/demo-clear.png)

**[音付きプレイ動画を見る（約31秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=iron-script)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで命令枠を選び、W/Sで命令を変更します。RETURNで最初の枠から実行し、実行中のRETURNで停止します。失敗や停止の後も命令列は残り、修正してRETURNを押すと、位置・敵・扉・弾数をその面の開始状態へ戻して再実行します。SPACEでやり直す場合は命令列も消去します。

| 命令 | 動作 |
| --- | --- |
| ↑ ↓ ← → | 指定方向を向き、1マス移動します。方向にはJR-100のグラフィック文字を使用しています。 |
| .（WAIT） | その場で1動作待ち、レーザーの周期を合わせます。 |
| F（FIRE） | DIRの方向へ1発撃ちます。最初に当たった敵へ1ダメージ。壁と閉じた扉で弾が止まります。 |
| U（USE） | スイッチの上で、すべての扉を開閉します。 |
| L（LOOP） | 直前の2枠を、同じ順でもう一度実行します。たとえば「→ → L」で4マス進みます。先頭2枠、または直前2枠にLがある場合は使えません。 |

命令枠は左から右、上から下へ実行します。A・B・Cは10〜12番目の枠です。PROGRAMは使用可能な枠数で、Xの枠は使えません。面によって6〜12枠となり、繰り返しで命令を短くする必要があります。途中で端末に着けば、残りの命令は実行せずクリアです。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

ロボットは矢印の方向を向き、マスの中間を通って移動します。扉は途中の開き方を挟んで開閉し、弾が前方へ飛びます。装甲敵は1発目で点滅して装甲が外れ、撃破時は4段階で消滅します。各動作にSEがあり、失敗時は原因と該当する命令枠を残して停止します。演出が終わってから次のキーを押してください。

AMMOは残弾、DIRは射撃する向き、DOORは扉の開閉状態、STEPSは実行した動作数です。Lは1枠で2動作を実行します。編集画面では時間を止めて考えられます。

レーザーは1動作ごとに点灯・消灯が切り替わります。NEXT LASERは次の動作後の状態で、ON!になる動作ではレーザーのマスに残れません。WAITや射撃も1動作です。2本の光線が点灯中、点だけの床が消灯中のレーザーです。

警備ロボットは進路を塞ぎ、接触すると停止します。通常の敵は1発、「2」付きの装甲敵は2発で倒せます。向きを変えるにはその方向へ移動するため、射撃位置と残弾を先に考えます。敵をすべて倒す必要はなく、弾が足りないときは迂回も選べます。

1〜4面は扉と射撃、5〜8面はレーザーの周期、9〜12面は繰り返し、13〜16面は射撃位置と迂回、17〜20面は仕掛けの組み合わせ、21〜24面は命令枠と弾数を使う総合課題です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/iron-script/play-02.png)
