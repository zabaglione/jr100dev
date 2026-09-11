"""Replay only input events from BASIC autostart through all twenty sectors."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tests"))
from machine import Machine, lib
from solve import Room


def snapshot(machine):
    raw = machine.read("ENEMIES", 24)
    alive = sum((1 << i) for i in range(6) if raw[i * 4 + 3])
    raw = machine.read("BULLETS", 48)
    slots = [tuple(raw[i : i + 3]) if raw[i + 2] else None for i in range(0, 48, 3)]
    while slots and slots[-1] is None:
        slots.pop()
    return (
        machine.get("PLAYER_X"),
        machine.get("PLAYER_Y"),
        machine.get("AMMO"),
        alive,
        machine.get("PHASE"),
        tuple(slots),
    )


def play_action(machine, action, pad):
    if action >= 9:
        machine.action(5, pad=pad)
        while machine.get("FACING") != action - 8:
            machine.action(4, pad=pad)
        machine.action(5, pad=pad)
    elif action == 7 and pad:
        machine.action(5, pad=True)
        machine.action(2, pad=True)
        machine.action(5, pad=True)
    else:
        machine.action(action, pad=pad)


def replay(rom=None, captures=None, pad=True):
    rooms = json.loads((ROOT / "levels.json").read_text())
    solutions = json.loads((ROOT / "solutions.json").read_text())
    m = Machine(rom=rom)
    if captures:
        captures.mkdir(parents=True, exist_ok=True)
        (ROOT / "art").mkdir(exist_ok=True)
        m.capture(captures / "title.png")
        m.export_workbench(ROOT / "art/title.pcg.json")
    m.action(5, pad=pad)
    total = 0
    for i, (data, solution) in enumerate(zip(rooms, solutions)):
        assert m.get("MODE") == 1 and m.get("LEVEL") == i
        room = Room(data)
        state = room.initial
        assert snapshot(m) == state, (i, snapshot(m), state)
        for n, action in enumerate(solution["actions"]):
            state = room.step(state, action)
            play_action(m, action, pad)
            assert snapshot(m) == state, (i, n, action, snapshot(m), state)
            if captures and (i, n) in ((1, 4), (4, 4), (14, 2)):
                m.capture(captures / f"sector-{i + 1:02}.png")
                if i == 1:
                    m.export_workbench(ROOT / "art/play.pcg.json")
            total += 1
        assert m.get("MODE") == 4, (i, m.get("MODE"))
        print(f"Sector {i + 1:02}: {len(solution['actions'])} actions PASS", flush=True)
        if captures and i == 19:
            m.capture(captures / "last-sector.png")
        m.action(5, pad=pad)
    assert m.get("MODE") == 5
    assert m.read(0x300, len(m.code)) == m.code, "Game code changed during replay"
    assert lib.min_sp(m.p) >= 0x3E00, f"stack overrun: {lib.min_sp(m.p):04x}"
    if captures:
        m.capture(captures / "ending.png")
    print(
        f"PASS: {total} world actions; min SP ${lib.min_sp(m.p):04X}; input source {'pad' if pad else 'keyboard'}"
    )
    return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--captures", type=Path)
    parser.add_argument("--keyboard", action="store_true")
    args = parser.parse_args()
    replay(
        args.rom.read_bytes() if args.rom else None, args.captures, not args.keyboard
    )
