# サウンドサンプルの来歴

Webサウンドエディターの初期プロジェクトには、読み取り専用のBGM 12曲と効果音11種類を収録します。BGMは各原曲を参照して本リポジトリで作成した、ごく短い単音向け縮約です。歌詞、録音、楽譜画像、既存の近現代編曲は収録しません。

確認用の`samples/sound_demo`には、意図的に`ODE_TO_JOY_OPENING`、`AH_VOUS_DIRAIJE_OPENING`、`BLIP`だけを選択して収録します。ゲームに取り込む資産は、ワークベンチで選択したものだけです。

| 資産ID | 原曲 | 作曲者 | 来歴 |
| --- | --- | --- | --- |
| `ODE_TO_JOY_OPENING` | [交響曲第9番 終楽章](https://imslp.org/wiki/Symphony_No.9_%28Beethoven%2C_Ludwig_van%29) | Ludwig van Beethoven（1827年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `AH_VOUS_DIRAIJE_OPENING` | [K.265主題](https://imslp.org/wiki/12_Variations_on_%27Ah%2C_vous_dirai-je_maman%27%2C_K.265%2F300e_%28Mozart%2C_Wolfgang_Amadeus%29) | Wolfgang Amadeus Mozart（1791年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `FUR_ELISE_OPENING` | [エリーゼのために WoO 59](https://imslp.org/wiki/F%C3%BCr_Elise%2C_WoO_59_%28Beethoven%2C_Ludwig_van%29) | Ludwig van Beethoven（1827年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `BACH_PRELUDE_C_OPENING` | [平均律クラヴィーア曲集第1巻 前奏曲 BWV 846](https://imslp.org/wiki/Prelude_and_Fugue_in_C_major%2C_BWV_846_%28Bach%2C_Johann_Sebastian%29) | Johann Sebastian Bach（1750年没） | 原曲の分散和音を単音用に独自縮約。 |
| `EINE_KLEINE_NACHTMUSIK_OPENING` | [アイネ・クライネ・ナハトムジーク K.525](https://imslp.org/wiki/Eine_kleine_Nachtmusik%2C_K.525_%28Mozart%2C_Wolfgang_Amadeus%29) | Wolfgang Amadeus Mozart（1791年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `VIVALDI_SPRING_OPENING` | [四季「春」 RV 269](https://imslp.org/wiki/Le_Quattro_Staggioni_%28Vivaldi%2C_Antonio%29) | Antonio Vivaldi（1741年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `HANDEL_WATER_MUSIC_OPENING` | [水上の音楽 HWV 348-350](https://imslp.org/wiki/Water_Music_%28Handel%2C_George_Frideric%29) | George Frideric Handel（1759年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `PACHELBEL_CANON_OPENING` | [カノンとジーグ ニ長調 P.37](https://imslp.org/wiki/Canon_in_D_%28Pachelbel%2C_Johann%29) | Johann Pachelbel（1706年没） | 原曲の和声進行を単音用に独自縮約。 |
| `RAMEAU_GAVOTTE_OPENING` | [ガヴォット イ短調 RCT 5](https://imslp.org/wiki/Gavotte_in_A_minor_%28Rameau%2C_Jean-Philippe%29) | Jean-Philippe Rameau（1764年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `HAYDN_SURPRISE_OPENING` | [交響曲第94番「驚愕」](https://imslp.org/wiki/Symphony_No.94_%28Haydn%2C_Joseph%29) | Joseph Haydn（1809年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `SWAN_LAKE_OPENING` | [白鳥の湖 Op.20](https://imslp.org/wiki/Swan_Lake%2C_Op._20_%28Tchaikovsky%2C_Pyotr_Ilyich%29) | Pyotr Ilyich Tchaikovsky（1893年没） | 原曲の公開資料を参照した独自単音縮約。 |
| `CARMEN_HABANERA_OPENING` | [カルメンのハバネラ](https://imslp.org/wiki/Carmen_%28Bizet%2C_Georges%29) | Georges Bizet（1875年没） | 原曲の公開資料を参照した独自単音縮約。原題材の「El arreglito」の作曲者Sebastián Yradier（1865年没）も保護期間満了。歌詞は含まない。 |

効果音はすべて本リポジトリで作成した合成的な単音列であり、外部の楽曲・録音・効果音素材を参照しません。各効果音は10msセル50個（500ms）以内です。

| 資産ID | 種別 |
| --- | --- |
| `BLIP` | 上昇チャイム |
| `CLICK` | 短いクリック |
| `LASER` | 下降レーザー |
| `JUMP` | 上昇ジャンプ |
| `HIT` | 短いヒット |
| `EXPLODE` | 下降バースト |
| `PICKUP` | 取得音 |
| `ALERT` | 二連アラート |
| `START` | 開始チャイム |
| `GAME_OVER` | 終了チャイム |
| `COIN` | コイン音 |

日本の著作物は原則として著作者の死後70年で保護期間が満了し、満了した著作物はパブリックドメインとして利用できます。一方で録音には実演家・レコード製作者の権利があり得るため、本リポジトリは録音を収録・利用しません。詳細は[文化庁の解説](https://www.bunka.go.jp/seisaku/chosakuken/taisetsu/point/index.html)を参照してください。
