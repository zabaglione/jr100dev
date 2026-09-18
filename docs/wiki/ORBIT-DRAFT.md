# ORBIT DRAFT

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → ORBIT DRAFT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-draft) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/orbit_draft)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

2枚の候補から1枚を選び、3×3の軌道盤へ配置するパズルです。行や列を回して同じ天体を揃え、3面それぞれの目標を達成します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-clear.png)

**[音付きプレイ動画を見る（約33秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=orbit-draft)**

1ステージのクリアまでを収録。

## 操作と遊び方

1. 右上の2枚をA/Dで選び、RETURNで決定します。
2. WASDで空き枠を選び、RETURNで配置します。使わなかった候補は残り、使った側だけに次の札が補充されます。
3. 候補を選び直すときは、盤面の下へ移動し、CARDSでRETURNを押します。候補選択中はSでこのメニューへ移れます。
4. ROW>でRETURNを押すと行の選択になり、W/Sで行を選び、RETURNで右へ1マス回します。COLVではA/Dで列を選び、RETURNで下へ1マス回します。端の札は反対側へ回り込みます。行選択はA/D、列選択はW/Sで取り消せます。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面のやり直し確認を開きます。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

選んだ候補の天体カードが枠へ飛び、行・列を回すと札が途中の位置を通って反対側へ回り込みます。同じ天体が揃うと段階的に発光して共鳴音が鳴り、達成数を確認する間を置いてから次の操作へ進みます。演出が終わってから次のキーを押してください。

Aは星、Bは環のある惑星、Cは月です。初期配置の3枚に6枚を加え、9枠を埋めた時点で目標を満たすとクリアします。

| 面 | 目標 | 右の計器 |
| --- | --- | --- |
| 1 | 同じ天体3枚の列を2本以上作る。縦・横・斜めが対象 | LINES |
| 2 | A・B・Cそれぞれの列を1本以上作る | ABC LINES |
| 3 | 2本の対角線を両方ともAで揃える。必要な5枠にAの印がある | A DIAGS |

計器は現在の達成数と目標です。完成した列の札には星印、その種類のA/B/Cにも星印が付きます。回転で列が崩れると達成数と印も戻ります。CARDSは配置数、SPINSは残りの回転回数です。

回転は1面2回まで。初期配置の札と空き枠も一緒に動きます。同じ札3枚だけの行・列を選んだ場合は回数を消費しません。2面以降は、初期配置の札を動かしてから揃える場所を考えるのが攻略の手がかりです。

9枠が埋まっても回転が残っていれば続けられます。回転を使い切って目標に届かなければ失敗です。満杯時のENDを選ぶと、その面を失敗として終えます。結果とジングルを確認した後、成功時はRETURNで次の面へ進みます。失敗時はRETURNでやり直し確認を開きます。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/play-02.png)
