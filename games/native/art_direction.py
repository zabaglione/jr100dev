"""Use the library's new title art while preserving game-only PCG animation slots."""

import json
import re

from art import emit
from artwork import title
from title_styles import RESERVED


def apply_title(output, metadata):
    info = next(
        g
        for g in json.loads((output.parents[1] / "library.json").read_text())["games"]
        if g["id"] == metadata["id"]
    )
    art = json.loads((output / "art.json").read_text())
    bank, screen = title(info)
    text = (output / "assets.inc").read_text()
    if metadata["id"] == "chrono-breach":
        frames = art["title_pcg"][128:]
        bank[224:] = frames[:32]
        text += emit("TITLE_CLOCK_FRAMES", frames)
    else:
        for slot in RESERVED.get(metadata["id"], ()):
            bank[slot * 8 : slot * 8 + 8] = art["title_pcg"][slot * 8 : slot * 8 + 8]
    for label, data in [("TITLE_PCG", bank), ("TITLE_SCREEN", screen)]:
        text, count = re.subn(
            label + r":\n(?:    \.byte[^\n]*\n)+", emit(label, data), text, count=1
        )
        assert count == 1, label
    (output / "assets.inc").write_text(text)
    art["title_pcg"] = bank
    art["title_screen"] = screen
    (output / "art.json").write_text(json.dumps(art, indent=2) + "\n")
