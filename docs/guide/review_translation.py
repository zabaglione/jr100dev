"""Record Japanese source hashes only after the named translations are reviewed."""

import argparse
import hashlib
import json

from build import HERE, ROOT, japanese_controls, japanese_manual


def main():
    games = {
        game["id"]: game
        for game in json.loads((ROOT / "games/library.json").read_text())["games"]
    }
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids", nargs="+", choices=[*games, "controls"])
    args = parser.parse_args()
    path = HERE / "translation-sources.json"
    hashes = json.loads(path.read_text())
    for gid in args.ids:
        text = japanese_controls() if gid == "controls" else japanese_manual(games[gid])
        hashes[gid] = hashlib.sha256(text.encode()).hexdigest()
    path.write_text(json.dumps(hashes, indent=2) + "\n")
    print(f"Recorded {len(args.ids)} reviewed translations")


if __name__ == "__main__":
    main()
