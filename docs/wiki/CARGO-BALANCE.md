# CARGO BALANCE

[ホーム](Home) → [経営・サバイバル](Genre-Management) → CARGO BALANCE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=cargo-balance) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/cargo_balance)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

12個の荷物を4つの船倉へ積む全6航海。外側は運賃が2倍になる一方、船を傾ける力は内側の3倍です。次の2個の重さを読み、風と許容差に備えます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/demo-clear.png)

**[音付きプレイ動画を見る（約42秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=cargo-balance)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで船倉を選び、RETURNで積みます。各船倉は4個まで。左右の力の差に風の分を加え、LIMITを超えると転覆します。全12個を積めば出航です。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

クレーンから荷物が落下し、船体と積み荷が一緒に傾いて揺れます。積載音、転覆の原因表示、出航ジングルで結果を確認できます。演出が終わってから次のキーを押してください。

NEXT LOADは今の荷物、NEXTは続く2個、LOADEDは積載数。PORTとSTARBOARDは左右に掛かる力、WINDは左へ掛かる追加の力、FAREは運賃です。後半は許容差が10から8へ狭まります。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/cargo-balance/play-02.png)
