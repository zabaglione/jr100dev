"""Copy only approved demo assets into the public emulator's media directory."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def package(destination):
    library = json.loads((ROOT / "library.json").read_text())
    catalog = {"schemaVersion": 1, "games": []}
    for game in library["games"]:
        directory = ROOT / game["directory"] / "images"
        report = json.loads((directory / "play.json").read_text())
        assert report["host_state_writes"] == 0 and report["playback_speed"] == 1
        assert report["video_seconds"] >= 25
        if game["id"] == "peg-garden":
            assert not report["edited"]
        else:
            assert report["video_seconds"] <= 35
        entry = {key: game[key] for key in ("id", "title", "genre")}
        entry.update({key: report[key] for key in ("edited", "outcome", "prg_sha256")})
        entry["seconds"] = report["video_seconds"]
        assets = []
        for name in ["play.mp4", *report["images"]]:
            source = directory / name
            target = destination / game["id"] / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            assets.append(
                {
                    "path": f"game-media/{game['id']}/{name}",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
            )
        entry["video"], entry["images"] = assets[0], assets[1:]
        catalog["games"].append(entry)
    (destination / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    shutil.copyfile(ROOT / "LICENSE", destination / "LICENSE.txt")
    shutil.copyfile(
        Path(__file__).with_name("gameplay.html"), destination.parent / "gameplay.html"
    )
    print(
        f"Packaged {len(catalog['games'])} videos and {len(catalog['games']) * 3} screenshots"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", type=Path)
    package(parser.parse_args().destination)
