"""Player-guide completeness, links, and translation freshness checks."""

import hashlib
import importlib.util
import json
import re
import struct
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

import pytest

SPEC = importlib.util.spec_from_file_location(
    "guide_build", Path(__file__).parents[1] / "build.py"
)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


@pytest.fixture
def published_games(tmp_path):
    root = tmp_path / "published/games"
    entries = []
    library = json.loads((builder.ROOT / "games/library.json").read_text())
    for game in library["games"]:
        meta = json.loads(
            (builder.ROOT / "games" / game["directory"] / "game.json").read_text()
        )
        payload = struct.pack("<II", 0x300, 1) + b"\x39" + struct.pack("<I", 0)
        data = (
            b"PROG"
            + struct.pack("<I", 2)
            + b"PBIN"
            + struct.pack("<I", len(payload))
            + payload
        )
        path = f"games/{game['id']}/{meta['version']}/{game['id']}.prg"
        target = root.parent / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        entries.append(
            {k: meta[k] for k in ("id", "version", "entry", "ramKiB")}
            | {"path": path, "sha256": hashlib.sha256(data).hexdigest()}
        )
    (root / "catalog.json").write_text(
        json.dumps({"schemaVersion": 1, "games": entries})
    )
    (root / "LICENSE.txt").write_bytes((builder.ROOT / "games/LICENSE").read_bytes())
    (root / "boot.rom").write_bytes(b"private fixture must not enter the bundle")
    return root


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


def test_all_games_have_both_languages_media_and_valid_navigation(
    tmp_path, published_games
):
    builder.build(tmp_path, published_games)
    ids = json.loads((tmp_path / "manifest.json").read_text())["games"]
    assert len(ids) == 51
    assert len(list(tmp_path.glob("*.html"))) == 54
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


def test_japanese_rule_changes_require_translation_review(
    tmp_path, published_games, monkeypatch
):
    original = builder.japanese_manual
    monkeypatch.setattr(
        builder, "japanese_manual", lambda game: original(game) + "Changed rule\n"
    )
    with pytest.raises(ValueError, match="Review the English translation"):
        builder.build(tmp_path, published_games)


def test_shared_ranked_rules_and_special_reset_modes(tmp_path, published_games):
    builder.build(tmp_path, published_games)
    assert "108 drops" in (tmp_path / "sand-rescue.html").read_text()
    assert (
        "SPACE is disabled during play" in (tmp_path / "brick-pulse.html").read_text()
    )
    for gid in ("frost-steps", "gravity-well", "glyph-shift", "magnet-vault"):
        text = (tmp_path / f"{gid}.html").read_text()
        assert "ACDEFGHJKMNPQRTW" in text
        assert "Final challenges" in text
        assert "4–24 letters" in text


def test_mister_downloads_are_direct_complete_and_autostart_ready(
    tmp_path, published_games
):
    builder.build(tmp_path, published_games)
    catalog = json.loads((published_games / "catalog.json").read_text())["games"]
    index = (tmp_path / "index.html").read_text()
    assert "MiSTer FPGA" in index
    assert "downloads/jr100-games-mister.zip" in index
    expected = {"JR100/README-en.txt", "JR100/README-ja.txt", "JR100/LICENSE.txt"}
    with zipfile.ZipFile(tmp_path / "downloads/jr100-games-mister.zip") as archive:
        for game in catalog:
            gid = game["id"]
            download = f"downloads/{gid}.prg"
            data = (tmp_path / download).read_bytes()
            assert download in Page(index).links
            page = (tmp_path / f"{gid}.html").read_text()
            assert download in Page(page).links
            assert page.index(download) < page.index("demo-start.png")
            assert f'download="{gid}.prg"' in page
            assert "Autostart loaded program" in page and "A=USR($0300)" in page
            original = (published_games.parent / game["path"]).read_bytes()
            assert data.startswith(original)
            assert data.endswith(b"USR=$0300")
            assert archive.read(f"JR100/{gid}.prg") == data
            expected.add(f"JR100/{gid}.prg")
        assert set(archive.namelist()) == expected
        assert len(archive.namelist()) == len(expected)
        assert (
            archive.read("JR100/LICENSE.txt")
            == (builder.ROOT / "games/LICENSE").read_bytes()
        )
        assert b"JR-800 Web Emulator contributors" in archive.read(
            "JR100/README-en.txt"
        )
        assert b"have not been tested" in archive.read("JR100/README-en.txt")
    assert (
        "JR-800 Web Emulator contributors" in (tmp_path / "relic-dive.html").read_text()
    )


@pytest.mark.parametrize("change", ["hash", "traversal", "missing", "entry"])
def test_downloads_reject_invalid_or_stale_programs(tmp_path, published_games, change):
    manifest = published_games / "catalog.json"
    catalog = json.loads(manifest.read_text())
    if change == "hash":
        catalog["games"][0]["sha256"] = "0" * 64
    elif change == "traversal":
        catalog["games"][0]["path"] = "../boot.rom"
    elif change == "entry":
        catalog["games"][0]["entry"] = 0xC000
    else:
        catalog["games"].pop()
    manifest.write_text(json.dumps(catalog))
    with pytest.raises(ValueError):
        builder.build(tmp_path, published_games)


def test_autostart_retains_binary_sections_and_existing_credit():
    payload = struct.pack("<II", 0x300, 3) + b"\x01\x01\x39" + struct.pack("<I", 0)
    binary = b"PBIN" + struct.pack("<I", len(payload)) + payload
    comment = b"Existing credit USR=$1234"
    note = struct.pack("<I", len(comment)) + comment
    raw = (
        b"PROG\x02\x00\x00\x00" + binary + b"CMNT" + struct.pack("<I", len(note)) + note
    )
    converted = builder.autostart_program(raw, 0x300)
    assert converted.startswith(raw[:8] + binary)
    assert converted.endswith(b"USR=$0300 Existing credit")
    assert converted.count(b"USR=") == 1
    assert builder.autostart_program(converted, 0x300) == converted


@pytest.mark.parametrize(
    "data",
    [
        b"invalid",
        b"PROG\x01\x00\x00\x00",
        b"PROG\x02\x00\x00\x00PB",
        b"PROG\x02\x00\x00\x00CMNT\x04\x00\x00\x00\xff\x00\x00\x00",
    ],
)
def test_autostart_rejects_bad_containers(data):
    with pytest.raises(ValueError):
        builder.autostart_program(data, 0x300)
