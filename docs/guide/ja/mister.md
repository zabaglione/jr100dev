## 1作品ずつ、または全作品をまとめて保存

[全作品一覧](Home)の各カードにある「MiSTer用 .prgを保存」から、その作品を直接ダウンロードできます。ソースの取得やビルドは不要です。

全51作品を入れる場合は、上のZIPをダウンロードして展開します。中の`JR100`フォルダーを、MiSTerのSDカードの`games/`へコピーしてください。個別配布とZIPには同じゲームが入っており、自動起動用のヒントも付いています。ZIPには起動手順とMITライセンスも同梱しています。

## 初回の設定

[JR-100コア](https://github.com/MiSTer-devel/JR100_MiSTer)と、自分で用意したBASIC ROMを使用します。**games/JR100/boot.rom**の用意は、コアの[ROM設定手順](https://github.com/MiSTer-devel/JR100_MiSTer#rom)を参照してください。ゲームの配布物にはROMやコア本体は含みません。

JR-100コアを起動して**READY**を待ちます。画面上のメニューで**Autostart loaded program**を**Yes**にし、**Load PRG**からダウンロードしたゲームを選びます。タイトル画面が出たら**RETURN**で開始します。ゲームは標準RAM 16KB用なので、`Extended RAM (reset)`はOffのままで使えます。

自動起動を無効にしている場合や、読み込み後もREADYのままの場合は、`A=USR($0300)`を入力してRETURNを押してください。この配布のゲームは機械語なので、`RUN`は不要です。自動入力の先頭が欠ける場合は、コアを最新版に更新してください。

## SuperStation One・USBストレージの場合

ファイルは、MiSTerが実際に使用しているストレージの`games/JR100/`へ置きます。SuperStation Oneでは、SDカードではなくUSBストレージが選ばれている場合があります。

上の手順はJR-100コア自身の**Load PRG**メニューを使います。SuperStation Oneの**Console Mode → Load Game**にはMGLランチャーが必要で、.prgだけでは登録できません。この画面から起動したい場合は、コアの[Console Mode設定手順](https://github.com/MiSTer-devel/JR100_MiSTer/blob/main/docs/SS1_FW12_CONSOLE_MODE.md)を参照してください。

## 操作・クレジット・確認状況

各ゲームのルールは作品別のガイド、キーボードとパッドの操作は[操作と起動方法](Controls)を参照してください。

RELIC DIVEは**JR-800 Web Emulator contributors**との共同制作です。配布物の[MITライセンス](LICENSE.txt)にもクレジットを記載しています。

2026年9月18日、SuperStation One実機と`JR100_20260801.rbf`で確認しました。標準RAM 16KBの設定で、以下の4作品の記載した版が配布PRGから自動起動し、本編に進むことを確認しています。

| 作品 | 確認した版 | SS1で確認した内容 |
| --- | --- | --- |
| FROST STEPS | 1.7.2 | 開始・移動・クリスタル取得 |
| GATE RUNNER | 3.0.0 | 開始・障害物の進行・穴に落ちた際の失敗表示 |
| STAR LANCE | 3.0.0 | 開始・移動・通常弾と重い弾の発射 |
| NIGHT SWARM | 3.0.0 | 開始・移動・パルス攻撃 |

上記4作品の記載した版は、実機所有者による物理パッド操作と効果音の確認も済んでいます。改修後のSTAR LANCE 4.0.0はエミュレーターで検証しており、SS1での再確認は未実施です。各作品の全ステージを通した確認と、残り47作品のSS1動作確認は未実施です。オリジナルのJR-100実機でも未確認です。
