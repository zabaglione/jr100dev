"""Build independent JR-100 games and verify their complete memory layout."""

import importlib.util
import json
import re
import sys
from pathlib import Path

from jr100dev.asm.encoder import Assembler
from jr100dev.link import pack_prg

ROOT = Path(__file__).resolve().parent
INVERSE = dict(
    zip(
        [
            "BEQ",
            "BNE",
            "BCC",
            "BCS",
            "BHI",
            "BLS",
            "BPL",
            "BMI",
            "BVC",
            "BVS",
            "BGE",
            "BLT",
            "BGT",
            "BLE",
        ],
        [
            "BNE",
            "BEQ",
            "BCS",
            "BCC",
            "BLS",
            "BHI",
            "BMI",
            "BPL",
            "BVS",
            "BVC",
            "BLT",
            "BGE",
            "BLE",
            "BGT",
        ],
    )
)


def long_branches(source):
    """Expand conditional jumps before assembly, using only 6800 instructions."""
    lines = []
    for line in source.splitlines():
        match = re.fullmatch(r"\s+(B\w+)\s+([A-Z][A-Z_0-9]*)\s*(?:;.*)?", line)
        if match and match[1] == "BRA":
            lines.append(f"    JMP {match[2]}")
        elif match and match[1] in INVERSE:
            label = f"LONG_BRANCH_{len(lines)}"
            lines.extend(
                (f"    {INVERSE[match[1]]} {label}", f"    JMP {match[2]}", f"{label}:")
            )
        else:
            lines.append(line)
    return "\n".join(lines) + "\n"


def build(directory):
    directory = directory.resolve()
    metadata = json.loads((directory / "game.json").read_text())
    output = directory / "build"
    output.mkdir(exist_ok=True)
    spec = importlib.util.spec_from_file_location(
        "game_assets", directory / "assets.py"
    )
    assets = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assets)
    assets.generate(output)
    modules = [
        ROOT / "common" / name for name in ("memory.inc", "platform.asm", "sound.asm")
    ]
    modules += [directory / "src" / name for name in metadata["modules"]]
    modules += [output / "assets.inc", output / "levels.inc"]
    source = "    .org $0300\n    JMP ENTRY\n"
    for path in modules:
        module_source = path.read_text()
        if path.name == "platform.asm" and metadata.get("clockModule"):
            before, remainder = module_source.split("CLOCK_RELOAD:\n", 1)
            _, after = remainder.split("POLL_INPUT:\n", 1)
            clock = (directory / "src" / metadata["clockModule"]).read_text()
            module_source = before + clock + "\nPOLL_INPUT:\n" + after
        source += f"\n; Module: {path.name}\n" + module_source + "\n"
    source += "CODE_END:\n"
    source = long_branches(source)
    (output / "game.asm").write_text(source)
    result = Assembler(source, filename="build/game.asm").assemble()
    symbols = result.symbols
    assert symbols["CODE_END"] <= 0x3000, "Code/data overlap display buffer"
    assert symbols["STATE_END"] <= 0x3900, "State overlaps saved display data"
    binary = result.machine_code
    prg = pack_prg(
        0x300,
        binary,
        0x300,
        program_name=metadata["title"],
        comment=f"{metadata['version']} / 16KB / MIT",
    )
    (output / f"{metadata['id']}.bin").write_bytes(binary)
    (output / f"{metadata['id']}.prg").write_bytes(prg)
    (output / "symbols.json").write_text(json.dumps(symbols, indent=2) + "\n")
    layout = {
        "code_bytes": len(binary),
        "code_end": symbols["CODE_END"],
        "code_capacity": 0x2D00,
        "state_end": symbols["STATE_END"],
        "framebuffer_bytes": 768,
        "pcg_slots": 32,
        "stack_reserved": 512,
        "standard_ram_bytes": 16384,
    }
    (output / "layout.json").write_text(json.dumps(layout, indent=2) + "\n")
    print(json.dumps({"game": metadata["id"], **layout}))


if __name__ == "__main__":
    build(Path(sys.argv[1]))
