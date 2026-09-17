"""Verify the public game layout and run its rule checks and input replay."""

import json
import subprocess
import sys
from pathlib import Path

game = Path(sys.argv[1]).resolve()
metadata = json.loads((game / "game.json").read_text())
symbols = json.loads((game / "build/symbols.json").read_text())
assert metadata["ramKiB"] == 16 and metadata["entry"] == 0x300
assert symbols["CODE_END"] <= symbols["FRAMEBUFFER"] == 0x3000
assert symbols["STATE_END"] <= symbols["SAVE_PCG"]
assert symbols["SAVE_PCG"] + 256 <= symbols["SAVE_SP"]
assert symbols["SAVE_SCREEN"] + 768 == 0x3E00
art = json.loads((game / "build/art.json").read_text())
assert len(art["game_pcg"]) == len(art["title_pcg"]) == 256
assert len(art["title_screen"]) == 768
assert all(0 <= code < 160 for code in art["title_screen"])
subprocess.run(
    [sys.executable, str(game.parent / "tests/check_fonts.py"), game.name], check=True
)
if "CONFIRM_RESET" in symbols:
    subprocess.run(
        [sys.executable, str(game.parent / "tests/check_reset.py"), game.name],
        check=True,
    )
for script in ("check_rules.py", "replay.py"):
    command = (
        [sys.executable, str(game.parent / "native" / script), game.name]
        if metadata.get("nativeRules")
        else [sys.executable, str(game / script)]
    )
    subprocess.run(command, check=True)
if metadata.get("rankedCampaign"):
    subprocess.run(
        [sys.executable, str(game.parent / "native/campaign_checks.py"), game.name],
        check=True,
    )
    subprocess.run(
        [sys.executable, str(game.parent / "native/password_checks.py"), game.name],
        check=True,
    )
print("PASS: standard 16KB layout and 32 PCG slots")
