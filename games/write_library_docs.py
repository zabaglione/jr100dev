"""Generate genre navigation and native-game manuals from the authored catalogue."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKI = ROOT.parent / "docs/wiki"
BASE = "https://github.com/zabaglione/jr100dev"
PLAY = "https://zabaglione.github.io/pyjr100emu/?game="
IMAGES = "https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images"
library = json.loads((ROOT / "library.json").read_text())
manuals = json.loads((ROOT / "native/manuals.json").read_text())
genres = {g["id"]: g for g in library["genres"]}
games = library["games"]


def page(genre):
    return "Genre-" + genre.title()


def launch_note():
    return "同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。"


home = f"# JR-100 Games\n\n標準RAM 16KB向けのオリジナルゲーム{len(games)}作品です。ジャンルから選ぶと、各作品の画面・遊び方・起動リンクを探せます。\n\n"
home += "| ジャンル | 作品数 | 内容 |\n| --- | ---: | --- |\n"
for gid, genre in genres.items():
    subset = [g for g in games if g["genre"] == gid]
    home += f"| [{genre['title']}]({page(gid)}) | {len(subset)} | {genre['description']} |\n"
home += (
    "\n[タイトル順の全作品](All-Games) · [共通操作と起動方法](Controls)\n\n"
    + launch_note()
)
home += "\n\n基本の方向キーは **W/A/S/D**、8方向の作品は **QWE／AD／ZXC** です。作品ごとの操作は各ページに掲載しています。\n\nエミュレーターで確認済みです。実機での動作・音声は未確認です。\n\n"
home += f"[ビルド可能なソースと開発手順]({BASE}/tree/main/games)\n"
(WIKI / "Home.md").write_text(home)
sidebar = "[JR-100 Games](Home)\n\n"
for gid, genre in genres.items():
    sidebar += f"- [{genre['title']}]({page(gid)})\n"
sidebar += "\n[全作品をタイトル順に探す](All-Games)\n\n[操作・起動方法](Controls)\n"
(WIKI / "_Sidebar.md").write_text(sidebar)
all_games = "# 全作品・タイトル順\n\n[ホーム](Home) · [ジャンルから探す](Home)\n\n| タイトル | ジャンル | 起動 |\n| --- | --- | --- |\n"
for g in sorted(games, key=lambda g: g["title"]):
    all_games += f"| [{g['title']}]({g['id'].upper()}) | [{genres[g['genre']]['title']}]({page(g['genre'])}) | [プレイ]({PLAY}{g['id']}) |\n"
(WIKI / "All-Games.md").write_text(all_games)
for gid, genre in genres.items():
    content = f"# {genre['title']}\n\n[ホーム](Home) → {genre['title']}\n\n{genre['description']}。タイトルを選ぶと操作と複数のゲーム画面を確認できます。\n\n"
    content += "| 画面 | ゲーム・概要 | 起動 |\n| --- | --- | --- |\n"
    for g in sorted((g for g in games if g["genre"] == gid), key=lambda g: g["title"]):
        content += f'| [<img src="{IMAGES}/{g["id"]}/title.png" width="200" alt="{g["title"]}">]({g["id"].upper()}) | **[{g["title"]}]({g["id"].upper()})**<br>{g["summary"]} | [プレイ]({PLAY}{g["id"]}) |\n'
    content += "\n" + launch_note() + "\n"
    (WIKI / (page(gid) + ".md")).write_text(content)
(WIKI / "Controls.md").write_text("""# 操作と起動方法

[ホーム](Home) → 共通操作

## 4方向の基本

```text
    W
  A S D
```

W＝上、A＝左、S＝下、D＝右です。決定・主操作はRETURN。作品によりFの補助操作があります。CHRONO BREACHとABYSS SIGNALの待機はXです。

## 8方向

NIGHT SWARMとRELIC DIVEでは次の配置を使います。

```text
Q W E
A   D
Z X C
```

Q/E/Z/Cが斜め、Xが下です。Sは移動に使いません。RELIC DIVEではSで1ターン待機、W/Xでメニューを選択します。1ボタンパッドでも斜め入力を受け付けます。

## 開始・やり直し・終了

タイトルでRETURNまたはパッドのボタンを押すと開始します。最初の50作品はSPACEで説明を開けます。新作44本のプレイ中はSPACEで現在の面をやり直せます。最初の6作品は各ページに記載の操作パネルを使います。RELIC DIVEはタイトルでW/Xにより難易度を選び、プレイ中のRETURNメニューからHELPを開きます。SPACEは戻る操作です。CTRL+Cでゲームを終了してBASICへ戻ります。

