"""Generate genre navigation and native-game manuals from the authored catalogue."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "common"))
from fonts import STYLES

WIKI = ROOT.parent / "docs/wiki"
BASE = "https://github.com/zabaglione/jr100dev"
PLAY = "https://zabaglione.github.io/pyjr100emu/?game="
IMAGES = "https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images"
library = json.loads((ROOT / "library.json").read_text())
manuals = json.loads((ROOT / "native/manuals.json").read_text())
visuals = json.loads((ROOT / "visual-design.json").read_text())
titles = json.loads((ROOT / "title-design.json").read_text())
genres = {g["id"]: g for g in library["genres"]}
games = library["games"]
assert set(visuals) == {g["id"] for g in games}
assert set(titles) == set(visuals)
MOTION = {
    "frost-steps": "氷上を1マスずつ滑り、途中でクリスタルやルーンを拾う様子を表示します。1回の方向入力は、滑走距離にかかわらず1手です。",
    "gravity-well": "重力を変えると、球が1マスずつ転がって止まるまでを表示します。複数の球が移動する順序も追えます。",
    "seed-merge": "種の移動、同じ種の合成、隙間を詰める移動、新しい種の出現を順に表示します。",
    "prism-trace": "鏡を回した後、光が通るマスを順に表示します。反射して進む経路を追えます。",
    "peg-garden": "選んだ駒が隣の駒を飛び越え、空いた穴に着地する様子を表示します。",
    "quiet-route": "プレイヤーが動いた盤面を一度表示してから、警備員が応答します。自分の行動と敵の行動を区別できます。",
}


def feedback_section(game):
    text = "## 動きとクリア演出\n\n"
    if game["id"] in MOTION:
        text += MOTION[game["id"]] + "演出中の追加入力は受け付けません。\n\n"
    duration = "約1.9秒" if game["id"] == "relic-dive" else "約1.6秒"
    text += f"クリア時は完成した盤面・結果を残し、{duration}のジングルと余韻を挟みます。その後、キーを押し直して次の操作に進みます。クリア直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。\n\n"
    return text


def page(genre):
    return "Genre-" + genre.title()


def launch_note():
    return "同じブラウザーで自分のBASIC ROMを事前に設定してください。登録済みなら「プレイ」からタイトルまで自動起動します。音は最初のキー入力または画面クリックで有効になります。"


def font_description(game):
    if game["id"] == "relic-dive":
        layout = json.loads(
            (ROOT / game["directory"] / "build/layout.json").read_text()
        )
        return f"通常文字のフォント変更は保留しています。タイトルはPCG全32枠、ゲーム中は31枠を使用し、コード・定数の空きは{layout['code_free_bytes']}バイトです。ロゴ・地形・アイテムの判別を優先しています。"
    record = json.loads((ROOT / game["directory"] / "build/fonts.json").read_text())
    name, shape = STYLES[record["style"]]
    chars = record["game"]["characters"]
    if not chars:
        return "今回は通常フォントを維持しています。絵柄やアニメーションに使うPCGを残すと、一式の数字・英字を揃える枠が足りないためです。一部の文字だけ書体が変わる置き換えは行いません。"
    target = "英大文字A〜Zの26文字" if "A" in chars else "数字0〜9の10文字"
    return f"ゲーム中の**{target}を{name}フォント**（{shape}）で揃えています。部分的な英字の置き換えは行いません。タイトルの操作案内・説明・パスワード入力は通常フォントに統一しています。既存のロゴと絵柄を保ち、空きPCG枠だけを使用します。"


def visual_section(game):
    return (
        "## タイトルのデザイン\n\n"
        + titles[game["id"]]
        + "\n\n"
        + "## 画面の奥行き\n\n"
        + visuals[game["id"]]
        + "\n\n"
        + "## ゲーム専用フォント\n\n"
        + font_description(game)
        + "\n\n"
        + feedback_section(game)
    )


def update_visual_section(text, game):
    text = re.sub(
        r"\n## 動きとクリア演出\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL
    )
    text = re.sub(
        r"\n## タイトルのデザイン\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL
    )
    text = re.sub(r"\n## 画面の奥行き\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL)
    text = re.sub(
        r"\n## ゲーム専用フォント\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL
    )
    position = text.find("\n## ")
    if position < 0:
        position = len(text.rstrip())
    return (
        text[:position].rstrip()
        + "\n\n"
        + visual_section(game)
        + text[position:].lstrip()
    )


home = f"# JR-100 Games\n\n標準RAM 16KB向けのオリジナルゲーム{len(games)}作品です。ジャンルから選ぶと、各作品の画面・遊び方・起動リンクを探せます。\n\n"
home += "| ジャンル | 作品数 | 内容 |\n| --- | ---: | --- |\n"
for gid, genre in genres.items():
    subset = [g for g in games if g["genre"] == gid]
    home += f"| [{genre['title']}]({page(gid)}) | {len(subset)} | {genre['description']} |\n"
home += (
    "\n[タイトル順の全作品](All-Games) · [タイトル画面ギャラリー](#タイトル画面ギャラリー) · [共通操作と起動方法](Controls) · [画面表現の工夫](Visual-Design) · [専用フォント](Font-Design)\n\n"
    + launch_note()
)
home += "\n\n基本の方向キーは **W/A/S/D**、8方向の作品は **QWE／AD／ZXC** です。作品ごとの操作は各ページに掲載しています。\n\nエミュレーターで確認済みです。実機での動作・音声は未確認です。\n\n"
home += "[移動とクリア演出・動作動画](Motion-and-Clear)\n\n"
home += f"[ビルド可能なソースと開発手順]({BASE}/tree/main/games)\n"
home += "\n## タイトル画面ギャラリー\n\n"
home += f"全{len(games)}作品のタイトルを、遊びの中心となる道具・場所・動きに合わせて個別に構成しました。文字の大きさと縦横比、余白、白い面の量も変えています。石の刻印・結晶の切り口・スリットを入れた文字は作品に合わせて使い、操作案内とパスワードは通常文字で揃えています。\n\n"
home += "すべてゲーム本体のPCGで描画します。標準RAM 16KB、PCG最大32文字の範囲内です。画像は所有するBASIC ROMから起動したエミュレーターの実画面で、実機での表示は未確認です。\n\n"
for gid, genre in genres.items():
    home += f"### [{genre['title']}]({page(gid)})\n\n| タイトル画面 | デザインと起動 |\n| --- | --- |\n"
    for game in sorted(
        (g for g in games if g["genre"] == gid), key=lambda g: g["title"]
    ):
        game_id = game["id"]
        home += f'| [<img src="{IMAGES}/{game_id}/title.png" width="300" alt="{game["title"]}">]({game_id.upper()}) | **[{game["title"]}]({game_id.upper()})**<br>{titles[game_id]}<br>[プレイ]({PLAY}{game_id}) |\n'
    home += "\n"
(WIKI / "Home.md").write_text(home.rstrip() + "\n")
sidebar = "[JR-100 Games](Home)\n\n"
for gid, genre in genres.items():
    sidebar += f"- [{genre['title']}]({page(gid)})\n"
sidebar += "\n[全作品をタイトル順に探す](All-Games)\n\n[タイトル画面ギャラリー](Home#タイトル画面ギャラリー)\n\n[操作・起動方法](Controls)\n\n[画面表現の工夫](Visual-Design) · [専用フォント](Font-Design)\n"
sidebar += "\n[移動とクリア演出](Motion-and-Clear)\n"
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

タイトルでRETURNまたはパッドのボタンを押すと開始します。最初の50作品はSPACEで説明を開けます。新作44本のうちBRICK PULSE以外では、プレイ中のSPACEで現在の面のやり直し確認を開きます。BRICK PULSEのプレイ中のSPACEには何も割り当てていません。最初の6作品は各ページに記載の操作パネルを使います。RELIC DIVEはタイトルでW/Xにより難易度を選び、プレイ中のRETURNメニューからHELPを開きます。SPACEは戻る操作です。CTRL+Cでゲームを終了してBASICへ戻ります。

やり直しは「REALLY RESET?」で確認します。最初はNOが選ばれ、A/D（パッド左右）で選択、RETURN（ボタン）で確定します。SPACEでも取り消せます。確認中はゲーム進行を止めます。面選択への移動など、途中の盤面を捨てる操作も確認します。1手の取り消し、LOOP TENの巻き戻し、RELIC DIVEの中断・再開は通常操作として扱います。ブラウザのResetボタンも実行前に確認します。

ゲームは主な操作に1ボタンパッドも使えます。説明の表示、任意のタイミングでのやり直し、BASICへ戻る操作にはキーボードを使用します。

FROST STEPS、MAGNET VAULT、GLYPH SHIFT、GRAVITY WELLは40面と星評価に対応しています。Fで面選択、WASDで選択、RETURNで開始、SPACEでタイトルへ戻ります。面選択は最初から全40面を選べます。クリア画面のSPACEは同じ面の再挑戦、RETURNは次の面です。終了前にタイトル／面選択のPWを書き留めると、次回Xから面番号と全40面の最高評価を復元できます。

## 移動中・クリア直後の入力

連続移動の演出中は追加の操作を受け付けません。クリア時は完成した盤面・結果を残し、約1.6秒（RELIC DIVEは約1.9秒）のジングルと余韻を挟みます。終わってからキーを押し直してください。[動作動画と作品ごとの変更](Motion-and-Clear)も掲載しています。

## Wikiから起動する

1. [JR-100 Web Emulator](https://zabaglione.github.io/pyjr100emu/)で、自分のBASIC ROMを事前に設定します。
2. Wikiの作品ページ、ジャンル一覧、または全作品一覧から「プレイ」を押します。
3. 同じブラウザーにROMが保存されていれば、ゲームのタイトル画面まで自動起動します。ファイル選択やUSR入力は不要です。

ROMを削除した場合や別のブラウザーでは、ROMの設定が必要です。BASIC ROMはゲーム配布物に含みません。

ブラウザーが許可していれば音声を自動で開始します。制限されている場合は、ゲーム画面の上に「画面をマウスでクリックして、音声を有効にしてください」と表示します。画面・案内・Enable soundのクリック、画面のタップ、またはキー入力で有効になり、案内が消えます。ゲームパッドだけでは音声制限を解除できないことがあります。保存したミュート設定は維持します。
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
        path.write_text(update_visual_section(text, g))
        readme_path = directory / "README.md"
        readme_text = update_visual_section(readme_path.read_text(), g)
        readme_text = re.sub(
            r"バージョン[： ]+[\d.]+", f"バージョン：{meta['version']}", readme_text
        )
        readme_text = re.sub(
            r"[\d,]+ bytes(?!のスタック)",
            f"{layout['code_bytes']:,} bytes",
            readme_text,
        )
        readme_path.write_text(readme_text)
        continue
    objective, controls, hud = manuals[g["directory"]]
    layout = json.loads((directory / "build/layout.json").read_text())
    prefix = f"# {g['title']}\n\n{breadcrumb}\n\n[プレイ]({PLAY}{g['id']}) · [ビルドソース]({BASE}/tree/main/games/{g['directory']})\n\n{launch_note()}\n\n"
    body = f"{objective}\n\n![タイトル]({IMAGES}/{g['id']}/title.png)\n\n"
    body += visual_section(g) + f"## 操作と遊び方\n\n{controls}\n\n"
    body += "方向キーはキーボードまたはパッド、RETURNはパッドのボタンでも操作できます。"
    body += (
        "プレイ中のSPACEは無効です。"
        if meta.get("disableSpaceReset")
        else "SPACEでこの面のやり直し確認を開きます。"
    )
    body += "やり直し確認はNOが初期選択です。A/Dで選び、RETURNで確定、SPACEで取り消します。確認中は進行を止めます。CTRL+CでBASICへ戻ります。\n\n"
    body += f"{hud}\n\n![ゲーム開始時]({IMAGES}/{g['id']}/play-01.png)\n\n![プレイ中の場面]({IMAGES}/{g['id']}/play-02.png)\n\n"
    if g["id"] == "frost-steps":
        body += f"## 滑走とクリアの動画\n\n![1面を滑走して3つ星クリアする実画面]({IMAGES}/frost-steps/slide-clear.gif)\n\n[音付き動画を見る]({BASE}/blob/main/games/frost_steps/images/slide-clear.mp4)。キーボード入力だけで1面をクリアした、約7.5秒のエミュレーター録画です。GIFには音がありません。\n\n"
    if g["id"] == "brick-pulse":
        body += f"![落下アイテム]({IMAGES}/brick-pulse/items.png)\n\n![後半のドローンと装甲ブロック]({IMAGES}/brick-pulse/drone.png)\n\n![やり直し確認]({IMAGES}/brick-pulse/reset.png)\n\n"
    if meta.get("rankedCampaign"):
        levels = json.loads((directory / "levels.json").read_text())
        body += "## 手数と星評価\n\n規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。\n\n"
        body += "| 評価 | 条件 |\n| --- | --- |\n| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |\n| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |\n| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |\n\n"
        body += "PARは、両方のルーンを回収してクリアできる最短手数を探索して設定しています。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。\n\n"
        body += f"![3つ星クリア]({IMAGES}/{g['id']}/three-stars.png)\n\n"
        body += "## 40面の構成と再挑戦\n\n| 面 | 難度の段階 | PARの範囲 |\n| --- | --- | ---: |\n"
        for i, tier in enumerate(("入門", "基本", "応用", "上級", "最終課題")):
            pars = [v[69] for v in levels[i * 8 : (i + 1) * 8]]
            body += (
                f"| {i * 8 + 1}〜{i * 8 + 8} | {tier} | {min(pars)}〜{max(pars)} |\n"
            )
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
    readme += body.replace(f"{IMAGES}/{g['id']}/", "images/")
    (directory / "README.md").write_text(readme)
readme = f"# JR-100 Games\n\n標準RAM 16KB向けの独立したオリジナルゲーム{len(games)}作品です。教材用の `samples/` とは分けて管理します。\n\n"
readme += f"[Wikiのジャンル別一覧]({BASE}/wiki) · [共通操作]({BASE}/wiki/Controls) · [画面表現の工夫]({BASE}/wiki/Visual-Design) · [専用フォント]({BASE}/wiki/Font-Design)\n\n"
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
visual_page = "# 画面表現の工夫\n\n[ホーム](Home) → 画面表現の工夫\n\n"
visual_page += "全51作品を確認し、JR-100らしい擬似3D表現を追加しました。壁や駒の上面・側面、接地影、盤の厚み、遠近感を使い分けています。操作に必要な文字や格子は読みやすさを優先し、当たり判定と操作方法は変えていません。\n\n"
visual_page += "すべて標準RAM 16KB内です。PCGの描き換えと既存の背景領域を中心に使い、PCGは最大32文字のままです。追加画像をブラウザー側で重ねる方式ではなく、ゲームのPRG自体に組み込んでいます。\n\n"
visual_page += "## 代表的な画面\n\n"
for gid, caption in (
    ("frost-steps", "氷壁の上面と反射"),
    ("gate-runner", "奥へ収束する3本の走路"),
    ("dice-relic", "上面と側面のあるダイス"),
    ("word-foundry", "文字を読みやすく保った活字台"),
):
    filename = "battle-01.png" if gid == "dice-relic" else "play-01.png"
    visual_page += f"### [{gid.upper()}]({gid.upper()})\n\n{caption}。\n\n![{caption}]({IMAGES}/{gid}/{filename})\n\n"
for gid, genre in genres.items():
    visual_page += f"## {genre['title']}\n\n| 作品 | 画面表現と読みやすさへの配慮 |\n| --- | --- |\n"
    for g in games:
        if g["genre"] == gid:
            visual_page += (
                f"| [{g['title']}]({g['id'].upper()}) | {visuals[g['id']]} |\n"
            )
    visual_page += "\n"
visual_page += "## 検証範囲\n\n掲載画像は所有するBASIC ROMから起動したエミュレーターの実フレームです。全作品のRAM配置・操作・ゲーム進行と、公開用WASMでの起動を確認しています。実機での表示・動作は未確認です。\n"
(WIKI / "Visual-Design.md").write_text(visual_page)
print(f"Generated {len(games)} game manuals and {len(genres)} genre navigation pages")

font_page = "# ゲーム専用フォント\n\n[ホーム](Home) → ゲーム専用フォント\n\n"
font_page += "51作品のPCG使用状況を調べ、統一した書体を揃えられる42作品に専用フォントを追加しました。41作品は数字0〜9の一式、WORD FOUNDRYは英大文字A〜Zの一式を使用します。残り9作品は通常フォントを維持しています。既存のロゴや立体的な絵柄を保ち、すべて標準RAM 16KB・PCG最大32文字に収めています。\n\n"
font_page += "英字と数字は作品に合う6系統で描き分けました。一つの単語の中で書体が混ざるような部分置換は行いません。タイトルの操作案内・説明・パスワード入力は通常フォントで統一しています。専用フォントはゲーム内に含まれます。数字の0には斜線を入れ、Oと区別しています。パスワードの文字種類と操作方法は変更していません。\n\n"
font_page += "| 系統 | 文字の特徴 |\n| --- | --- |\n"
for name, shape in STYLES.values():
    font_page += f"| {name} | {shape} |\n"
font_page += "\n## 代表的な画面\n\n"
for gid, caption in (
    ("seed-merge", "栽培槽と丸みのある数字"),
    ("circuit-works", "論理回路の計器文字"),
    ("word-foundry", "単語パズルの活字"),
    ("frost-steps", "氷の迷宮と結晶風の手数表示"),
):
    font_page += f"### [{gid.upper()}]({gid.upper()})\n\n![{caption}]({IMAGES}/{gid}/play-01.png)\n\n{caption}。\n\n"
for gid, genre in genres.items():
    font_page += f"## {genre['title']}\n\n| 作品 | フォント対応 |\n| --- | --- |\n"
    for game in games:
        if game["genre"] == gid:
            font_page += f"| [{game['title']}]({game['id'].upper()}) | {font_description(game)} |\n"
    font_page += "\n"
font_page += "## 検証範囲\n\nRAM配置、文字と絵柄のPCG枠の衝突、全文字コードの描画、タイトルとゲームの切り替え、操作リプレイを検証しています。掲載画像は所有するBASIC ROMから起動したエミュレーターの実フレームです。実機での表示と動作は未確認です。\n"
(WIKI / "Font-Design.md").write_text(font_page)

motion_page = "# 移動とクリア演出\n\n[ホーム](Home) → 移動とクリア演出\n\n"
motion_page += "連続移動の途中経過を表示する演出を6作品に追加しました。途中のマス、合成、敵の応答など、入力から結果までの流れを追えるようにしています。全51作品にクリア時のジングルと結果を見せる間を設けています。\n\n"
motion_page += f"## FROST STEPSの実画面\n\n![滑走から3つ星クリアまで]({IMAGES}/frost-steps/slide-clear.gif)\n\n[音付き動画]({BASE}/blob/main/games/frost_steps/images/slide-clear.mp4) · [プレイ]({PLAY}frost-steps)\n\n"
motion_page += "## 移動の途中経過\n\n| 作品 | 演出 |\n| --- | --- |\n"
for game_id, description in MOTION.items():
    motion_page += f"| [{game_id.upper().replace('-', ' ')}]({game_id.upper()}) | {description} |\n"
motion_page += "\n元から1マスずつ進む移動、時間を区切って進むアクション、カーソル選択、LOOP TENの意図したワープは、それぞれのテンポを保っています。追加した演出中の入力は捨て、次の行動が勝手に出ないようにしています。\n\n"
motion_page += "## クリア後の余韻\n\n最初の50作品は、完成した盤面と結果を残し、約1.6秒のジングルと余韻を挟んでから次の操作を受け付けます。曲は明るい結晶系、探索系、標準の3種類を作品に合わせて使います。押しっぱなしや演出中の入力では結果を飛ばしません。RELIC DIVEは容量に合わせた専用の約1.9秒のジングルを最終クリア時に鳴らします。通常プレイ中の効果音・BGMはありません。\n\n"
motion_page += "## 検証と録画\n\nすべて標準RAM 16KB内で、JR-100のCPUと音源を使って実行します。手数・盤面・評価、全ステージの入力リプレイ、途中フレーム、結果表示の保持、ジングルの音声出力と入力の抑止をエミュレーターで検査しています。掲載動画は所有するBASIC ROMから起動し、ゲームの状態を書き換えずに入力だけで録画しました。実機での表示・動作・音声は未確認です。\n\n"
motion_page += "```sh\nmake games-test\n.venv/bin/python games/frost_steps/capture_motion.py --rom /path/to/owned-rom.prg\n```\n"
(WIKI / "Motion-and-Clear.md").write_text(motion_page)
