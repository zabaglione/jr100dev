"""Capture the complete title gallery using a locally supplied BASIC ROM."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tests"))
from machine import Machine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path, required=True)
    args = parser.parse_args()
    rom = args.rom.read_bytes()
    for game in json.loads((ROOT / "library.json").read_text())["games"]:
        directory = ROOT / game["directory"]
        if game["id"] == "relic-dive":
            subprocess.run(
                [
                    sys.executable,
                    str(directory / "capture.py"),
                    "--rom",
                    str(args.rom.resolve()),
                    "--title-only",
                ],
                check=True,
            )
            continue
        machine = Machine(game["directory"], rom)
        machine.capture(directory / "images/title.png")
        machine.export_workbench(directory / "art/title.pcg.json")
    print("Captured all 51 title screens from BASIC autostart")


if __name__ == "__main__":
    main()
