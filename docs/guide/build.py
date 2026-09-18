"""Build the bilingual player guide from Wiki originals and reviewed English text."""

import argparse
import hashlib
import html
import json
import re
import shutil
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
md = MarkdownIt("commonmark", {"html": False}).enable("table")


def pair(en, ja):
    return {"en": en, "ja": ja}


def bilingual(values):
    return "".join(
        f'<span lang="{lang}" data-language="{lang}">{html.escape(values[lang])}</span>'
        for lang in LANGUAGES
    )


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
    nav = (
        '<a data-guide-link href="index.html">'
        + bilingual(pair("All games", "全作品"))
        + "</a>"
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
            "Made for the JR-100 with standard 16 KB RAM. Emulator-tested; real hardware is unverified.",
            "標準RAM 16KBのJR-100向け。エミュレーターで検証済みです。実機での動作・音声は未確認です。",
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
  <link rel="stylesheet" href="style.css">
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
  <footer class="wrap"><p>{footer}</p><a href="{BASE}/wiki">Wiki</a> · <a href="{BASE}/tree/main/games">Source / MIT License</a></footer>
</body>
</html>
'''


def game_page(game, english, metadata, game_ids):
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
    body = f'''<section class="hero">
      <p class="breadcrumbs"><a data-guide-link href="index.html">{bilingual(pair("All games", "全作品"))}</a> / {bilingual(pair(metadata["genres"][game["genre"]], metadata["genres_ja"][game["genre"]]))}</p>
      <h1>{title}</h1>{intro}
      <nav class="actions"><a class="button primary" href="../?game={gid}">{bilingual(pair("Play this game", "このゲームをプレイ"))}</a><a href="{BASE}/tree/main/games/{game["directory"]}">{bilingual(pair("Source", "ソース"))}</a></nav>
      <p class="note">{bilingual(pair("To play, set up your own BASIC ROM in the emulator once. Screenshots and videos need no ROM.", "プレイにはエミュレーターで自分のBASIC ROMを一度設定してください。画像と動画の閲覧にはROMは不要です。"))} <a data-guide-link href="controls.html">{bilingual(pair("Setup and controls", "設定と共通操作"))}</a></p>
    </section>
    <section class="media" aria-label="Screenshots and video">
      <div class="shots">{shots}</div>
      <p class="video-link"><a class="button" href="../gameplay.html?game={gid}#video">{video}</a></p>
      <p class="note">{bilingual(video_note)}</p>
    </section>{contents}'''
    return shell(
        gid + ".html",
        pair(game["title"], game["title"]),
        body,
        pair(metadata["summaries"][gid], game["summary"]),
    )


def index_page(games, metadata):
    title = pair("Find your next game", "次に遊ぶゲームを探す")
    intro = pair(
        f"{len(games)} original games for the JR-100. Browse the screenshots, read the rules, and play in your browser.",
        f"JR-100のオリジナルゲーム{len(games)}作品。画面と遊び方を見て、ブラウザーからすぐに遊べます。",
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
          <a data-guide-link href="{gid}.html">{bilingual(pair("How to play", "遊び方を見る"))}</a></div>
        </article>''')
    body = f"""<section class="hero"><p class="eyebrow">51 GAMES / 16 KB</p><h1>{bilingual(title)}</h1><p class="intro">{bilingual(intro)}</p></section>
      <div class="filters"><div class="search-field"><label for="search">{bilingual(pair("Find a game", "タイトル・内容から探す"))}</label><input type="search" id="search" autocomplete="off"></div>
      <div><label for="genre">{bilingual(pair("Genre", "ジャンル"))}</label><select id="genre">{options}</select></div>
      <button type="button" id="clear-search">{bilingual(pair("Clear filters", "絞り込みを解除"))}</button></div>
      <p class="note" id="match-count" role="status">51 games</p>
      <p id="no-results" hidden>{bilingual(pair("No games found. Try another title or clear the filters.", "該当する作品がありません。別の語句に変えるか、絞り込みを解除してください。"))}</p>
      <div class="grid">{"".join(cards)}</div>"""
    return shell("index.html", title, body, intro)


def build(destination):
    library = json.loads((ROOT / "games/library.json").read_text())
    games = library["games"]
    metadata = json.loads((HERE / "en/catalog.json").read_text())
    metadata["genres_ja"] = {g["id"]: g["title"] for g in library["genres"]}
    ids = {g["id"] for g in games}
    if set(metadata["summaries"]) != ids:
        raise ValueError("English catalogue must cover every published game")
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
        pages[gid + ".html"] = game_page(game, english, metadata, ids)
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
    for name, content in pages.items():
        (destination / name).write_text(content)
    for name in ("language.js", "guide.js", "style.css"):
        shutil.copyfile(HERE / "assets" / name, destination / name)
    shutil.copyfile(ROOT / "games/LICENSE", destination / "LICENSE.txt")
    files = {
        name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
        for name in sorted(
            [*pages, "language.js", "guide.js", "style.css", "LICENSE.txt"]
        )
    }
    (destination / "manifest.json").write_text(
        json.dumps({"schemaVersion": 1, "games": sorted(ids), "files": files}, indent=2)
        + "\n"
    )
    print(f"Built {len(games)} bilingual game guides and getting-started pages")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    build(parser.parse_args().destination)
