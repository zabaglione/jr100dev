"""Prepare only the collection's Wiki pages and authored screenshots; never push."""

import json
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
destination = Path(sys.argv[1]).resolve()
destination.mkdir(parents=True, exist_ok=True)
directories = json.loads((root / "games/collection.json").read_text())["games"]
library = json.loads((root / "games/library.json").read_text())
pages = ["Home", "_Sidebar", "All-Games", "Controls", "Presentation"]
pages += ["Genre-" + genre["id"].title() for genre in library["genres"]]
for directory in directories:
    game = root / "games" / directory
    metadata = json.loads((game / "game.json").read_text())
    pages.append(metadata["id"].upper())
    for source in (game / "images").iterdir():
        if source.suffix not in {".png", ".gif"}:
            continue
        target = destination / "images" / metadata["id"] / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
for name in ("presentation.gif", "disc-turn.png"):
    target = destination / "images" / "presentation" / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / "games" / "images" / name, target)
for page in pages:
    source = root / "docs/wiki" / f"{page}.md"
    shutil.copyfile(source, destination / source.name)
print("Prepared collection Wiki pages and game screenshots")
