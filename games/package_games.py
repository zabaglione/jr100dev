"""Copy only authored, built game PRGs and their license to a web catalog."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def package(destination, source_ref="main"):
    destination.mkdir(parents=True, exist_ok=True)
    games = []
    for directory in json.loads((ROOT / "collection.json").read_text())["games"]:
        metadata = ROOT / directory / "game.json"
        game = json.loads(metadata.read_text())
        source = metadata.parent / "build" / f'{game["id"]}.prg'
        layout = json.loads((source.parent / "layout.json").read_text())
        assert game["ramKiB"] == 16 and layout["code_end"] <= 0x3000
        data = source.read_bytes()
        assert data[:4] == b"PROG"
        relative = f'{game["id"]}/{game["version"]}/{game["id"]}.prg'
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        games.append(
            {k: game[k] for k in ("id", "title", "version", "ramKiB", "entry")}
            | {
                "path": "games/" + relative,
                "sha256": hashlib.sha256(data).hexdigest(),
                "sourceUrl": f"https://github.com/zabaglione/jr100dev/tree/{source_ref}/games/{metadata.parent.name}",
            }
        )
    (destination / "catalog.json").write_text(
        json.dumps({"schemaVersion": 1, "games": games}, indent=2) + "\n"
    )
    shutil.copyfile(ROOT / "LICENSE", destination / "LICENSE.txt")
    print(f"Packaged {len(games)} public games")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    parser.add_argument("--source-ref", default="main")
    args = parser.parse_args()
    package(args.destination, args.source_ref)
