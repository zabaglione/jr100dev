"""Join native assembly and encode authored text and title graphics."""

import json
from pathlib import Path

from pack_text import pack
from title_art import build

ROOT = Path(__file__).resolve().parent
MODULES = (
    "constants.inc",
    "platform.asm",
    "main.asm",
    "map.asm",
    "terrain.asm",
    "dungeon.asm",
    "sight_rays.inc",
    "turns.asm",
    "items.asm",
    "extras.asm",
    "ui.asm",
    "assets.asm",
)
parts = ["    .org $0300\n    JMP ENTRY\n"]
for name in MODULES:
    parts.append(f"; Module: {name}\n" + (ROOT / "src" / name).read_text())
text, text_report = pack(json.loads((ROOT / "text.json").read_text()))
art, art_report = build()
parts.extend([text, art])
parts.append("CODE_END:\n")
(ROOT / "build" / "game.asm").write_text("\n".join(parts))
(ROOT / "build" / "text-layout.json").write_text(
    json.dumps(text_report, indent=2) + "\n"
)
(ROOT / "build" / "title-art.json").write_text(json.dumps(art_report, indent=2) + "\n")
