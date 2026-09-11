"""Real input completes all five records and returns to base in standard RAM."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import Machine, lib
from model import SITES, State, advance, route

FIELDS = {
    "x": "PLAYER_X",
    "y": "PLAYER_Y",
    "oxygen": "OXYGEN",
    "hull": "HULL",
    "flags": "FLAGS",
    "sight": "SIGHT",
    "noise": "NOISE",
    "quiet": "QUIET",
    "turn": "TURN",
    "hx": "HUNTER_X",
    "hy": "HUNTER_Y",
    "grace": "GRACE",
    "mode": "MODE",
}


def act(m, a, pad):
    if a in (8, 9, 10, 7) and pad:
        index = {8: 0, 9: 1, 10: 2, 7: 3}[a]
        m.action(5, True)
        for _ in range(index):
            m.action(2, True)
        m.action(5, True)
    elif a in (9, 10):
        m.action(5)
        for _ in range({9: 1, 10: 2}[a]):
            m.action(2)
        m.action(5)
    else:
        m.action(a, pad)


def compare(m, s):
    for field, name in FIELDS.items():
        assert m.get(name) == getattr(s, field), (
            name,
            m.get(name),
            getattr(s, field),
            s,
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--keyboard", action="store_true")
    args = parser.parse_args()
    rom = args.rom.read_bytes() if args.rom else None
    m = Machine("abyss_signal", rom)
    root = Path(__file__).resolve().parent
    if args.capture:
        assert rom, "Publication frames require the actual ROM"
        (root / "images").mkdir(exist_ok=True)
        (root / "art").mkdir(exist_ok=True)
        m.capture(root / "images/title.png")
        m.export_workbench(root / "art/title.pcg.json")
    m.action(5, not args.keyboard)
    s = State()
    compare(m, s)
    actions = []
    for i, target in enumerate([*SITES, (2, 2)]):
        # Sounding at each leg makes the route exercise sonar and its hunter noise.
        if i < 5:
            act(m, 8, not args.keyboard)
            s = advance(s, 8)
            compare(m, s)
            actions.append(8)
        for a in route(s, target, 1 if i < 5 else 0):
            act(m, a, not args.keyboard)
            s = advance(s, a)
            compare(m, s)
            actions.append(a)
            assert s.mode == 1 or i == 5, s
        if i < 5:
            if args.capture and i == 2:
                act(m, 8, not args.keyboard)
                s = advance(s, 8)
                compare(m, s)
                actions.append(8)
                m.capture(root / "images/sonar.png")
                m.export_workbench(root / "art/sonar.pcg.json")
            act(m, 9, not args.keyboard)
            s = advance(s, 9)
            compare(m, s)
            actions.append(9)
            assert s.mode == 3, s
            if args.capture:
                m.capture(root / f"images/discovery-{i+1:02}.png")
            m.action(5, not args.keyboard)
            s.mode = 1
            compare(m, s)
    assert s.mode == 5 and s.flags == 31
    assert m.read(0x300, len(m.code)) == m.code
    assert lib.min_sp(m.p) >= 0x3E00
    if args.capture:
        m.capture(root / "images/survey-complete.png")
    print(
        f"PASS: 5 discoveries and return, {len(actions)} actions, O2 {s.oxygen}, hull {s.hull}, stack ${lib.min_sp(m.p):04X}"
    )


if __name__ == "__main__":
    main()
