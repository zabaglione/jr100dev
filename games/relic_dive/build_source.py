"""Join native assembly and encode authored text and title graphics."""

import json
import re
from pathlib import Path

from pack_text import pack
from title_art import build

from jr100dev.asm.encoder import Assembler

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
source = "\n".join(parts)
# BRA and JMP have identical flag/register effects. Relax only proven in-range
# internal jumps; this reclaims bytes without changing maps, text or RAM layout.
jumps = []


def mark_jump(match):
    label = f"RELAX_JUMP_{len(jumps)}"
    jumps.append((label, match[1]))
    return f"{label}:\n    JMP {match[1]}"


source = re.sub(r"^    JMP ([A-Z][A-Z_0-9]*)$", mark_jump, source, flags=re.MULTILINE)
while True:
    symbols = Assembler(source).assemble().symbols
    changed = False
    for label, target in jumps:
        old = f"{label}:\n    JMP {target}"
        if old in source and -128 <= symbols[target] - symbols[label] - 2 <= 127:
            source = source.replace(old, f"{label}:\n    BRA {target}")
            changed = True
    if not changed:
        break
(ROOT / "build" / "game.asm").write_text(source)
(ROOT / "build" / "text-layout.json").write_text(
    json.dumps(text_report, indent=2) + "\n"
)
(ROOT / "build" / "title-art.json").write_text(json.dumps(art_report, indent=2) + "\n")
