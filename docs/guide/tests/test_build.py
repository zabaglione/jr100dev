"""Player-guide completeness, links, and translation freshness checks."""

import importlib.util
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import pytest

SPEC = importlib.util.spec_from_file_location(
    "guide_build", Path(__file__).parents[1] / "build.py"
)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.media = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a":
            self.links.append(values.get("href", ""))
        if tag == "img":
            self.media.append(values)


def test_all_games_have_both_languages_media_and_valid_navigation(tmp_path):
    builder.build(tmp_path)
    ids = json.loads((tmp_path / "manifest.json").read_text())["games"]
    assert len(ids) == 51
    assert len(list(tmp_path.glob("*.html"))) == 53
    for gid in ids:
        text = (tmp_path / f"{gid}.html").read_text()
        assert '<html lang="en">' in text
        for language in ("en", "ja"):
            assert f'<article class="manual" data-language="{language}"' in text
            assert f'hreflang="{language}"' in text
        english = text.split('<article class="manual" data-language="en" lang="en">')[
            1
        ].split("</article>")[0]
        assert not re.search(r"[\u3040-\u30ff\u3400-\u9fff]", english)
        assert "&lt;!--" not in english
        assert (
            text.index("demo-start.png")
            < text.index("demo-play.png")
            < text.index("demo-clear.png")
            < text.index(f"../gameplay.html?game={gid}#video")
        )
        page = Page(text)
        assert len({image["src"] for image in page.media}) >= 3
        assert all(image.get("alt") for image in page.media)
        assert f"../?game={gid}" in page.links
    for path in tmp_path.glob("*.html"):
        for link in Page(path.read_text()).links:
            target = urlsplit(link)
            assert target.scheme in ("", "https")
            if not target.scheme and target.path and not target.path.startswith("../"):
                assert (tmp_path / target.path).is_file(), (path.name, link)


def test_japanese_rule_changes_require_translation_review(tmp_path, monkeypatch):
    original = builder.japanese_manual
    monkeypatch.setattr(
        builder, "japanese_manual", lambda game: original(game) + "Changed rule\n"
    )
    with pytest.raises(ValueError, match="Review the English translation"):
        builder.build(tmp_path)


def test_shared_ranked_rules_and_special_reset_modes(tmp_path):
    builder.build(tmp_path)
    assert "108 drops" in (tmp_path / "sand-rescue.html").read_text()
    assert (
        "SPACE is disabled during play" in (tmp_path / "brick-pulse.html").read_text()
    )
    for gid in ("frost-steps", "gravity-well", "glyph-shift", "magnet-vault"):
        text = (tmp_path / f"{gid}.html").read_text()
        assert "ACDEFGHJKMNPQRTW" in text
        assert "Final challenges" in text
        assert "4–24 letters" in text
