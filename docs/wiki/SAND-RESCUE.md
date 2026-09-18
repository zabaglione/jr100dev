# SAND RESCUE

> [Read this guide in English / 日本語のゲームガイド](https://zabaglione.github.io/pyjr100emu/guide/sand-rescue.html) · [MiSTer .prg](https://zabaglione.github.io/pyjr100emu/guide/downloads/sand-rescue.prg) · [MiSTer setup / 起動方法](https://zabaglione.github.io/pyjr100emu/guide/mister.html)

[ホーム](Home) → [戦術・自動化](Genre-Tactics) → SAND RESCUE

[プレイ](https://zabaglione.github.io/pyjr100emu/?game=sand-rescue) · [ビルドソース](https://github.com/zabaglione/jr100dev/tree/main/games/sand_rescue)

同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。

108滴の水を使い、6つの畑を救います。手前の作物は2〜3滴で3点、奥の作物は3〜5滴で6〜10点になります。畑ごとの収穫目標を満たしたら次へ進めますが、残りの作物で得点を伸ばすこともできます。水は途中で補充されず、余った分を次の畑へ持ち越します。

![タイトル](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/title.png)

## 紹介画像とプレイ動画

![開始時の盤面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/demo-start.png)

![操作を進めた場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/demo-play.png)

![最初の目標を達成した場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/demo-clear.png)

**[音付きプレイ動画を見る（約30秒）](https://zabaglione.github.io/pyjr100emu/gameplay.html?game=sand-rescue)**

1ステージのクリアまでを収録。

## 操作と遊び方

A/Dで水門A〜Cを選び、RETURNで貯水槽にたまった水をすべて流します。1つの放流が終わるまで次の放流はできません。手前の作物が必要な水を受け取り、余った水が奥へ進みます。

水は貯水槽へ自動的に入り、最大9滴までたまります。満杯のまま待つと、入ってきた水があふれて失われます。ひび割れた水路では、放流のたびに横の数字の分だけ水がしみ込みます。奥まで届けるなら、作物の必要量と途中で失う量を合計してから流してください。

収穫目標を満たすとREADYが点灯します。流れている水がなくなってからW（パッド上）で今回の収穫を確定し、結果画面のRETURNで次の畑へ進みます。追加の収穫を狙う場合は、Wを押さずに給水を続けてください。

方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEで全6面のやり直し確認を開き、承認すると最初の畑・108滴・0点から再開します。やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。

6つの畑で108滴の水を共有します。手前の作物は少量、奥の作物は高得点ですが、乾いた水路で水を失います。貯水と放流、最低収穫での終了と追加収穫を選び、余った水と得点を次へ持ち越します。水門、連続する水の移動、芽から実への成長、収穫、あふれに動きとSEがあります。演出が終わってから次のキーを押してください。

WATERは未使用の水の合計、TANKは貯水槽の量、POURは流れている水の量です。作物の下は「給水済み／必要量」、横の＋数字は収穫点です。育ち切った作物へは水を使わず、その先へ流します。

HARVESTは今回の収穫点と目標、TOTALは合計点、NEXTは次の畑の目標です。6つの目標は14・17・19・21・24・26点で、水路の配置、作物の必要量、水のたまる速さも変わります。最終合計130点でSILVER、140点でGOLDです。水を使い切って目標に届かなければ失敗です。

1面では、Aの手前と奥を育てるのに7滴（手前2＋水路1＋奥4）が必要です。ここで11点を確保し、BかCの手前へ2滴を流せば14点になります。もう一方の手前も育てると17点ですが、その2滴は次の畑には残りません。

![ゲーム開始時](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/play-01.png)

![プレイ中の場面](https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images/sand-rescue/play-02.png)
