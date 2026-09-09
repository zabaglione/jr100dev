"""Join native assembly modules with source markers for reproducible diagnostics."""

from pathlib import Path

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
parts.append("CODE_END:\n")
(ROOT / "build" / "game.asm").write_text("\n".join(parts))
