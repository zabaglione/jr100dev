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
    if metadata.get("nativeRules"):
        sys.path.insert(0, str(ROOT / "common"))
        sys.path.insert(0, str(ROOT / "native"))
        import assets as native_assets
        from compiler import compile_file

        native_assets.generate(output, metadata, directory)
        compiled, state_slots = compile_file(directory / "rules.py")
        if metadata["id"] == "phase-pairs":
            compiled += f"\nPHASE_FIRST: .equ {state_slots['s.first']}\n"
        if metadata.get("rankedCampaign"):
            compiled += f"\nRANK_STARS: .equ {state_slots['s.stars']}\n"
        (output / "rules.inc").write_text(compiled)
        (output / "state_slots.json").write_text(
            json.dumps(state_slots, indent=2) + "\n"
        )
    else:
        load_assets(directory, output)
        sys.path.insert(0, str(ROOT / "native"))
        sys.path.insert(0, str(ROOT / "common"))
        from art_direction import apply_title

        apply_title(output, metadata)
    from fonts import apply as apply_fonts
    from fonts import instrument as instrument_fonts

    fonts_enabled = apply_fonts(output, metadata)
    from art import emit
    from feedback import jingle, pacing_assets

    with (output / "assets.inc").open("a") as asset_file:
        asset_file.write(emit("RESULT_JINGLE", jingle(metadata["id"])))
        asset_file.write(pacing_assets(metadata))
    modules = [
        ROOT / "common" / name
        for name in (
            "memory.inc",
            "platform.asm",
            "screens.asm",
            "sound.asm",
            "pacing.asm",
            "feedback.asm",
        )
    ]
    if metadata.get("nativeRules"):
        modules += [ROOT / "native/runtime.asm", output / "rules.inc"]
        if "JSR N_ANIMATE" in compiled or "JSR N_HOLD" in compiled:
            modules += [ROOT / "native/motion.asm"]
        if "JSR N_FACE" in compiled:
            modules += [ROOT / "native/facing.asm"]
        if "JSR N_IMPACT" in compiled:
            modules += [ROOT / "native/impact.asm"]
        if "JSR N_VANISH" in compiled:
            modules += [ROOT / "native/vanish.asm"]
        if "JSR N_MOVER" in compiled:
            modules += [ROOT / "native/mover.asm"]
    modules += [directory / "src" / name for name in metadata["modules"]]
    if metadata["id"] != "loop-ten":
        modules += [ROOT / "common/confirm.asm"]
    modules += [output / "assets.inc", output / "levels.inc"]
    source = "    .org $0300\n    JMP ENTRY\n"
    if metadata.get("nativeRules"):
        source += f"GAME_RATE: .equ {metadata.get('rate', 255)}\nGAME_LEVELS: .equ {metadata.get('levels', 10)}\n"
    for path in modules:
        module_source = path.read_text()
        if path.name == "runtime.asm" and metadata["id"] == "phase-pairs":
            from phase_pairs.presentation import hint_hook

            module_source = hint_hook(module_source)
        if path.name == "runtime.asm" and metadata.get("rankedCampaign"):
            # Use the ranked menu/loader, with the existing arithmetic and drawing ABI.
            helpers = module_source.split("N_INDEX:\n", 1)[1].split("N_WIN:\n", 1)[0]
            module_source = (ROOT / "native/campaign_runtime.asm").read_text()
            module_source += "\n" + (ROOT / "native/password.asm").read_text()
            module_source += "\nN_INDEX:\n" + helpers
        if path.name == "platform.asm" and fonts_enabled:
            module_source = instrument_fonts(module_source)
        if (
            path.name == "runtime.asm"
            and metadata.get("rankedCampaign")
            and fonts_enabled
        ):
            # Password entry uses one plain font for letters, numbers and hints.
            module_source = module_source.replace(
                "P_DRAW:\n", "P_DRAW:\n    LDX #FONT_TITLE_MAP\n    STX FONT_MAP\n", 1
            )
        if path.name == "platform.asm" and metadata.get("rankedCampaign"):
            from password import input_hook

            module_source = input_hook(module_source)
        if path.name == "platform.asm" and metadata.get("clockModule"):
            before, remainder = module_source.split("CLOCK_RELOAD:\n", 1)
            _, after = remainder.split("POLL_INPUT:\n", 1)
            clock = (directory / "src" / metadata["clockModule"]).read_text()
            module_source = before + clock + "\nPOLL_INPUT:\n" + after
        if path.name == "platform.asm" and metadata.get("directions") == 8:
            from input_eight import apply_eight_way

            module_source = apply_eight_way(module_source)
        if path.name == "runtime.asm" and metadata.get("disableSpaceReset"):
            module_source = module_source.replace("BEQ N_SPACE_RETRY", "BEQ N_DRAW")
        if path.name == "confirm.asm" and fonts_enabled:
            module_source = module_source.replace(
                "CONFIRM_RESET:\n",
                "CONFIRM_RESET:\n    LDX FONT_MAP\n    STX CN_FONT\n    LDX #FONT_TITLE_MAP\n    STX FONT_MAP\n",
            ).replace(
                "CONFIRM_DONE:\n", "CONFIRM_DONE:\n    LDX CN_FONT\n    STX FONT_MAP\n"
            )
        source += f"\n; Module: {path.name}\n" + module_source + "\n"
    if not metadata.get("nativeRules"):
        source = re.sub(
            r"TITLE_TEXT:\n(?:    \.word[^\n]*\n)+",
            "TITLE_TEXT:\n    .word 0\n",
            source,
            count=1,
        )
    source += "CODE_END:\n"
    if metadata.get("nativeRules") and "JSR N_FACE" in compiled:
        source = source.replace(
            "    JSR FN_INIT\n", "    JSR N_FACE_RESET\n    JSR FN_INIT\n"
        )
    if metadata.get("nativeRules"):
        source = source.replace(
            "    JSR FN_INIT\n", "    JSR FN_INIT\n    JSR QUEUE_START\n"
        )
    from screens import compress

    source = compress(source)
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


def load_assets(directory, output):
    spec = importlib.util.spec_from_file_location(
        "game_assets", directory / "assets.py"
    )
    assets = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assets)
    assets.generate(output)


if __name__ == "__main__":
    build(Path(sys.argv[1]))
