# ORBIT DRAFT

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → ORBIT DRAFT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-draft) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/orbit_draft)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

次に来る札を3×3の盤へ配置し、同じA・B・Cを一列に揃えます。一列3点で、9枚を置いた時点で6点以上なら成功です。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-clear.png)

**[音付きプレイ動画を見る（約34秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=orbit-draft)**

1ステージのクリアまでを収録。

## 操作と遊び方

WASDで空き場所を選び、RETURNで次の札を置きます。配札の異なる3ラウンドがあります。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

天体カードがNEXTから選択した枠へ飛び、一列揃うと三つの天体が段階的に発光します。配置音と共鳴音を分け、加点表示を見せてから次の札へ進みます。演出が終わってから次のキーを押してください。

Aは星、Bは環のある惑星、Cは月です。左右の矢印で選んだ枠へ、NEXTの札が飛んで配置されます。縦・横・斜めに同じ札が三つ揃うと、その列が発光してRESONANCE +3を表示します。完成したカードには星印を残します。SCOREは現在の得点と目標6点、PLACEDは配置済みの枚数です。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/play-02.png)
