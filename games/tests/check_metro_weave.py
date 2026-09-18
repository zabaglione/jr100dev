"""Observe complete deliveries, stable forecasts and terminal arrival frames."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import assert_state, lib
from replay import Player


def route(player, destination):
    desired = [0, player.r.c[1]] if destination == 0 else [1, destination - 1]
    for junction, value in enumerate(desired):
        if player.r.c[junction] != value:
            if player.s.cursor != junction:
                player.press(2)
            player.press(5)
    assert not player.s.j1 or player.s.route == destination


def arrivals(player, wrong=False, capture=None):
    while player.s.x < 24:
        player.wait()
    m, r = player.m, player.r
    slots = json.loads((m.directory / "build/state_slots.json").read_text())
    fields = ("service", "dest", "next1", "next2", "next3")
    before = tuple(getattr(r.s, field) for field in fields)
    arrival_age = r.s.age + 1
    switches = bytes(r.c)
    bank = m.read(0xC000, 256)
    m.until("FN_TICK")
    r.tick()

    def observe():
        actual = tuple(m.get(slots[f"s.{field}"]) for field in fields)
        assert actual == before, ("Forecast changed during arrival", before, actual)
        assert m.get(slots["s.age"]) == arrival_age
        assert m.get(slots["s.x"]) == 26 and m.get(slots["s.arrival"]) == 1
        assert m.get(slots["s.wrong"]) == wrong
        screen = m.read(0xC100, 768)
        assert [screen[21 * 32 + x] for x in (6, 10, 14)] == [
            33 + destination for destination in before[2:]
        ]
        assert m.read(0xC000, 256) == bank
        for station in range(3):
            y = 5 + station * 5
            assert screen[y * 32 + 29 : y * 32 + 31] == bytes(
                [140 + station * 4, 141 + station * 4]
            )
        if wrong:
            assert screen[65:79] == bytes(
                64 if c == " " else ord(c) - 32 for c in "WRONG PLATFORM"
            )

    if wrong:
        m.until("SCENE_IMPACT")
        observe()  # The cause is visible from the first impact, before its hold.
        if capture:
            m.capture(capture / "wrong-platform.png")
    frames = 0
    while True:
        event = lib.until_either(
            m.p, m.sym["N_MOTION_ENTER"], m.sym["FRAME_READY"], 12_000_000
        )
        assert event
        if event == 2:
            break
        m.until("MOTION_VISIBLE")
        observe()
        frames += 1
        if capture and not wrong and frames == 1:
            m.capture(capture / f"arrival-{before[0]:02}.png")
    assert frames == (1 if wrong else 4), frames
    assert lib.audio_peak(m.p) > 0
    assert_state(m, r)
    assert bytes(r.c) == switches, "Arrival changed a manually set junction"
    if r.s.mode == 1:
        assert r.s.service == (before[0] + 1) % 12
        assert r.s.dest == before[2]
        assert (r.s.next1, r.s.next2) == before[3:]
        assert r.s.age == r.s.route == r.s.arrival == r.s.wrong == 0
        assert (r.s.x, r.s.y, r.s.j1, r.s.j2) == (2, 5, 0, 0)
    else:
        assert tuple(getattr(r.s, field) for field in fields) == before
        assert r.s.age == arrival_age and r.s.x == 26 and r.s.arrival == 1


def tracks(rom, capture):
    # Independently authored centerline waypoints: no single A -> C jump.
    for first, second in ((0, 0), (0, 1), (1, 0), (1, 1)):
        p = Player("metro_weave", rom=rom, pad=False)
        for junction, setting in enumerate((first, second)):
            if setting:
                if p.s.cursor != junction:
                    p.press(2)
                p.press(5)
        assert p.s.x == 2 and p.s.y == 5
        screen = p.m.read(0xC100, 768)
        assert screen[6 * 32 + 9] == 152 + first
        assert screen[11 * 32 + 18] == 152 + second
        assert screen[4 * 32 + 9] == (0x47 if first else 0x49)
        assert screen[9 * 32 + 18] == (0x47 if second else 0x49)
        for y, connected in (
            (6, not first),
            (11, first and not second),
            (16, first and second),
        ):
            assert screen[y * 32 + 25] == (154 if connected else 13)
        assert screen[8 * 32 + 11] == (155 if first else 0x7F)
        prefix = [(x, 5) for x in (2, 4, 6, 8)]
        if first:
            prefix += [(8 + i, 5 + i) for i in range(1, 6)]
            prefix += [(15, 10), (17, 10)]
            expected = prefix + (
                [(17 + i, 10 + i) for i in range(1, 6)] + [(24, 15), (26, 15)]
                if second
                else [(19, 10), (21, 10), (23, 10), (25, 10), (26, 10)]
            )
        else:
            expected = prefix + [(x, 5) for x in range(10, 28, 2)]
        m, r = p.m, p.r
        initial_mutations = lib.host_mutations(m.p)
        if rom:
            assert initial_mutations == 0
        slots = json.loads((m.directory / "build/state_slots.json").read_text())
        waypoints, visible, poses = [(2, 5)], [(2, 5)], set()
        while waypoints[-1][0] != 26:
            m.until("FN_TICK")
            r.tick()
            event = lib.until_either(
                m.p, m.sym["N_GLIDE"], m.sym["FRAME_READY"], 12_000_000
            )
            assert event
            if event == 1:
                end = tuple(m.get(slots[f"s.{axis}"]) for axis in ("x", "y"))
                m.until("GLIDE_VISIBLE")
                mid = tuple(m.get(slots[f"s.effect_{axis}"]) for axis in ("x", "y"))
                screen = m.read(0xC100, 768)
                assert [
                    screen[(mid[1] + dy) * 32 + mid[0] + dx]
                    for dy in (0, 1)
                    for dx in (0, 1)
                ] == [136, 137, 138, 139]
                poses.add(m.read(0xC000 + 64, 32))
                visible += [mid, end]
                waypoints.append(end)
                if capture and first and second and end[1] in (7, 9, 12, 14):
                    m.capture(capture / f"connected-turn-{end[1]:02}.png")
                m.until("FRAME_READY")
            assert_state(m, r)
        assert waypoints == expected, (first, second, waypoints, expected)
        assert all(
            0 <= b[0] - a[0] <= 1 and 0 <= b[1] - a[1] <= 1
            for a, b in zip(visible, visible[1:])
        ), "A visible frame skipped a cell"
        assert len(poses) == (2 if first else 1)
        assert lib.host_mutations(m.p) == initial_mutations

    # Change junction 2 after passing junction 1; it is read at its own point.
    p = Player("metro_weave", rom=rom, pad=False)
    route(p, 1)
    while not p.s.j1:
        p.wait()
    p.press(2)
    p.press(5)
    assert p.r.c[1] == 1 and not p.s.j2 and p.s.route == 1
    while not p.s.j2:
        p.wait()
    assert p.s.route == 2
    p.press(5)  # Switching behind the train must not pull it into another lane.
    assert p.r.c[1] == 0
    while p.s.x < 24:
        p.wait()
    assert p.s.route == 2 and p.s.y == 15
    arrivals(p, wrong=True)


def check(rom=None, capture=None):
    tracks(rom, capture)
    p = Player("metro_weave", rom=rom, pad=False)
    seen = []
    original = p.m.read(0xC000, 256)
    signs = set()
    for delivered in range(12):
        assert p.s.delivered == delivered and p.s.hp == 3
        seen.append(p.s.dest)
        signs.add(p.m.read(0xC000 + 96, 96))
        bank = p.m.read(0xC000, 256)
        assert bank[:64] == original[:64] and bank[192:] == original[192:]
        route(p, p.s.dest)
        arrivals(p, capture=capture if delivered < 7 else None)
    assert Counter(seen) == {0: 4, 1: 4, 2: 4}, seen
    assert any(a == b for a, b in zip(seen, seen[1:]))
    assert len(signs) == 3
    assert p.s.mode == 2 and p.s.delivered == 12 and p.s.route == p.s.dest

    # Misses consume a train, not a successful-delivery count. The queue wraps
    # after twelve departures even when the two values differ.
    p = Player("metro_weave", rom=rom, pad=False)
    for service in range(14):
        wrong = service in (0, 11)
        assert p.s.service == service % 12
        route(p, (p.s.dest + 1) % 3 if wrong else p.s.dest)
        arrivals(p, wrong=wrong)
    assert p.s.mode == 2 and p.s.hp == 1 and p.s.delivered == 12

    p = Player("metro_weave", rom=rom, pad=False)
    for miss in range(3):
        route(p, (p.s.dest + 1) % 3)
        arrivals(p, wrong=True, capture=capture if miss == 0 else None)
        assert p.s.hp == 2 - miss and p.s.delivered == 0
    assert p.s.mode == 3 and p.s.wrong and p.s.route != p.s.dest
    print(
        "PASS: four connected track paths, per-junction timing, single-cell motion, "
        "two train poses, persistent switches, 29 arrivals, stable forecasts, "
        "two-miss recovery, three-miss loss, preserved final platforms and PCM"
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
