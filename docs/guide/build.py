"""Build the bilingual player guide from Wiki originals and reviewed English text."""

import argparse
import hashlib
import html
import json
import re
import shutil
import struct
import zipfile
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIKI = ROOT / "docs/wiki"
BASE = "https://github.com/zabaglione/jr100dev"
WIKI_BASE = BASE + "/wiki/"
IMAGE_BASE = "https://raw.githubusercontent.com/wiki/zabaglione/jr100dev/images"
PUBLIC = "https://zabaglione.github.io/pyjr100emu/guide/"
LANGUAGES = ("en", "ja")
BUNDLE = "downloads/jr100-games-mister.zip"
md = MarkdownIt("commonmark", {"html": False}).enable("table")


def pair(en, ja):
    return {"en": en, "ja": ja}


def bilingual(values):
    return "".join(
        f'<span lang="{lang}" data-language="{lang}">{html.escape(values[lang])}</span>'
        for lang in LANGUAGES
    )


def autostart_program(data, entry):
    """Preserve PROG v2 sections and add the MiSTer CMNT launch hint."""
    if data[:8] != b"PROG\x02\x00\x00\x00" or entry != 0x0300:
        raise ValueError("MiSTer downloads require PROG v2 with entry $0300")
    result, comments, offset = bytearray(data[:8]), [], 8
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError("Truncated PROG section")
        tag = data[offset : offset + 4]
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        if end > len(data):
            raise ValueError("Truncated PROG payload")
        payload = data[offset + 8 : end]
        if tag == b"CMNT":
            if (
                len(payload) < 4
                or struct.unpack_from("<I", payload)[0] != len(payload) - 4
            ):
                raise ValueError("Invalid PROG comment")
            comments.append(
                re.sub(r"USR=\$[0-9A-Fa-f]{4}", "", payload[4:].decode("utf-8")).strip()
            )
        else:
            result.extend(data[offset:end])
        offset = end
    note = " ".join([f"USR=${entry:04X}", *(text for text in comments if text)]).encode(
        "utf-8"
    )
    payload = struct.pack("<I", len(note)) + note
    return bytes(result) + b"CMNT" + struct.pack("<I", len(payload)) + payload


def published_programs(folder, ids):
    catalog = json.loads((folder / "catalog.json").read_text())
    entries = catalog.get("games", [])
    if (
        catalog.get("schemaVersion") != 1
        or len(entries) != len(ids)
        or {g["id"] for g in entries} != ids
    ):
        raise ValueError("Published game catalog must cover every guide exactly once")
    result = {}
    for game in entries:
        gid, version = game["id"], game["version"]
        expected = f"games/{gid}/{version}/{gid}.prg"
        if (
            not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version)
            or game["path"] != expected
            or game["ramKiB"] != 16
        ):
            raise ValueError("Invalid published program path or RAM")
        source = folder.parent / expected
        if not source.resolve().is_relative_to(folder.resolve()) or source.is_symlink():
            raise ValueError("Program must stay inside the published games directory")
        data = source.read_bytes()
        if hashlib.sha256(data).hexdigest() != game["sha256"]:
            raise ValueError("Published program hash mismatch")
        result[gid] = game | {"data": autostart_program(data, game["entry"])}
    return result


def launch_steps():
    return [
        pair(
            "Copy the .prg into games/JR100/ on your SD card.",
            ".prgをSDカードのgames/JR100/へコピーします。",
        ),
        pair(
            "In the JR-100 core menu, set Autostart loaded program to Yes.",
            "JR-100コアのメニューでAutostart loaded programをYesにします。",
        ),
        pair(
            "Choose Load PRG, select the game, then press RETURN at its title.",
            "Load PRGでゲームを選び、タイトル画面でRETURNを押します。",
        ),
    ]


