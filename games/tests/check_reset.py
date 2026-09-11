"""Exercise reset questions through real keyboard and joystick input."""

import json
from pathlib import Path

from machine import Machine, lib

ROOT = Path(__file__).resolve().parents[1]


def check(name):
    m = Machine(name)
    m.action(5)
    m.action(4)
    if m.metadata.get("nativeRules"):
        if m.metadata.get("disableSpaceReset"):
            m.action(6)
            assert not m.get("CN_ACTIVE") and m.get("MODE") == 1
            # Defeat is an explicit fixture; retry is still a real input path.
            lib.poke(m.p, m.sym["MODE"], 3)
            m.action(5)
        else:
            m.action(6)
    elif name in ("chrono_breach", "abyss_signal", "trace_blade"):
        m.action(5)
        for _ in range(4 if name == "abyss_signal" else 2):
            m.action(2)
        m.action(5)
    else:
        # Exercise post-defeat retry without relying on accidental combat loss.
        lib.poke(m.p, m.sym["MODE"], 3)
        m.action(5)
    assert m.get("CN_ACTIVE") == 1 and m.get("CN_CHOICE") == 0
    before = m.read(0x3340, 0x4C0)
    lib.ticks(m.p, 2_000_000)
    assert m.read(0x3340, 0x4C0) == before, (name, "Game advances behind question")
    assert m.get("CN_ACTIVE") == 1, "Prompt closed without further input"
    # Default RETURN is cancel, with no directional selection.
    m.action(5)
    assert not m.get("CN_ACTIVE")
    if m.metadata.get("nativeRules"):
        assert m.read(0x3400, 0x400) == before[0xC0:], (name, "Cancel loses state")
    # Open it again, cancel with SPACE even after selecting YES.
    if m.metadata.get("nativeRules"):
        m.action(5 if m.metadata.get("disableSpaceReset") else 6)
    else:
        m.action(5)
    assert m.get("CN_ACTIVE")
    m.action(4, pad=True)
    m.action(6)
    assert not m.get("CN_ACTIVE")
    if m.metadata.get("nativeRules"):
        m.action(5 if m.metadata.get("disableSpaceReset") else 6)
    else:
        m.action(5)
    m.answer_reset(True, pad=True)
    if name == "dice_relic":
        lib.ticks(m.p, 1_000_000)
    assert m.get("MODE") == 1
    assert m.read(0x300, len(m.code)) == m.code
    assert lib.min_sp(m.p) >= 0x3E00
    print(
        f"PASS: {name}, paused question, default cancel, SPACE cancel, pad YES, immutable code"
    )


if __name__ == "__main__":
    import sys

    selected = sys.argv[1:]
    for info in json.loads((ROOT / "library.json").read_text())["games"]:
        name = info["directory"]
        if name not in ("loop_ten", "relic_dive") and (
            not selected or name in selected
        ):
            check(name)
