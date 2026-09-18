# ORBIT DRAFT

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/orbit-draft.html)

[ホーム](Home) → [カード・ボード](Genre-Tabletop) → ORBIT DRAFT

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=orbit-draft) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/orbit_draft)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

2枚の候補から札を選び、4×4の軌道盤へ落とすパズルです。次の3枚を読み、行・列の回転と落下連鎖で得点を伸ばします。配札は開始するタイミングで変わり、盤面と得点を引き継いで何ラウンドでも続けられます。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/demo-clear.png)

**[音付きプレイ動画を見る（約33秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=orbit-draft)**

1ステージのクリアまでを収録。

## 操作と遊び方

1. 右上の2枚をA/Dで選び、RETURNで決定します。
2. A/Dで落とす列を選び、RETURNで配置します。矢印で挟まれた空き枠に落ちます。使わなかった候補は残り、使った側だけにNEXTの左端の札が補充されます。NEXTは左から順に次の3枚です。
3. 盤面の下へSで移動すると、CARD・ROW・COLのメニューを選べます。候補選択中はSで直接メニューへ移れます。
4. ROWを選ぶと、W/Sで選んだ行をRETURNで右へ1マス回します。COLではA/Dで選んだ列をRETURNで下へ1マス回します。端の札は反対側へ回り込みます。
5. ROW・COLは回転後も選択を維持します。別のモードを明示的に選ぶまで続けて使えます。札の配置へ戻るときはメニューのCARDでRETURNを押します。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEで新しいゲームの確認を開き、承認すると盤面と得点をリセットします。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

選んだ札は列の空き枠まで落下し、行・列の回転では途中の位置を通って反対側へ回り込みます。三連以上が揃うとセミグラフィックスの光が三段階に広がり、消去音とともに消えます。残った札が落ちて再び揃うと連鎖音が鳴り、得点と回転回数が増えます。演出が終わってから次のキーを押してください。

Aは星、Bは環のある惑星、Cは月、Dは彗星、Eは人工衛星です。初めは最下段に異なる4枚が並びます。

同じ天体が縦・横・斜めに3枚以上続くと消えます。4枚の並びは重なった2本の三連、交差した並びはそれぞれの三連として数えますが、同じ札を二重には加点しません。回転直後の並びを判定してから空きを下へ詰め、落下によってまた揃えば連鎖します。

| 計器 | 意味 |
| --- | --- |
| SCORE | ゲーム開始からの合計得点。上限9999点 |
| CHAIN X | 直前の操作で起きた連鎖数 |
| GOAL | 今ラウンドの得点／目標。得点表示は99まで |
| SPIN | 回転の残り回数／最大4回 |
| RND | ラウンド番号。255以降は表示を255に保って継続 |

消去1回の得点は「消した札の枚数×2×連鎖数＋同時に揃えた2本目以降の三連1本につき2点」です。三連1本なら6点、四連なら10点、2連鎖目の三連は12点になります。

回転は最初に2回使えます。消去が起きるたびに1回補充され、最大4回まで貯められます。すべて同じ札、または空き枠だけの行・列は回数を消費しません。回転だけで空きを詰めた場合も1回消費します。

最初の目標は12点。達成するとジングルと結果を表示し、RETURNで次のラウンドへ進みます。目標は6点ずつ上がり、60点になった後も続きます。盤面・候補・予告・合計得点・残り回転回数はそのままで、ラウンド内の得点だけが0に戻ります。超過分は合計得点に入り、次ラウンドの目標には繰り越しません。

16枠が埋まっても回転が残っていれば続けられます。回転を使い切って満杯になると「FULL BOARD - NO SPINS」を表示して終了します。RETURNまたはSPACEで新しいゲームの確認を開けます。

攻略の手がかりは、予告にある札を使う場所を残すことです。同じ種類ごとに列を分けるだけでは5種類を4列に収めきれません。先に消す列の上に別の天体を置くと、落下後の横・斜めの連鎖も狙えます。回転は空き枠も動かすので、満杯になる前に使い道を考えておきましょう。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/orbit-draft/play-02.png)
