from pathlib import Path

import pytest

from jr100dev.asm import opcodes_mb8861h
from tools.sync_opcodes import load_cpu_spec


@pytest.mark.skipif(
    not Path("external/pyjr100emu").exists(),
    reason="pyjr100emu checkout (external/pyjr100emu) is required for sync verification",
)
def test_opcode_table_matches_emulator(tmp_path):
    entries = load_cpu_spec(Path("external/pyjr100emu"))
    generated = [
        {
            "mnemonic": entry.mnemonic,
            "addressing": entry.addressing,
            "opcode": entry.opcode,
            "size": entry.size,
        }
        for entry in entries
    ]
    current = [
        {
            "mnemonic": row["mnemonic"],
            "addressing": row["addressing"],
            "opcode": row["opcode"],
            "size": row["size"],
        }
        for row in opcodes_mb8861h.OPCODES
    ]
    assert generated == current
