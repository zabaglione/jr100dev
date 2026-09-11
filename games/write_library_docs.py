"""Generate genre navigation and native-game manuals from the authored catalogue."""

import json
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


home = "# JR-100 Games\n\n標準RAM 16KB向けのオリジナルゲーム50作品です。ジャンルから選ぶと、各作品の画面・遊び方・起動リンクを探せます。\n\n"
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

NIGHT SWARMでは次の配置を使います。

```text
Q W E
A   D
Z X C
```

Q/E/Z/Cが斜め、Xが下です。Sは移動に使いません。1ボタンパッドでも斜め入力を受け付けます。

## 開始・やり直し・終了

タイトルでRETURNまたはパッドのボタンを押すと開始します。SPACEで説明を開けます。新作44本のプレイ中はSPACEで現在の面をやり直せます。最初の6作品は各ページに記載の操作パネルを使います。CTRL+Cでゲームを終了してBASICへ戻ります。

ゲームは主な操作に1ボタンパッドも使えます。説明の表示、任意のタイミングでのやり直し、BASICへ戻る操作にはキーボードを使用します。

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
        import re

        text = ("\n".join(lines) + "\n").replace("バージョン：1.0.0", "バージョン：1.1.0")
        text = re.sub(r"[\d,]+ bytes(?!のスタック)", f"{layout['code_bytes']:,} bytes", text)
        path.write_text(text)
        continue
    objective, controls, hud = manuals[g["directory"]]
    layout = json.loads((directory / "build/layout.json").read_text())
    prefix = f"# {g['title']}\n\n{breadcrumb}\n\n[プレイ]({PLAY}{g['id']}) · [ビルドソース]({BASE}/tree/main/games/{g['directory']})\n\n{launch_note()}\n\n"
    body = f"{objective}\n\n![タイトル]({IMAGES}/{g['id']}/title.png)\n\n## 操作と遊び方\n\n{controls}\n\n"
    body += "方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。SPACEでこの面をやり直し、CTRL+CでBASICへ戻ります。\n\n"
    body += f"{hud}\n\n![ゲーム開始時]({IMAGES}/{g['id']}/play-01.png)\n\n![プレイ中の場面]({IMAGES}/{g['id']}/play-02.png)\n\n"
    body += f"## ビルドと検証\n\nバージョン {meta['version']}。開始番地 `$0300`、ゲーム本体と定数は {layout['code_bytes']:,} bytes。画面・作業領域・復帰用の保存領域・512 bytesのスタックを含めて標準RAM 16KB内で動作します。PCGは32文字を場面ごとに切り替えます。\n\n"
    body += f"```sh\nmake -C games/{g['directory']}\nmake -C games/{g['directory']} test\n```\n\n"
    body += "出力はゲームの `build/` ディレクトリに作られます。`rules.py` はビルド時にMB8861Hの機械語へ変換されます。JR-100上でPythonを実行する方式ではありません。\n\n"
    body += "キー入力による全ステージのクリア、失敗を含む入力試験、画面範囲、RAM配置、スタック、PCM出力をエミュレーターで検査しています。掲載画像は所有するBASIC ROMからPRGを起動した実フレームです。実機での動作・音声は未確認です。\n\n"
    body += f"```sh\n.venv/bin/python games/native/replay.py {g['directory']} --rom /path/to/owned-rom.prg --capture --keyboard\n```\n\n"
    body += "タイトルには長めの単音曲、プレイ中には効果音を付けています。"
    body += f"ソース・画像・曲は[MIT License]({BASE}/blob/main/games/LICENSE)。`art/`にはPCG Workbench用の画面データもあります。\n"
    (WIKI / (g["id"].upper() + ".md")).write_text(prefix + body)
    readme = f"# {g['title']}\n\n[Wiki]({BASE}/wiki/{g['id'].upper()}) · [プレイ]({PLAY}{g['id']})\n\n"
    readme += body.replace(f'{IMAGES}/{g["id"]}/', "images/")
    (directory / "README.md").write_text(readme)
readme = "# JR-100 Games\n\n標準RAM 16KB向けの独立したオリジナルゲーム50作品です。教材用の `samples/` とは分けて管理します。\n\n"
readme += f"[Wikiのジャンル別一覧]({BASE}/wiki) · [共通操作]({BASE}/wiki/Controls)\n\n"
for gid, genre in genres.items():
    readme += f"## {genre['title']}\n\n| ゲーム | 内容 |\n| --- | --- |\n"
    for g in games:
        if g["genre"] == gid:
            readme += f"| [{g['title']}]({g['directory']}/) | {g['summary']} |\n"
    readme += "\n"
old = (ROOT / "README.md").read_text()
readme += old[old.index("## ビルド") :]
readme = readme.replace(
    "ターン制の5作品はTimer 2を約60Hzでポーリングします。",
    "共通処理はTimer 2を約60Hzでポーリングします。",
)
readme += "\n`native/` は新作44本のコンパイラー、画面構成、共通実行処理、ルール検査と全編リプレイを収めます。作品固有のルールと地形は各作品のディレクトリにあります。4方向はWASD、8方向はQWE／AD／ZXCです。\n"
(ROOT / "README.md").write_text(readme)
print("Generated 50 game manuals and 6 genre navigation pages")
