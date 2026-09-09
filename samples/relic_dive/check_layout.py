"""Fail the build if the standard 16K memory or PCG budget is exceeded."""

import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent
symbols = {
    k: int(v, 16)
    for k, v in re.findall(
        r"^(\w+)\s*=\s*\$([0-9A-Fa-f]+)",
        (ROOT / "build/relic_dive.map").read_text(),
        re.MULTILINE,
    )
}
assert symbols["CODE_END"] <= symbols["FRAMEBUFFER"], "Code overlaps framebuffer"
assert symbols["FRAMEBUFFER"] + 768 <= symbols["STATE_BEGIN"]
assert symbols["STATE_END"] <= symbols["SAVE_ZP"]
assert symbols["FLOORS"] + symbols["FLOOR_DATA_END"] <= symbols["STATE_END"]
assert symbols["SEEN"] == symbols["FLOORS"] + symbols["TERRAIN_BYTES"]
assert symbols["VISIBLE"] == symbols["SEEN"] + symbols["MASK_BYTES"]
assert (
    symbols["FLOORS"] + symbols["ENEMY_START"]
    == symbols["VISIBLE"] + symbols["MASK_BYTES"]
)
assert symbols["ITEM_START"] == symbols["ENEMY_START"] + symbols["MAX_ENEMIES"] * 8
assert symbols["FLOOR_DATA_END"] == symbols["ITEM_START"] + symbols["MAX_ITEMS"] * 3
assert 0x80 <= symbols["FAST_BEGIN"] < symbols["FAST_END"] <= 0x100
assert symbols["SAVE_ZP"] + 128 <= symbols["SAVE_PCG"]
assert symbols["SAVE_PCG"] + 256 <= symbols["SCRATCH_BEGIN"]
assert symbols["SCRATCH_END"] <= symbols["SAVE_SP"]
assert symbols["SAVE_VIA"] + 4 <= 0x3E00
assert symbols["TILES_END"] - symbols["TILES"] <= 256
report = {
    "code_bytes": symbols["CODE_END"] - 0x300,
    "code_end": symbols["CODE_END"],
    "code_capacity": symbols["FRAMEBUFFER"] - 0x300,
    "framebuffer_bytes": 768,
    "map_bytes": symbols["TERRAIN_BYTES"] + symbols["MASK_BYTES"] * 2,
    "pcg_slots": (symbols["TILES_END"] - symbols["TILES"]) // 8,
    "stack_reserved": 512,
    "standard_ram_bytes": 16384,
}
(ROOT / "build/layout.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))

# Verify the distributed container against the BIN used by runtime tests.
prg = (ROOT / "build/relic_dive.prg").read_bytes()
assert prg[:8] == b"PROG\x02\x00\x00\x00"
position = 8
segments = []
while position < len(prg):
    tag = prg[position : position + 4]
    length = struct.unpack_from("<I", prg, position + 4)[0]
    payload = prg[position + 8 : position + 8 + length]
    assert len(payload) == length
    if tag == b"PBIN":
        address, size = struct.unpack_from("<II", payload)
        segments.append((address, payload[8 : 8 + size]))
        assert b"entry=$0300" in payload[8 + size :]
    position += 8 + length
assert position == len(prg)
assert segments == [(0x300, (ROOT / "build/relic_dive.bin").read_bytes())]