def quickstart(collapsed=False):
    steps = "".join(f"<li>{bilingual(step)}</li>" for step in launch_steps())
    content = f"""<section class="quickstart" aria-labelledby="mister-start">
      <h2 id="mister-start">{bilingual(pair("Start on MiSTer", "MiSTerで起動"))}</h2>
      <ol>{steps}</ol>
      <p class="note">{bilingual(pair("Still at READY? Type", "READYで止まる場合は"))} <code>A=USR($0300)</code> {bilingual(pair("and press RETURN.", "を入力してRETURN。"))}
      <a data-guide-link href="mister.html">{bilingual(pair("First-time setup / SuperStation One", "初回設定・SuperStation Oneの手順"))}</a></p>
    </section>"""
    if collapsed:
        heading = bilingual(
            pair("Start on MiSTer in 3 steps", "MiSTerで起動する3ステップ")
        )
        return f'<details class="quickstart-fold"><summary>{heading}</summary>{content}</details>'
    return content


def download_link(gid, label=None):
    return f'<a class="button primary" href="downloads/{gid}.prg" download="{gid}.prg">{bilingual(label or pair("Download .prg (MiSTer)", "MiSTer用 .prgを保存"))}</a>'


def bundle_link():
    return f'<a class="button primary" href="{BUNDLE}" download="jr100-games-mister.zip">{bilingual(pair("Download all 51 games (.zip)", "全51作品をまとめて保存（ZIP）"))}</a>'


