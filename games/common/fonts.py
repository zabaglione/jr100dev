"""Original 8x8 type, allocated only to explicitly unused scene PCG slots."""

import json
import re
from pathlib import Path

from art import FONT_ROWS, emit
from relief import NATIVE

ROOT = Path(__file__).resolve().parents[1]
STYLES = {
    "panel": ("計器盤", "角張った太線"),
    "slant": ("スピード", "右へ傾く太線"),
    "engraved": ("石碑", "上下の飾りを持つ刻印"),
    "crystal": ("結晶", "細い角形と斜めの切り口"),
    "round": ("栽培", "丸みのある太線"),
    "book": ("活字", "読みやすいセリフ体"),
}
GROUPS = {
    "panel": "chrono-breach iron-script circuit-works magnet-vault gravity-well lunar-touchdown metro-weave cargo-balance number-vault fuse-box",
    "slant": "night-swarm orbit-dodge gate-runner brick-pulse star-lance ribbon-snake echo-parry pendulum-port trace-blade",
    "engraved": "sigil-deck dice-relic hearth-zero glyph-shift five-forge stone-balance ruin-lexicon mirror-relic sand-rescue loop-ten",
    "crystal": "abyss-signal lumen-cross frost-steps prism-trace tide-bridge orbit-draft phase-pairs tidal-nets",
    "round": "seed-merge orchard-days potion-path peg-garden",
    "book": "chain-suit quiet-route corner-crown memory-mosaic twenty-one shadow-archive compass-rose auction-house word-foundry",
}
STYLE_FOR = {game: style for style, games in GROUPS.items() for game in games.split()}
# Audited draw routines: retain every tile, border, portrait and animation glyph.
# Native sprites each own four consecutive glyphs; ranked stars own 28 and 29.
CUSTOM_FREE = {
    "chrono-breach": ([], [30, 31]),
    "sigil-deck": ([26, 27, 30, 31], [26, 27, 28, 30, 31]),
    "abyss-signal": (list(range(16, 32)), list(range(24, 28))),
    "trace-blade": (list(range(16, 32)), [29, 30, 31]),
    "dice-relic": (list(range(16, 32)), list(range(18, 32))),
    "loop-ten": (list(range(16, 32)), [28, 29, 31]),
}
SYMBOLS = {
    "+": "0004041F040400",
    "-": "0000001F000000",
    "/": "01010204081010",
    ":": "000C0C000C0C00",
    ">": "10080402040810",
    "<": "01020408040201",
    "=": "00001F001F0000",
    "?": "0E110102040004",
    ".": "00000000000C0C",
    "!": "04040404040004",
    "#": "0A0A1F0A1F0A0A",
    "%": "19190204081313",
}
# Wider square digits for control panels. Zero is slashed; 1 has a foot.
PANEL_DIGITS = {
    "0": [30, 51, 55, 59, 51, 51, 30],
    "1": [12, 28, 12, 12, 12, 12, 30],
    "2": [30, 51, 3, 14, 24, 48, 63],
    "3": [62, 3, 3, 30, 3, 3, 62],
    "4": [6, 14, 22, 38, 63, 6, 6],
    "5": [63, 48, 48, 62, 3, 3, 62],
    "6": [30, 48, 48, 62, 51, 51, 30],
    "7": [63, 3, 6, 12, 24, 24, 24],
    "8": [30, 51, 51, 30, 51, 51, 30],
    "9": [30, 51, 51, 31, 3, 3, 30],
}


def glyph(char, style):
    """Author-owned letters, never copied from the installed BASIC ROM."""
    encoded = (FONT_ROWS | SYMBOLS)[char]
    rows = [int(encoded[i : i + 2], 16) for i in range(0, 14, 2)]
    if style == "panel":
        rows = PANEL_DIGITS.get(char, [(r << 1) | r for r in rows])
        return [r << 1 for r in rows] + [0]
    if style == "slant":
        return [((r << 1) | r) << (2 if y < 3 else 1) for y, r in enumerate(rows)] + [0]
    if style in ("engraved", "book"):
        values = [r << 2 for r in rows]
        for y in (0, 6):
            values[y] |= (values[y] << 1 | values[y] >> 1) & 0xFE
        if style == "engraved":
            # Chisel-cut left strokes, with a small spur at the middle bar.
            values = [v | ((v >> 1) & 0x20) for v in values]
        return values + [0]
    if style == "crystal":
        return [r << (2 if y < 3 else 1) for y, r in enumerate(rows)] + [0]
    if style == "round":
        values = [(r << 2) | (r << 1) for r in rows]
        # Rounded terminals, without narrowing the counters in 6, 8 and 9.
        values[0] = rows[0] << 2
        values[6] = rows[6] << 2
        return values + [0]
    raise ValueError(style)