ゲームは主な操作に1ボタンパッドも使えます。説明の表示、任意のタイミングでのやり直し、BASICへ戻る操作にはキーボードを使用します。

FROST STEPS、MAGNET VAULT、GLYPH SHIFT、GRAVITY WELLは40面と星評価に対応しています。Fで面選択、WASDで選択、RETURNで開始、SPACEでタイトルへ戻ります。面選択は最初から全40面を選べます。クリア画面のSPACEは同じ面の再挑戦、RETURNは次の面です。終了前にタイトル／面選択のPWを書き留めると、次回Xから面番号と全40面の最高評価を復元できます。

## Wikiから起動する

1. [JR-100 Web Emulator](https://zabaglione.github.io/pyjr100emu/)で、自分のBASIC ROMを事前に設定します。
2. Wikiの作品ページ、ジャンル一覧、または全作品一覧から「プレイ」を押します。
3. 同じブラウザーにROMが保存されていれば、ゲームのタイトル画面まで自動起動します。ファイル選択やUSR入力は不要です。

ROMを削除した場合や別のブラウザーでは、ROMの設定が必要です。BASIC ROMはゲーム配布物に含みません。音は最初のキー入力または画面クリックで有効になります。
""")
for g in games:
    directory = ROOT / g["directory"]
    meta = json.loads((directory / "game.json").read_text())
    breadcrumb = f"[ホーム](Home) → [{genres[g['genre']]['title']}]({page(g['genre'])}) → {g['title']}"
    if not meta.get("nativeRules"):
        path = WIKI / (g["id"].upper() + ".md")
        text = path.read_text()
        lines = text.splitlines()
        if not lines[2].startswith("[ホーム]"):
            lines[2:2] = [breadcrumb, ""]
        layout = json.loads((directory / "build/layout.json").read_text())
        text = "\n".join(lines) + "\n"
        text = re.sub(r"バージョン：[\d.]+", f"バージョン：{meta['version']}", text)
        text = re.sub(
            r"[\d,]+ bytes(?!のスタック)", f"{layout['code_bytes']:,} bytes", text
        )
        path.write_text(text)
        continue
    objective, controls, hud = manuals[g["directory"]]
    layout = json.loads((directory / "build/layout.json").read_text())
    prefix = f"# {g['title']}\n\n{breadcrumb}\n\n[プレイ]({PLAY}{g['id']}) · [ビルドソース]({BASE}/tree/main/games/{g['directory']})\n\n{launch_note()}\n\n"
    body = f"{objective}\n\n![タイトル]({IMAGES}/{g['id']}/title.png)\n\n## 操作と遊び方\n\n{controls}\n\n"
    body += "方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。\n\n"
    body += f"{hud}\n\n![ゲーム開始時]({IMAGES}/{g['id']}/play-01.png)\n\n![プレイ中の場面]({IMAGES}/{g['id']}/play-02.png)\n\n"
    if meta.get("rankedCampaign"):
        levels = json.loads((directory / "levels.json").read_text())
        body += "## 手数と星評価\n\n規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。\n\n"
        body += "| 評価 | 条件 |\n| --- | --- |\n| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |\n| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |\n| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |\n\n"
        body += "PARは、両方のルーンを回収してクリアできる最短手数を探索して設定しています。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。\n\n"
        body += f"![3つ星クリア]({IMAGES}/{g['id']}/three-stars.png)\n\n"
        body += "## 40面の構成と再挑戦\n\n| 面 | 難度の段階 | PARの範囲 |\n| --- | --- | ---: |\n"
        for i, tier in enumerate(("入門", "基本", "応用", "上級", "最終課題")):
            pars = [v[69] for v in levels[i * 8 : (i + 1) * 8]]
            body += f"| {i * 8 + 1}〜{i * 8 + 8} | {tier} | {min(pars)}〜{max(pars)} |\n"
        body += "\nFで面選択を開き、WASDまたはパッドで選び、RETURNまたはボタンで開始します。全40面を最初から選択でき、選択した面のPARと各面の最高評価を確認できます。面選択のSPACEはタイトルへ戻ります。\n\nクリア後はSPACEで同じ面に再挑戦、RETURNで次の面へ進みます。BESTは最高評価、NOWは今回の評価です。低い評価で再クリアしてもBESTは下がりません。ゲーム終了後も続ける場合は、次のパスワードを記録してください。\n\n"
        body += f"![40面の最高評価一覧]({IMAGES}/{g['id']}/stage-select.png)\n\n"
        body += "## パスワードで続きから\n\nタイトルと面選択の下部に表示される **PW** を書き留めてください。選択中の面番号と、全40面の最高評価を復元できます。盤面の途中経過は保存せず、復元後にRETURNでその面の最初から再開します。\n\nコードは空白を除いて **4〜24文字**。先頭の3つ星達成済みの面と末尾の未クリア面を省略するため、順番に3つ星を取って進める場合は通常5〜6文字です。数字は使わず、次の16種類の大文字だけを使います。\n\n```text\nACDEFGHJKMNPQRTW\n```\n\n1. タイトルまたは面選択でXを押します。\n2. コードを入力し、RETURNで復元します。表示上の区切り空白は入力しても省略しても構いません。\n3. 修正はBackspace（実機ではマイナスキー）、取り消しはXです。\n\n入力画面ではパッドの方向で文字を選び、ボタンで追加する方法も使えます。最後にLOADを選んでボタンを押すと復元します。DELは1文字削除、BACKは取り消しです。入力ミスや別作品のコードを検査し、エラー時は現在の記録を変更しません。\n\n"
        body += f"![パスワード入力]({IMAGES}/{g['id']}/password-entry.png)\n\n![再起動後の記録復元]({IMAGES}/{g['id']}/password-restored.png)\n\n"
    body += f"## ビルドと検証\n\nバージョン {meta['version']}。開始番地 `$0300`、ゲーム本体と定数は {layout['code_bytes']:,} bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。\n\n"
    body += f"```sh\nmake -C games/{g['directory']}\nmake -C games/{g['directory']} test\n```\n\n"
    body += "出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。\n\n"
    if meta.get("rankedCampaign"):
        body += "盤面はビルド時に2マスを1バイトへ圧縮します。`levels.json` が編集用の面データ、`challenges.json` がクリア経路とルーン回収経路、`solutions.json` が全40面の3つ星リプレイです。`native/campaign_levels.py` で再生成でき、`native/campaign_checks.py` は全盤面の解探索、評価条件、再挑戦、面選択、最高評価の保持、手数カウンターの上限を検査します。回転・鏡映だけの地形の重複は除外しています。`native/password_checks.py` はパスワードの圧縮・展開、誤入力の検出、別作品のコード拒否と、再起動後のキー／パッド入力による記録復元を検証します。\n\n"
    body += "キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。\n\n"
    body += f"```sh\n.venv/bin/python games/native/replay.py {g['directory']} --rom /path/to/owned-rom.prg --capture --keyboard\n```\n\n"
    body += "タイトルには長めの単音曲、プレイ中には効果音を付けています。"
    body += f"ソース・画像・曲は[MIT License]({BASE}/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。\n"
    (WIKI / (g["id"].upper() + ".md")).write_text(prefix + body)
    readme = f"# {g['title']}\n\n[Wiki]({BASE}/wiki/{g['id'].upper()}) · [プレイ]({PLAY}{g['id']})\n\n"
    readme += body.replace(f'{IMAGES}/{g["id"]}/', "images/")
    (directory / "README.md").write_text(readme)
readme = f"# JR-100 Games\n\n標準RAM 16KB向けの独立したオリジナルゲーム{len(games)}作品です。教材用の `samples/` とは分けて管理します。\n\n"
readme += f"[Wikiのジャンル別一覧]({BASE}/wiki) · [共通操作]({BASE}/wiki/Controls)\n\n"
for gid, genre in genres.items():
    readme += f"## {genre['title']}\n\n| ゲーム | 内容 |\n| --- | --- |\n"
    for g in games:
        if g["genre"] == gid:
            readme += f"| [{g['title']}]({g['directory']}/) | {g['summary']} |\n"
    readme += "\n"
old = (ROOT / "README.md").read_text()
build_notes = old[old.index("## ビルド") :]
readme += re.sub(r"\n`native/` は新作44本[^\n]*\n", "\n", build_notes).rstrip() + "\n"
readme = readme.replace(
    "ターン制の5作品はTimer 2を約60Hzでポーリングします。",
    "共通処理はTimer 2を約60Hzでポーリングします。",
)
readme += "\n`native/` は新作44本のコンパイラー、画面構成、共通実行処理、ルール検査と全編リプレイを収めます。作品固有のルールと地形は各作品のディレクトリにあります。4方向はWASD、8方向はQWE／AD／ZXCです。\n"
(ROOT / "README.md").write_text(readme)
print(f"Generated {len(games)} game manuals and {len(genres)} genre navigation pages")