def write_downloads(destination, programs):
    folder = destination / "downloads"
    folder.mkdir(exist_ok=True)
    files = {}
    for gid, game in sorted(programs.items()):
        files[f"{gid}.prg"] = game["data"]
    for lang in LANGUAGES:
        files[f"README-{lang}.txt"] = (
            HERE / "download-readme" / f"{lang}.txt"
        ).read_bytes()
    for name, data in files.items():
        (folder / name).write_bytes(data)
    files["LICENSE.txt"] = (ROOT / "games/LICENSE").read_bytes()
    with zipfile.ZipFile(
        destination / BUNDLE, "w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("JR100/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return [BUNDLE, *("downloads/" + name for name in files if name != "LICENSE.txt")]


def japanese_manual(game):
    """Remove only shared navigation/media; retain every game-specific rule."""
    text = (WIKI / (game["id"].upper() + ".md")).read_text()
    text = re.sub(
        r"\n## 紹介画像とプレイ動画\n.*?(?=\n## |\Z)", "\n", text, flags=re.DOTALL
    )
    lines = text.splitlines()
    kept = []
    for line in lines:
        if line.startswith(
            ("# ", "[ホーム]", "[プレイ]", "**[プレイ]", "同じブラウザー")
        ):
            continue
        if line.startswith("> [Read this guide"):
            continue
        if line.startswith("![") and line.endswith("/title.png)"):
            continue
        kept.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip() + "\n"


def split_intro(text):
    match = re.search(r"^## ", text, re.MULTILINE)
    if not match:
        raise ValueError("A manual needs an introduction and rules")
    return text[: match.start()], text[match.start() :]


def japanese_controls():
    text = (WIKI / "Controls.md").read_text()
    lines = [
        line
        for line in text.splitlines()
        if not line.startswith(("# ", "[ホーム]", "> [Read this guide"))
    ]
    return "\n".join(lines).strip().replace("Wiki", "ガイド") + "\n"


def english_extras(game, english):
    meta = json.loads((ROOT / "games" / game["directory"] / "game.json").read_text())
    if "<!-- common-controls -->" in english:
        reset = (
            "SPACE is disabled during play. After failure, RETURN opens the retry confirmation."
            if meta.get("disableSpaceReset")
            else "SPACE opens confirmation to restart all six fields; confirming resets to the first field, 108 drops, and 0 points."
            if meta.get("carryCampaign")
            else "SPACE opens a new-game confirmation; confirming resets the board and score."
            if meta.get("endless")
            else "SPACE opens confirmation to restart this stage."
        )
        common = (
            "Directions work on the keyboard or pad; the pad button also acts as RETURN. "
            + reset
        )
        common += " NO is selected initially. Choose with A/D, confirm with RETURN, or cancel with SPACE. Play pauses during confirmation. CTRL+C returns to BASIC."
        english = english.replace("<!-- common-controls -->", common)
    if "<!-- ranked-campaign -->" in english:
        levels = json.loads(
            (ROOT / "games" / game["directory"] / "levels.json").read_text()
        )
        table = "| Stages | Difficulty | PAR range |\n| --- | --- | ---: |\n"
        for i, tier in enumerate(
            ("Introduction", "Basics", "Applied", "Advanced", "Final challenges")
        ):
            pars = [v[69] for v in levels[i * 8 : (i + 1) * 8]]
            table += f"| {i * 8 + 1}–{i * 8 + 8} | {tier} | {min(pars)}–{max(pars)} |\n"
        ranked = (
            (HERE / "en/ranked.md").read_text().replace("<!-- par-table -->", table)
        )
        english = english.replace("<!-- ranked-campaign -->", ranked)
    missing = []
    for url in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", japanese_manual(game)):
        if url not in english:
            label = Path(url).stem.replace("-", " ")
            missing.append(f"![{game['title']}: {label}]({url})")
    if missing:
        english += "\n## More screenshots\n\n" + "\n\n".join(missing) + "\n"
    return english


def rewrite_link(url, game_ids):
    url = url.removeprefix(WIKI_BASE)
    page, _, fragment = url.partition("#")
    if page.lower() in game_ids:
        return page.lower() + ".html", True
    if page in ("Home", "All-Games") or page.startswith("Genre-"):
        return "index.html", True
    if page == "Controls":
        return "controls.html", True
    if page in ("Presentation", "Second-Review", "Quality-Review"):
        return WIKI_BASE + page + ("#" + fragment if fragment else ""), False
    return url, False


def render(text, game_ids):
    tokens = md.parse(text)
    for token in tokens:
        for child in token.children or []:
            if child.type == "link_open":
                href, internal = rewrite_link(child.attrGet("href"), game_ids)
                child.attrSet("href", href)
                if internal:
                    child.attrSet("data-guide-link", "")
            elif child.type == "image":
                child.attrSet("loading", "lazy")
                child.attrSet("decoding", "async")
    return (
        md.renderer.render(tokens, md.options, {})
        .replace("<table>", '<div class="table-scroll"><table>')
        .replace("</table>", "</table></div>")
    )


def shell(name, titles, content, descriptions):
    stylesheet_version = hashlib.sha256(
        (HERE / "assets/style.css").read_bytes()
    ).hexdigest()[:12]
    nav = (
        '<a data-guide-link href="index.html">'
        + bilingual(pair("All games", "全作品"))
        + "</a>"
        '<a data-guide-link href="mister.html">MiSTer FPGA</a>'
        '<a data-guide-link href="controls.html">'
        + bilingual(pair("Getting started", "操作と起動方法"))
        + "</a>"
        '<a href="../gameplay.html">'
        + bilingual(pair("Gameplay videos", "プレイ動画"))
        + "</a>"
        '<a href="../">' + bilingual(pair("Emulator", "エミュレーター")) + "</a>"
    )
    footer = bilingual(
        pair(
            "Made for the JR-100 with standard 16 KB RAM. See MiSTer FPGA for hardware test coverage.",
            "標準RAM 16KBのJR-100向け。SS1実機での確認範囲はMiSTer FPGAのページに掲載しています。",
        )
    )
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(titles["en"])} · JR-100 Games</title>
  <meta name="title-en" content="{html.escape(titles["en"], quote=True)} · JR-100 Games">
  <meta name="title-ja" content="{html.escape(titles["ja"], quote=True)} · JR-100 Games">
  <meta name="description" content="{html.escape(descriptions["en"], quote=True)}">
  <meta name="description-en" content="{html.escape(descriptions["en"], quote=True)}">
  <meta name="description-ja" content="{html.escape(descriptions["ja"], quote=True)}">
  <link rel="canonical" href="{PUBLIC}{name}">
  <link rel="alternate" hreflang="en" href="{PUBLIC}{name}?lang=en">
  <link rel="alternate" hreflang="ja" href="{PUBLIC}{name}?lang=ja">
  <link rel="alternate" hreflang="x-default" href="{PUBLIC}{name}">
  <script src="language.js"></script>
  <link rel="stylesheet" href="style.css?v={stylesheet_version}">
  <script src="guide.js" defer></script>