def free_slots(metadata):
    gid = metadata["id"]
    if not metadata.get("nativeRules"):
        return [], CUSTOM_FREE[gid][1]
    if gid == "phase-pairs":
        return [], []  # Tall numerals, card frames and four live fusion glyphs.
    if gid == "sand-rescue":
        return [], []  # Water channels, gates, crops and their growth poses.
    if gid == "gate-runner":
        return [], []  # Direct screen-code blitting keeps the road responsive.
    if gid == "prism-trace":
        return [], list(range(21, 32))  # Shared optical glyphs occupy 0..20.
    if gid == "orbit-draft":
        return [], list(range(22, 32))  # Five cards and two border glyphs.
    if gid == "chain-suit":
        return [], list(range(22, 32))  # Four suits and six card-border glyphs.
    if gid == "five-forge":
        return [], list(range(20, 32))  # Grid, two stones, landing and cursor.
    if gid == "brick-pulse":
        return [], list(range(16, 32))
    tiles = set(NATIVE[gid])
    if gid == "seed-merge":
        tiles.clear()  # The relief version uses ROM linework instead of tile 7.
    occupied = {t * 4 + q for t in tiles for q in range(4)}
    if gid == "fuse-box":
        occupied.update(range(10, 16))  # Inverted row/column hints, digits 0..5.
    if gid == "metro-weave":
        occupied.add(30)  # The diagonal rail's landing curve.
    if metadata.get("rankedCampaign"):
        occupied.update(range(24, 30))
    return [], sorted(set(range(32)) - occupied)


def choose(metadata, slots, scene):
    """A scene gets a complete alphabet or numeral set, never partial words."""
    if scene != "game":
        return ""
    if metadata["id"] == "word-foundry" and len(slots) >= 26:
        return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "0123456789" if len(slots) >= 10 else ""


def instrument(source):
    """Install text mapping only for games with an actual complete font set."""
    source = source.replace(
        "LOAD_PCG:\n    STX SRC\n",
        """LOAD_PCG:
    STX SRC
    CPX #GAME_PCG
    BEQ FONT_GAME_BANK
    LDX #FONT_TITLE_MAP
    BRA FONT_BANK_READY
FONT_GAME_BANK:
    LDX #FONT_GAME_MAP
FONT_BANK_READY:
    STX FONT_MAP
""",
    )
    return source.replace(
        "    STX SRC\n    JSR INTRO_FILTER\n    LDX DST\n    CMPA 0,X\n",
        """    STX SRC
    JSR INTRO_FILTER
    ; Convert text at presentation only; preserve semantic text and all artwork.
    CMPA #64
    BCC FONT_RAW
    STAA FONT_OFFSET + 1
    LDX FONT_MAP
    ADX FONT_OFFSET
    LDAA 0,X
FONT_RAW:
    LDX DST
    CMPA 0,X
""",
    )


def apply(output, metadata):
    """Replace unused bank bytes, then emit one 64-byte text map per bank."""
    gid = metadata["id"]
    art = json.loads((output / "art.json").read_text())
    source = (output / "assets.inc").read_text()
    records = {"style": STYLE_FOR[gid]}
    enabled = any(
        choose(metadata, free, scene)
        for scene, free in zip(("title", "game"), free_slots(metadata))
    )
    for scene, free in zip(("title", "game"), free_slots(metadata)):
        chars = choose(metadata, free, scene)
        mapping = list(range(64))
        bank = art[scene + "_pcg"]
        assigned = {}
        for char, slot in zip(chars, free):
            assert char not in assigned
            assigned[char] = slot
            bank[slot * 8 : slot * 8 + 8] = glyph(char, STYLE_FOR[gid])
            mapping[ord(char) - 32] = 128 + slot
        source, count = re.subn(
            scene.upper() + r"_PCG:\n(?:    \.byte[^\n]*\n)+",
            emit(scene.upper() + "_PCG", bank),
            source,
            count=1,
        )
        assert count == 1
        if enabled:
            source += emit("FONT_" + scene.upper() + "_MAP", mapping)
        records[scene] = {"free_slots": free, "characters": assigned}
    (output / "assets.inc").write_text(source)
    (output / "art.json").write_text(json.dumps(art, indent=2) + "\n")
    (output / "fonts.json").write_text(json.dumps(records, indent=2) + "\n")

    return enabled
