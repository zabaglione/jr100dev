"""Factory mechanics, editor recovery and visible native animation phases."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "native"), str(ROOT)]
from checks import Model, assert_state, lib
from iron_script.campaign import ROOMS, encode, initial, solve, transition
from replay import Player, solve_stage


def edit(player, program):
    for index, command in enumerate(program):
        while player.s.cursor > index:
            player.press(3)
        while player.s.cursor < index:
            player.press(4)
        while player.r.c[index] != command:
            player.press(1 if (command - player.r.c[index]) % 8 <= 4 else 2)


def independent_campaign():
    levels = json.loads((ROOT / "iron_script/levels.json").read_text())
    programs = json.loads((ROOT / "iron_script/solutions.json").read_text())
    assert levels == [encode(room) for room in ROOMS]
    assert len(levels) == len(programs) == 24
    loops = 0
    for number, (level, program) in enumerate(zip(levels, programs, strict=True)):
        r = Model("iron_script")
        r.init(number)
        r.c[: len(program)] = bytes(program)
        r.action(5)
        oracle = initial(level)
        for _ in range(24):
            pc = r.s.pc
            index = pc - 2 + r.s.sub if r.c[pc] == 7 else pc
            loops += r.c[pc] == 7
            oracle = transition(level, oracle, r.c[index])
            assert oracle is not None, (number + 1, pc, "unsafe solution")
            r.tick()
            hp = tuple(
                2 if r.b[i] == 8 else int(r.b[i] == 5)
                for i, tile in enumerate(level[:64])
                if tile in (5, 8)
            )
            actual = (
                r.s.pos,
                r.s.facing,
                r.s.ammo,
                r.s.gate,
                (r.s.steps + level[68]) & 1,
                hp,
            )
            assert actual == oracle, (number + 1, pc, actual, oracle)
            if r.s.mode == 2:
                break
        assert r.s.mode == 2 and level[r.s.pos] == 3
        # Every room demands a non-movement instruction, or a loop to fit its
        # slot budget. A walking-only route cannot silently bypass the premise.
        walking = solve(level, range(1, 5))
        assert walking is None or len(walking) > level[67], (number + 1, walking)
    assert loops >= 12


def observe_tick(player, label, capture=None, name="frame"):
    m, r = player.m, player.r
    m.until("FN_TICK")
    r.tick()
    screens, banks = [], []
    while True:
        event = lib.until_either(m.p, m.sym[label], m.sym["FRAME_READY"], 12_000_000)
        assert event
        if event == 2:
            break
        screen, bank = m.read(0xC100, 768), m.read(0xC000, 256)
        if screens and (screen, bank) == (screens[-1], banks[-1]):
            continue
        screens.append(screen)
        banks.append(bank)
        if capture:
            m.capture(capture / f"{name}-{len(screens)}.png")
    assert_state(m, r)
    assert lib.audio_peak(m.p) > 0
    return screens, banks


def check(rom=None, capture=None):
    independent_campaign()
    # All failure cases use actual keys. RETURN re-runs the preserved program.
    for program, reason in [
        ([1], 1),
        ([4, 6, 4, 4], 2),
        ([4, 4], 3),
        ([5, 5], 5),
        ([6], 6),
        ([7], 7),
        ([0, 0, 7, 7], 7),
        ([], 8),
    ]:
        p = Player("iron_script", rom=rom, pad=False)
        edit(p, program)
        p.press(5)
        while p.s.running:
            p.wait()
        assert p.s.notice == reason, (program, reason, vars(p.s))
        saved = bytes(p.r.c)
        assert p.s.cursor == min(p.s.pc, p.r.d[67] - 1)
        p.press(5)
        assert p.s.running and bytes(p.r.c) == saved
        assert p.s.pos == p.r.d[64] and p.s.ammo == p.r.d[66]
        assert not p.s.gate and p.s.steps == 0
        p.press(5)
        assert not p.s.running and p.s.notice == 9 and bytes(p.r.c) == saved

    p = Player("iron_script", rom=rom, pad=False)
    edit(p, [1, 2, 3, 4])
    screen = p.m.read(0xC100, 768)
    assert [screen[11 * 32 + 19 + i * 3] for i in range(4)] == [0x48, 0x47, 0x46, 0x49]
    if capture:
        p.m.capture(capture / "rom-arrows.png")
    edit(p, [4, 6, 4, 5, 4, 4, 4])
    p.press(5)
    original_bank = p.m.read(0xC000, 256)
    moving, _ = observe_tick(p, "MOTION_VISIBLE", capture, "move")
    assert moving and p.s.pos == 10 and p.s.origin == 10
    doors, banks = observe_tick(p, "MOTION_VISIBLE", capture, "door")
    assert len(doors) == 3 and len({bank[192:224] for bank in banks}) == 3
    assert all(
        bank[:192] == original_bank[:192] and bank[224:] == original_bank[224:]
        for bank in banks
    )
    assert p.s.gate and p.s.door_pose == 4
    p.wait()
    explosion, _ = observe_tick(p, "VANISH_VISIBLE", capture, "destroy")
    assert len(explosion) == len(set(explosion)) == 4
    assert p.r.b[12] == 0 and p.s.ammo == 0
    while p.s.mode == 1:
        p.wait()
    p.next()
    solve_stage(p)
    p.next()
    # Armor takes two hits. The first has a visible local flash and HP 2 -> 1.
    edit(p, [4, 6, 4, 4, 5, 5, 4, 4])
    p.press(5)
    while p.s.pc < 4:
        p.wait()
    before = bytes(p.r.b)
    p.wait()
    armor = [i for i, v in enumerate(before) if v == 8]
    assert len(armor) == 1 and p.r.b[armor[0]] == 5 and p.s.notice == 10
    assert p.s.ammo == 1 and p.s.mode == 1
    if capture:
        p.m.capture(capture / "armor-hit.png")
    p.wait()
    assert p.r.b[armor[0]] == 0 and p.s.ammo == 0 and p.s.notice == 11
    while p.s.mode == 1:
        p.wait()
    p.next()
    solve_stage(p)
    p.next()
    # The fifth room requires a WAIT. Walking straight into the lit laser fails.
    edit(p, [4])
    p.press(5)
    p.wait()
    assert not p.s.running and p.s.notice == 4 and p.s.cursor == 0
    if capture:
        p.m.capture(capture / "laser-hit.png")
    edit(p, [0, 4, 4, 4, 7])
    p.press(5)
    while p.s.running:
        p.wait()
    assert p.s.mode == 2
    print(
        "PASS: 24 independent factory solutions, 9 stop/retry causes, ROM arrows, 3 door poses, 4 destruction frames, armor and laser timing"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        assert args.rom, "Screenshots require the owned BASIC ROM"
        args.capture.mkdir(parents=True, exist_ok=True)
    check(args.rom.read_bytes() if args.rom else None, args.capture)
