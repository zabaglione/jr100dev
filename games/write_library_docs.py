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
    "fuse-box": "マスは面が細くなり、側面を見せてから反対の面が開く順に切り替わります。入／切の両方向に途中の形と効果音があります。",
    "frost-steps": "氷上を滑る途中の位置を細かく表示し、向きの変化と移動音で進路を追えます。1回の方向入力は、滑走距離にかかわらず1手です。",
    "gravity-well": "重力を変えると、球がマスの中間を通って転がり、止まるまでを表示します。複数の球が移動する順序も音とともに追えます。",
    "seed-merge": "種の移動、同じ種の合成、隙間を詰める移動、新しい種の出現を順に表示します。",
    "prism-trace": "鏡を回した後、光が通るマスを順に表示します。反射して進む経路を追えます。",
    "peg-garden": "選んだ駒が隣の駒を飛び越え、空いた穴に着地する様子を表示します。",
    "quiet-route": "探索者と警備員は進行方向を向き、マスの中間を通って移動します。探索者が動いてから警備員が応答するため、双方の行動を音とともに追えます。",
    "iron-script": "ロボットが進行方向を向き、マスの中間を通って移動します。移動音に合わせ、命令を実行する順序を追えます。",
    "magnet-vault": "ロボットは進行方向を向いて動きます。歩行と金属塊を引く動きには途中の位置と移動音があり、どの塊を動かしたか確認できます。",
    "glyph-shift": "探索者が進行方向を向き、マスの中間を通って移動します。移動音とともに一手の結果を確認できます。",
    "compass-rose": "探索者が進行方向を向き、マスの中間を通って移動します。移動音とともに進路を確認できます。",
    "mirror-relic": "探索者の向きと、マスの中間を通る移動を表示します。鏡を使う前後の位置を音とともに確認できます。",
    "ribbon-snake": "蛇の頭が進行方向を向きます。伸びた胴体と区別しながら、次に進む方向を確認できます。",
    "corner-crown": "挟んだ石は一枚ずつ、面が細くなって側面を見せ、反対の面が開く順に回転します。白から黒、黒から白の両方に途中の形と石返しの音があります。",
    "five-forge": "自分と相手が石を置く様子を一手ずつ表示します。着手音と短い間で、相手が置いた位置を確認できます。",
    "star-lance": "撃破した敵は、発光、中心の破片、外側へ散る破片を経て消えます。撃破音で命中を確認できます。",
    "night-swarm": "倒した敵は、発光して破片が外側へ散る順に消えます。接触時は被弾音と点滅が入り、危険な位置を確認できます。",
    "brick-pulse": "装甲やドローンに命中すると点滅します。破壊時は発光して破片が散り、命中と撃破の違いを音と画面で確認できます。",
    "echo-parry": "攻撃が当たると対象が点滅し、撃破時は発光して破片が散ります。防御を誤ると被弾音と短い停止が入り、失敗した方向を確認できます。",
}


def feedback_section(game):
    text = "## 動きとクリア演出\n\n"
    if game["id"] in MOTION:
        text += MOTION[game["id"]] + "演出中の追加入力は受け付けません。\n\n"
    duration = "約1.9秒" if game["id"] == "relic-dive" else "約1.6秒"
    text += f"クリア時は完成した盤面・結果を残し、{duration}のジングルと余韻を挟みます。失敗時も原因を表示し、ジングルの後に短い間を置きます。その後、キーを押し直して次の操作に進みます。直前から押し続けたキーや、演出中に押したキーで結果を飛ばすことはありません。\n\n"
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
        return f"通常文字のフォント変更は保留しています。タイトルはPCG27枠、ゲーム中は31枠を使用し、コード・定数の空きは{layout['code_free_bytes']}バイトです。ロゴ・地形・アイテムの判別を優先しています。"
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


