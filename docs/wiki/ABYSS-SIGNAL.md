# ABYSS SIGNAL

[ホーム](Home) → [探索・アドベンチャー](Genre-Exploration) → ABYSS SIGNAL

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=abyss-signal) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/abyss_signal)

同じブラウザーでBASIC ROMを事前に登録してください。

標準RAM 16KBのJR-100向け海底探索ゲーム。32×32セルの海域で5つの観測地点を記録し、基地へ帰還します。ソナーで視界を広げながら、海流、岩礁、音を追う生物を避けてください。発見した遺構には、それぞれ専用の観測画面があります。

![Title](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/demo-clear.png)

**[音付きプレイ動画を見る（約102秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=abyss-signal)**

5つの記録を回収し、基地へ帰還するまでを収録。

## 操作

| 操作 | キーボード | 1ボタンパッド |
| --- | --- | --- |
| 移動 | W/A/S/D | 上下左右 |
| 操作パネル／決定 | RETURN | ボタン |
| パネル選択 | W/S | 上下 |
| パネルを閉じる | SPACE | 項目を実行 |
| ソナー／待機 | F／X | パネルから選択 |
| BASICへ戻る | CTRL+C | キーボードを使用 |

パネルにはソナー、記録、静音切替、待機、やり直し、タイトルがあります。記録は未記録地点と同じセルか上下左右の隣から行います。5地点の順序は自由です。全記録後、出発地点へ戻ると成功です。

通常の移動・待機で酸素1、静音中は2、ソナーと記録で2を使います。海流による追加移動はさらに1を使います。岩礁への衝突は船体を1損傷します。酸素または船体が0になると失敗。パネル操作、写真の閲覧、何も入力していない間は時間も酸素も進みません。

ソナーは6行動の間、マンハッタン距離6以内を表示します。通常の視界は距離2。ソナーの音は追跡者を引き寄せます。追跡者は通常2行動ごと、静音中は4行動ごとに移動します。距離1以内で接触し、被弾後は4行動の猶予があります。

HUDは酸素と残量バー、船体、深度、次の未記録地点への距離・方位、記録数、機関、接近警報、ソナー状態を表示します。海流内の E/S/W/N は押される向きです。酸素30以下の `!!!` と接近警報は画面と効果音で知らせます。

![Sonar and instruments](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/sonar.png)
![Broken Gate](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/discovery-02.png)
![Black Sun](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/abyss-signal/discovery-05.png)

やり直し／プレイ中のタイトル移動は実行前に確認します。NOが初期選択です。A/Dで選びRETURNで確定、SPACEで取り消します。
