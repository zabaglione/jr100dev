"""CPU proof for staged starts, four-slot poses, impact holds and loss phrases."""

import argparse
import json
import sys
from pathlib import Path

from machine import KEYS, ROOT, Machine, lib

sys.path.insert(0, str(ROOT / "common"))
from art import quad_bank
from directional import frames
from title_styles import ROM_QUADS


def intro(rom=None, capture=None):
    m = Machine("magnet_vault", rom)
    lib.key(m.p, *KEYS[5], 1)
    m.until("DISPATCH")
    m.until("INTRO_REVEAL")
    began = lib.clocks(m.p)
    expected = m.read("FRAMEBUFFER", 768)
    groups = m.read("INTRO_GROUPS", 32)
    snapshots = []
    for phase in range(1, 5):
        m.until("PACE_WAIT_LOOP")
        assert m.get("INTRO_PHASE") == phase
        actual = m.read(0xC100, 768)
        assert actual == bytes(
            64 if 128 <= v < 160 and groups[v - 128] > phase else v for v in expected
        ), (phase, "Wrong actor reveal")
        snapshots.append(actual)
        if capture:
            m.capture(capture / f"start-{phase}.png")
        if phase < 4:
            m.until("INTRO_REVEAL")
    assert len(set(snapshots)) >= 3
    m.until("INTRO_MESSAGE_VISIBLE")
    banner = bytes(64 if c == " " else ord(c) - 32 for c in "   GAME START   ")
    assert m.read(0xC100 + 11 * 32 + 8, 16) == banner
    if capture:
        m.capture(capture / "start-message.png")
    m.until("FRAME_READY")
    elapsed = (lib.clocks(m.p) - began) / 894886.25
    assert 1.4 < elapsed < 2.1, elapsed
    assert m.read(0xC100, 768) == expected
    assert m.get("MODE") == 1 and not m.get("KEY_PENDING")
    assert not m.get("PACE_ACTIVE") and not m.get("CN_ACTIVE")
    lib.ticks(m.p, 180_000)
    assert m.read(0xC100, 768) == expected, "Held start button became an action"
    lib.key(m.p, *KEYS[5], 0)
    m.until("INPUT_DONE")
    for action in (1, 2, 3, 4):
        before = m.read(0xC000, 256)
        m.action(action)
        after = m.read(0xC000, 256)
        assert after[64:96] == bytes(frames("robot")[action - 1])
        assert after[:64] == before[:64] and after[96:] == before[96:]
        if capture:
            m.capture(capture / f"facing-{action}.png")
    assert m.read(0x300, len(m.code)) == m.code
    print(
        f"PASS: staged start {elapsed:.2f}s, held-input isolation, four-slot N/S/W/E poses"
    )


def impact_and_loss(rom=None, capture=None):
    m = Machine("echo_parry", rom)
    m.action(5)
    slots = json.loads((m.directory / "build/state_slots.json").read_text())
    bank = m.read(0xC000, 256)
    lib.key(m.p, *KEYS[5], 1)
    m.until("DISPATCH")
    m.until("SCENE_IMPACT_FLASH")
    began = lib.clocks(m.p)
    assert m.get(slots["s.hp"]) == 3
    contact = m.read(0xC100, 768)
    m.until("PACE_WAIT_LOOP")
    changed = {
        i for i, (a, b) in enumerate(zip(m.read(0xC100, 768), contact)) if a != b
    }
    assert changed and changed <= {14 * 32 + 5, 14 * 32 + 6, 15 * 32 + 5, 15 * 32 + 6}
    if capture:
        m.capture(capture / "impact.png")
    m.until("FRAME_READY")
    seconds = (lib.clocks(m.p) - began) / 894886.25
    assert 0.2 < seconds < 0.6, seconds
    assert m.get(slots["s.hp"]) == 3 and m.get("MODE") == 1
    assert m.read(0xC000, 256) == bank, "Flash changed every actor sharing PCG"
    lib.key(m.p, *KEYS[5], 0)
    m.until("INPUT_DONE")
    for hit in range(3):
        while m.get(slots["s.guarded"]) or m.get(slots["s.phase"]) != 0:
            m.until("FN_TICK")
            m.until("FRAME_READY")
        if hit < 2:
            m.action(5)
    lib.key(m.p, *KEYS[5], 1)
    m.until("DISPATCH")
    m.until("RESULT_LISTEN")
    assert m.get("MODE") == 3
    screen = m.read(0xC100, 768)
    why = bytes(ord(c) - 32 if c != " " else 64 for c in "WRONG GUARD OR EARLY PARRY")
    assert why in screen
    if capture:
        m.capture(capture / "failure.png")
    began = lib.clocks(m.p)
    m.until("FRAME_READY")
    seconds = (lib.clocks(m.p) - began) / 894886.25
    assert 1.3 < seconds < 1.7, seconds
    lib.ticks(m.p, 150_000)
    assert m.get("MODE") == 3 and m.read(0xC100, 768) == screen
    assert not m.get("KEY_PENDING") and not m.get("CN_ACTIVE")
    assert lib.audio_peak(m.p) > 0 and lib.min_sp(m.p) >= 0x3E00
    print(
        f"PASS: local impact flash, unchanged PCG, explicit cause, {seconds:.2f}s loss jingle, no held-key skip"
    )