</head>
<body>
  <a class="skip" href="#main">{bilingual(pair("Skip to content", "本文へ"))}</a>
  <header class="wrap masthead">
    <a class="brand" data-guide-link href="index.html">JR-100 GAMES</a>
    <nav class="languages" aria-label="Language / 言語">
      <a data-language-switch href="?lang=en" hreflang="en" lang="en">English</a>
      <a data-language-switch href="?lang=ja" hreflang="ja" lang="ja">日本語</a>
    </nav>
  </header>
  <div class="wrap"><nav class="utility">{nav}</nav></div>
  <main class="wrap" id="main">{content}</main>
  <footer class="wrap"><p>{footer} <a data-guide-link href="mister.html">MiSTer FPGA</a></p><p>{bilingual(pair("RELIC DIVE co-developed with JR-800 Web Emulator contributors.", "RELIC DIVEはJR-800 Web Emulator contributorsとの共同制作です。"))}</p><a href="{BASE}/wiki">Wiki</a> · <a href="LICENSE.txt">MIT License</a> · <a href="{BASE}/tree/main/games">Source</a></footer>
</body>
</html>
'''


def game_page(game, english, metadata, game_ids, program):
    gid = game["id"]
    title = html.escape(game["title"])
    texts = {"en": english_extras(game, english), "ja": japanese_manual(game)}
    parts = {lang: split_intro(texts[lang]) for lang in LANGUAGES}
    intro = "".join(
        f'<div class="intro" data-language="{lang}" lang="{lang}">{render(parts[lang][0], game_ids)}</div>'
        for lang in LANGUAGES
    )
    contents = "".join(
        f'<article class="manual" data-language="{lang}" lang="{lang}">{render(parts[lang][1], game_ids)}</article>'
        for lang in LANGUAGES
    )
    captions = [
        pair("At the start", "開始時の盤面"),
        pair("In play", "プレイ中"),
        pair("First goal reached", "最初の目標を達成"),
    ]
    shots = "".join(
        f'<figure><a href="../game-media/{gid}/{filename}"><img src="../game-media/{gid}/{filename}" width="816" height="624" alt="{title} — {caption["en"]}" loading="lazy"></a><figcaption>{bilingual(caption)}</figcaption></figure>'
        for filename, caption in zip(
            ("demo-start.png", "demo-play.png", "demo-clear.png"), captions
        )
    )
    report = json.loads(
        (ROOT / "games" / game["directory"] / "images/play.json").read_text()
    )
    seconds = round(report["video_seconds"])
    video = bilingual(
        pair(
            f"Watch gameplay with sound ({seconds} seconds)",
            f"音付きプレイ動画を見る（約{seconds}秒）",
        )
    )
    outcomes = metadata["outcomes"][report["outcome"]]
    video_note = pair(report["outcome"].capitalize() + ".", outcomes + "を収録。")
    if report["edited"]:
        video_note = pair(
            "Highlights; omitted sections are marked LATER.",
            "ダイジェスト。省略箇所にはLATERを表示します。",
        )
    body = f"""<section class="hero">
      <p class="breadcrumbs"><a data-guide-link href="index.html">{bilingual(pair("All games", "全作品"))}</a> / {bilingual(pair(metadata["genres"][game["genre"]], metadata["genres_ja"][game["genre"]]))}</p>
      <h1>{title}</h1>{intro}
      <nav class="actions">{download_link(gid)}<a class="button" href="../?game={gid}">{bilingual(pair("Play in browser", "ブラウザーで遊ぶ"))}</a></nav>
      <p class="note"><code>{gid}.prg</code> · v{program["version"]} · {len(program["data"]) / 1024:.1f} KiB · 16 KB RAM · {bilingual(pair("Autostart ready", "自動起動対応"))}</p>
    </section>{quickstart()}
    <section class="media" aria-label="Screenshots and video">
      <div class="shots">{shots}</div>
      <p class="video-link"><a class="button" href="../gameplay.html?game={gid}#video">{video}</a></p>
      <p class="note">{bilingual(video_note)}</p>
    </section>{contents}"""
    return shell(
        gid + ".html",
        pair(game["title"], game["title"]),
        body,
        pair(metadata["summaries"][gid], game["summary"]),
    )


def index_page(games, metadata):
    title = pair("Find your next game", "次に遊ぶゲームを探す")
    intro = pair(
        f"{len(games)} games for the JR-100. Find a game, download its .prg for MiSTer FPGA, or try it in your browser.",
        f"JR-100のゲーム{len(games)}作品。遊びたい作品の.prgをMiSTer FPGA用に保存したり、ブラウザーで試したりできます。",
    )
    options = (
        '<option value="" data-en="All genres" data-ja="全ジャンル">All genres</option>'
        + "".join(
            f'<option value="{key}" data-en="{html.escape(value, quote=True)}" data-ja="{metadata["genres_ja"][key]}">{html.escape(value)}</option>'
            for key, value in metadata["genres"].items()
        )
    )
    cards = []
    for game in sorted(games, key=lambda g: g["title"]):
        gid = game["id"]
        cards.append(f'''<article class="game-card" data-genre="{game["genre"]}">
          <a class="cover" data-guide-link href="{gid}.html"><img src="../game-media/{gid}/demo-play.png" width="816" height="624" alt="{html.escape(game["title"])}" loading="lazy"></a>
          <div class="card-body"><span class="genre">{bilingual(pair(metadata["genres"][game["genre"]], metadata["genres_ja"][game["genre"]]))}</span>
          <h2><a data-guide-link href="{gid}.html">{html.escape(game["title"])}</a></h2>
          <p>{bilingual(pair(metadata["summaries"][gid], game["summary"]))}</p>
          <nav class="card-actions">{download_link(gid)}<a href="../?game={gid}">{bilingual(pair("Play in browser", "ブラウザーで遊ぶ"))}</a><a data-guide-link href="{gid}.html">{bilingual(pair("How to play", "遊び方を見る"))}</a></nav></div>
        </article>''')
    body = f"""<section class="hero library-hero"><p class="eyebrow">51 GAMES / 16 KB</p><h1>{bilingual(title)}</h1><p class="intro">{bilingual(intro)}</p>
      <nav class="actions">{bundle_link()}<a data-guide-link href="mister.html">{bilingual(pair("How to start on MiSTer", "MiSTerでの起動方法"))}</a></nav>
      <p class="note">{bilingual(pair("Unzip, then copy the JR100 folder into games/ on your SD card. Includes launch instructions and license.", "ZIPを展開し、JR100フォルダーをSDカードのgames/へコピー。起動手順とライセンスも同梱しています。"))}</p></section>
      {quickstart(collapsed=True)}
      <div class="filters"><div class="search-field"><label for="search">{bilingual(pair("Find a game", "タイトル・内容から探す"))}</label><input type="search" id="search" autocomplete="off"></div>
      <div><label for="genre">{bilingual(pair("Genre", "ジャンル"))}</label><select id="genre">{options}</select></div>
      <button type="button" id="clear-search">{bilingual(pair("Clear filters", "絞り込みを解除"))}</button></div>
      <p class="note" id="match-count" role="status">51 games</p>
      <p id="no-results" hidden>{bilingual(pair("No games found. Try another title or clear the filters.", "該当する作品がありません。別の語句に変えるか、絞り込みを解除してください。"))}</p>
      <div class="grid">{"".join(cards)}</div>"""
    return shell("index.html", title, body, intro)


def build(destination, games_folder=None):
    library = json.loads((ROOT / "games/library.json").read_text())
    games = library["games"]
    metadata = json.loads((HERE / "en/catalog.json").read_text())
    metadata["genres_ja"] = {g["id"]: g["title"] for g in library["genres"]}
    ids = {g["id"] for g in games}
    if set(metadata["summaries"]) != ids:
        raise ValueError("English catalogue must cover every published game")
    programs = published_programs(games_folder or destination.parent / "games", ids)
    source_hashes = json.loads((HERE / "translation-sources.json").read_text())
    destination.mkdir(parents=True, exist_ok=True)
    pages = {"index.html": index_page(games, metadata)}
    for game in games:
        gid = game["id"]
        source_hash = hashlib.sha256(japanese_manual(game).encode()).hexdigest()
        if source_hashes.get(gid) != source_hash:
            raise ValueError(
                f"Review the English translation after Japanese changes: {gid}"
            )
        english = (HERE / "en" / (gid + ".md")).read_text()
        if re.search(r"[\u3040-\u30ff\u3400-\u9fff]", english):
            raise ValueError(f"Untranslated Japanese in English guide: {gid}")
        pages[gid + ".html"] = game_page(game, english, metadata, ids, programs[gid])
    controls_ja = japanese_controls()
    if (
        source_hashes.get("controls")
        != hashlib.sha256(controls_ja.encode()).hexdigest()
    ):
        raise ValueError(
            "Review the English translation after Japanese changes: controls"
        )
    controls_en = (HERE / "en/controls.md").read_text()
    controls_body = "".join(
        f'<article class="manual" data-language="{lang}" lang="{lang}">{render(text, ids)}</article>'
        for lang, text in (("en", controls_en), ("ja", controls_ja))
    )
    title = pair("Getting started", "操作と起動方法")
    pages["controls.html"] = shell(
        "controls.html",
        title,
        '<section class="hero"><h1>'
        + bilingual(title)
        + "</h1></section>"
        + controls_body,
        title,
    )
    mister_body = "".join(
        f'<article class="manual" data-language="{lang}" lang="{lang}">{render((HERE / lang / "mister.md").read_text(), ids)}</article>'
        for lang in LANGUAGES
    )
    title = pair("Play on MiSTer FPGA", "MiSTer FPGAで遊ぶ")
    pages["mister.html"] = shell(
        "mister.html",
        title,
        '<section class="hero"><h1>'
        + bilingual(title)
        + '</h1><nav class="actions">'
        + bundle_link()
        + "</nav></section>"
        + quickstart()
        + mister_body,
        title,
    )
    for name, content in pages.items():
        (destination / name).write_text(content)
    for name in ("language.js", "guide.js", "style.css"):
        shutil.copyfile(HERE / "assets" / name, destination / name)
    shutil.copyfile(ROOT / "games/LICENSE", destination / "LICENSE.txt")
    downloads = write_downloads(destination, programs)
    files = {
        name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
        for name in sorted(
            [*pages, *downloads, "language.js", "guide.js", "style.css", "LICENSE.txt"]
        )
    }
    (destination / "manifest.json").write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "games": sorted(ids),
                "files": files,
                "sourcePrograms": [
                    {
                        k: programs[gid][k]
                        for k in ("id", "path", "version", "entry", "sha256")
                    }
                    for gid in sorted(ids)
                ],
            },
            indent=2,
        )
        + "\n"
    )
    print(f"Built {len(games)} bilingual game guides and getting-started pages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument(
        "--games",
        type=Path,
        help="Published games directory; defaults to ../games next to the guide",
    )
    args = parser.parse_args()
    build(args.destination, args.games)
