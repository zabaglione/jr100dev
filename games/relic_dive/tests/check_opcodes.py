"""Compare each emitted instruction with the current independent emulator table."""

import importlib.util
import sys

from machine import EMU, ROOT

REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO / "src"))
from jr100dev.asm.encoder import Assembler


def check():
    spec = importlib.util.spec_from_file_location(
        "relic_opcode_sync", REPO / "tools/sync_opcodes.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    reference = {(e.mnemonic, e.opcode, e.size) for e in module.load_cpu_spec(EMU)}
    result = Assembler((ROOT / "build/game.asm").read_text()).assemble()
    count = 0
    for emitted in result.emissions:
        if emitted.line.is_directive or not emitted.data:
            continue
        key = (emitted.line.op, emitted.data[0], len(emitted.data))
        assert key in reference, (emitted.line.line_no, key)
        count += 1
    assert result.machine_code == (ROOT / "build/relic-dive.bin").read_bytes()
    return {"instructions": count, "status": "passed"}


if __name__ == "__main__":
    print(check())