def rom_geometry(rom):
    m = Machine("quiet_route", rom)
    expected = quad_bank()
    for mask, code in enumerate(ROM_QUADS):
        assert m.read(0xE000 + code * 8, 8) == bytes(expected[mask * 8 : mask * 8 + 8])
    print("PASS: all 16 semigraphic shapes matched the owned character ROM")


def independent_actors(rom=None):
    m = Machine("quiet_route", rom)
    m.action(5)
    m.action(4)
    m.action(3)
    bank = m.read(0xC000, 256)
    assert bank[64:96] == bytes(frames("explorer")[2])
    assert bank[160:192] == bytes(frames("guard")[3])
    m.action(1)  # Face a wall without moving the patrol.
    after = m.read(0xC000, 256)
    assert after[64:96] == bytes(frames("explorer")[0])
    assert after[:64] == bank[:64] and after[96:] == bank[96:]
    print("PASS: player and guard retain independent four-character poses")


def timed_start(rom=None):
    m = Machine("loop_ten", rom)
    lib.key(m.p, *KEYS[5], 1)
    m.until("INTRO_REVEAL")
    assert int.from_bytes(m.read("TIME_LEFT", 2), "big") == 600
    m.until("INTRO_MESSAGE_VISIBLE")
    assert int.from_bytes(m.read("TIME_LEFT", 2), "big") == 600
    m.until("LOOP_STARTED")
    assert int.from_bytes(m.read("TIME_LEFT", 2), "big") == 600
    assert not m.get("TIMED_OUT")
    print("PASS: LOOP TEN keeps all 600 game ticks through the start scene")


def defeat_animation(rom=None, capture=None):
    m = Machine("star_lance", rom)
    m.action(5)
    bank = m.read(0xC000, 256)
    lib.key(m.p, *KEYS[5], 1)
    m.until("N_VANISH")
    frames = []
    for phase in range(4):
        m.until("VANISH_VISIBLE")
        frames.append(m.read(0xC100, 768))
        assert m.read(0xC000, 256) == bank
        if capture:
            m.capture(capture / f"vanish-{phase}.png")
    assert len(set(frames)) == 4
    changed = {i for i, (a, b) in enumerate(zip(frames[0], frames[-1])) if a != b}
    assert changed == {9 * 32 + 13, 9 * 32 + 14, 10 * 32 + 13, 10 * 32 + 14}
    m.until("FRAME_READY")
    assert sum(bool(hp) for hp in m.read("B_ARRAY", 24)) == 17
    assert m.get("MODE") == 1 and not m.get("KEY_PENDING")
    assert lib.audio_peak(m.p) > 0
    print("PASS: four local destruction frames, SE, unchanged shared enemy PCG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        assert args.rom, "Screenshots require an owned BASIC ROM"
        args.capture.mkdir(parents=True, exist_ok=True)
    rom = args.rom.read_bytes() if args.rom else None
    if rom:
        rom_geometry(rom)
    intro(rom, args.capture)
    independent_actors(rom)
    timed_start(rom)
    impact_and_loss(rom, args.capture)
    defeat_animation(rom, args.capture)