def player_manual(text):
    """Keep game rules and screenshots in the public playing guide."""
    for heading in (
        "タイトルのデザイン",
        "画面の奥行き",
        "ゲーム専用フォント",
        "動きとクリア演出",
        "ビルドと検証",
        "対応と検証",
    ):
        text = re.sub(rf"\n## {heading}\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def with_media(text, game, local=False):
    report = json.loads((ROOT / game["directory"] / "images/play.json").read_text())
    text = re.sub(
        r"\n## 紹介画像とプレイ動画\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL
    )
    base = "images" if local else f"{IMAGES}/{game['id']}"
    url = f"https://zabaglione.github.io/pyjr100emu/gameplay.html?game={game['id']}"
    seconds = round(report["video_seconds"])
    outcomes = {
        "first stage cleared": "1ステージのクリアまで",
        "first two stages cleared": "最初の2ステージをクリアするまで",
        "first battle won": "最初の戦闘に勝利するまで",
        "first two chamber seals collected": "最初の2部屋の封印を回収するまで",
        "all five records recovered and returned to base": "5つの記録を回収し、基地へ帰還するまで",
        "first floor completed; entered floor 2": "最初の階を踏破し、2階へ進むまで",
    }
    block = (
        "\n## 紹介画像とプレイ動画\n\n"
        f"![開始時の盤面]({base}/demo-start.png)\n\n"
        f"![操作を進めた場面]({base}/demo-play.png)\n\n"
        f"![最初の目標を達成した場面]({base}/demo-clear.png)\n\n"
        f"**[音付きプレイ動画を見る（約{seconds}秒）]({url})**\n\n"
        f"{outcomes[report['outcome']]}を収録。\n"
    )
    position = text.find("\n## ")
    if position < 0:
        position = len(text.rstrip())
    return text[:position].rstrip() + "\n" + block + "\n" + text[position:].lstrip()


home = f"# JR-100 Games\n\n標準RAM 16KB向けのオリジナルゲーム{len(games)}作品です。ジャンルから選ぶと、各作品の画面・遊び方・起動リンクを探せます。\n\n各作品に3枚以上の紹介画像と約30秒の音付きプレイ動画を掲載しています。[全51作品の動画ギャラリー](https://zabaglione.github.io/pyjr100emu/gameplay.html)からも選べます。\n\n"
home += "| ジャンル | 作品数 | 内容 |\n| --- | ---: | --- |\n"
for gid, genre in genres.items():
    subset = [g for g in games if g["genre"] == gid]
    home += f"| [{genre['title']}]({page(gid)}) | {len(subset)} | {genre['description']} |\n"
home += (
    "\n[タイトル順の全作品](All-Games) · [タイトル画面ギャラリー](#タイトル画面ギャラリー) · [共通操作と起動方法](Controls)\n\n"
    + launch_note()
)
home += "\n\n基本の方向キーは **W/A/S/D**、8方向の作品は **QWE／AD／ZXC** です。作品ごとの操作は各ページに掲載しています。\n\nエミュレーターで確認済みです。実機での動作・音声は未確認です。\n\n"
home += f"[ビルド可能なソースと開発手順]({BASE}/tree/main/games)\n"
home += "\n**2026年9月18日更新：** タイトルの立体表現、開始・被弾・結果の音と間を更新しました。石返し、大きな駒の移動、敵の消滅にも途中の動きを加えています。[動きと音を動画で見る](Presentation)。\n"
home += "\n## タイトル画面ギャラリー\n\n"
for gid, genre in genres.items():
    home += f"### [{genre['title']}]({page(gid)})\n\n| タイトル画面 | ゲーム・概要 |\n| --- | --- |\n"
    for game in sorted(
        (g for g in games if g["genre"] == gid), key=lambda g: g["title"]
    ):
        game_id = game["id"]
        home += f'| [<img src="{IMAGES}/{game_id}/title.png" width="300" alt="{game["title"]}">]({game_id.upper()}) | **[{game["title"]}]({game_id.upper()})**<br>{game["summary"]}<br>[プレイ]({PLAY}{game_id}) · [遊び方を見る]({game_id.upper()}) |\n'
    home += "\n"
(WIKI / "Home.md").write_text(home.rstrip() + "\n")
sidebar = "[JR-100 Games](Home)\n\n"
for gid, genre in genres.items():
    sidebar += f"- [{genre['title']}]({page(gid)})\n"
sidebar += "\n[全作品をタイトル順に探す](All-Games)\n\n[タイトル画面ギャラリー](Home#タイトル画面ギャラリー)\n\n[動きと音の紹介](Presentation)\n\n[操作・起動方法](Controls)\n"
(WIKI / "_Sidebar.md").write_text(sidebar)
all_games = "# 全作品・タイトル順\n\n[ホーム](Home) · [ジャンルから探す](Home)\n\n| タイトル | ジャンル | ゲーム・概要 | 起動 |\n| --- | --- | --- | --- |\n"
for g in sorted(games, key=lambda g: g["title"]):
    all_games += f"| [{g['title']}]({g['id'].upper()}) | [{genres[g['genre']]['title']}]({page(g['genre'])}) | {g['summary']} | [プレイ]({PLAY}{g['id']}) |\n"
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

タイトルでRETURNまたはパッドのボタンを押すと開始します。説明画面の開き方やプレイ中の補助操作は[各作品のページ](Home)に掲載しています。RELIC DIVEはタイトルでW/Xにより難易度を選び、プレイ中のRETURNメニューからHELPを開きます。SPACEは戻る操作です。CTRL+Cでゲームを終了してBASICへ戻ります。

やり直しは「REALLY RESET?」で確認します。最初はNOが選ばれ、A/D（パッド左右）で選択、RETURN（ボタン）で確定します。SPACEでも取り消せます。確認中はゲーム進行を止めます。面選択への移動など、途中の盤面を捨てる操作も確認します。1手の取り消し、LOOP TENの巻き戻し、RELIC DIVEの中断・再開は通常操作として扱います。ブラウザのResetボタンも実行前に確認します。

ゲームは主な操作に1ボタンパッドも使えます。説明の表示、任意のタイミングでのやり直し、BASICへ戻る操作にはキーボードを使用します。

FROST STEPS、MAGNET VAULT、GLYPH SHIFT、GRAVITY WELLは40面と星評価に対応しています。Fで面選択、WASDで選択、RETURNで開始、SPACEでタイトルへ戻ります。面選択は最初から全40面を選べます。クリア画面のSPACEは同じ面の再挑戦、RETURNは次の面です。終了前にタイトル／面選択のPWを書き留めると、次回Xから面番号と全40面の最高評価を復元できます。

## 開始・移動・結果の演出中の入力

開始時はSEと画面中央のGAME STARTを挟みます。作品によっては地形、目標、自分、敵の順に画面が現れます。表示が終わってから操作してください。開始演出中は制限時間を消費しません。

移動や石返しの途中、被弾・撃破・クリア直後は、次の操作まで少し間があります。被弾時は対象が点滅し、失敗時は原因を表示してジングルを流します。演出と音が終わってからキーを押し直してください。演出中の入力は次の手に持ち越しません。

[動きと音の紹介](Presentation)で、石返しや撃破の様子を確認できます。

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
        path.write_text(with_media(player_manual(text), g))
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
        readme_path.write_text(with_media(readme_text, g, local=True))
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
    if g["id"] in MOTION:
        body += MOTION[g["id"]] + "演出が終わってから次のキーを押してください。\n\n"
    body += f"{hud}\n\n![ゲーム開始時]({IMAGES}/{g['id']}/play-01.png)\n\n![プレイ中の場面]({IMAGES}/{g['id']}/play-02.png)\n\n"
    if g["id"] == "brick-pulse":
        body += f"![落下アイテム]({IMAGES}/brick-pulse/items.png)\n\n![後半のドローンと装甲ブロック]({IMAGES}/brick-pulse/drone.png)\n\n![やり直し確認]({IMAGES}/brick-pulse/reset.png)\n\n"
    if meta.get("rankedCampaign"):
        levels = json.loads((directory / "levels.json").read_text())
        body += "## 手数と星評価\n\n規定手数を超えても失敗にはならず、そのままクリアできます。ルーンは丸い枠に十字の印がある任意の回収物で、各面に2つあります。\n\n"
        body += "| 評価 | 条件 |\n| --- | --- |\n| 星1 | 規定手数を超えてクリア。ルーンの回収数は問いません。 |\n| 星2 | 規定手数以内でクリアし、ルーンが未回収。 |\n| 星3 | 規定手数以内でクリアし、ルーン2つを両方回収。 |\n\n"
        body += "PARは、両方のルーンを回収してクリアできる最短手数です。すべての面に、ルーンを取り切らずに短い手数でクリアする経路もあります。手数が255を超えるとMOVは255+を表示し、評価は星1です。\n\n"
        body += f"![3つ星クリア]({IMAGES}/{g['id']}/three-stars.png)\n\n"
        body += "## 40面の構成と再挑戦\n\n| 面 | 難度の段階 | PARの範囲 |\n| --- | --- | ---: |\n"
        for i, tier in enumerate(("入門", "基本", "応用", "上級", "最終課題")):
            pars = [v[69] for v in levels[i * 8 : (i + 1) * 8]]
            body += (
                f"| {i * 8 + 1}〜{i * 8 + 8} | {tier} | {min(pars)}〜{max(pars)} |\n"
            )
        body += "\nFで面選択を開き、WASDまたはパッドで選び、RETURNまたはボタンで開始します。全40面を最初から選択でき、選択した面のPARと各面の最高評価を確認できます。面選択のSPACEはタイトルへ戻ります。\n\nクリア後はSPACEで同じ面に再挑戦、RETURNで次の面へ進みます。BESTは最高評価、NOWは今回の評価です。低い評価で再クリアしてもBESTは下がりません。ゲーム終了後も続ける場合は、次のパスワードを記録してください。\n\n"
        body += f"![40面の最高評価一覧]({IMAGES}/{g['id']}/stage-select.png)\n\n"
        body += "## パスワードで続きから\n\nタイトルと面選択の下部に表示される **PW** を書き留めてください。選択中の面番号と、全40面の最高評価を復元できます。盤面の途中経過は保存せず、復元後にRETURNでその面の最初から再開します。\n\nコードは空白を除いて **4〜24文字**。順番に3つ星を取って進める場合は通常5〜6文字です。数字は使わず、次の16種類の大文字だけを使います。\n\n```text\nACDEFGHJKMNPQRTW\n```\n\n1. タイトルまたは面選択でXを押します。\n2. コードを入力し、RETURNで復元します。表示上の区切り空白は入力しても省略しても構いません。\n3. 修正はBackspace（実機ではマイナスキー）、取り消しはXです。\n\n入力画面ではパッドの方向で文字を選び、ボタンで追加する方法も使えます。最後にLOADを選んでボタンを押すと復元します。DELは1文字削除、BACKは取り消しです。入力ミスや別作品のコードを検査し、エラー時は現在の記録を変更しません。\n\n"
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
    (WIKI / (g["id"].upper() + ".md")).write_text(
        with_media(player_manual(prefix + body), g)
    )
    readme = f"# {g['title']}\n\n[Wiki]({BASE}/wiki/{g['id'].upper()}) · [プレイ]({PLAY}{g['id']})\n\n"
    readme += body.replace(f"{IMAGES}/{g['id']}/", "images/")
    (directory / "README.md").write_text(with_media(readme, g, local=True))
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
