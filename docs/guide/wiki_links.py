"""Keep existing Wiki URLs while linking each page to the bilingual guide."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = "https://zabaglione.github.io/pyjr100emu/guide/"


def update_wiki_links():
    games = {
        g["id"] for g in json.loads((ROOT / "games/library.json").read_text())["games"]
    }
    for path in (ROOT / "docs/wiki").glob("*.md"):
        slug = path.stem.lower()
        target = slug + ".html" if slug in games or slug == "controls" else ""
        link = f"> [Read this guide in English / 日本語のゲームガイド]({BASE}{target})"
        text = re.sub(
            r"^> \[Read this guide[^\n]*\n\n?", "", path.read_text(), flags=re.MULTILINE
        )
        if path.name == "_Sidebar.md":
            text = link + "\n\n" + text
        else:
            first, rest = text.split("\n", 1)
            text = first + "\n\n" + link + "\n" + rest
        path.write_text(text)
    print("Updated Wiki links to the bilingual guides")


if __name__ == "__main__":
    update_wiki_links()
