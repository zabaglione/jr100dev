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

**STAR LANCE 4.0.0を含む全51作品を、MiSTer（SuperStation One）実機で確認済みです。** 2026年9月18日、実機所有者が`JR100_20260801.rbf`を使用し、全作品の起動・物理パッド操作・音を確認しました。

対象は[確認した版の一覧](https://github.com/zabaglione/jr100dev/blob/main/docs/guide/ss1-verification-2026-09-18.md)を参照してください。確認範囲は起動・操作・音で、全ステージの踏破を示すものではありません。オリジナルのJR-100実機では未確認です。
