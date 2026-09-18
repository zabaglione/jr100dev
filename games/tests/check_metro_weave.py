"""Dispatch choices, queue pressure, deadlines and visible single-cell motion."""

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, assert_state, lib, render_bounds
from replay import Player, metro_dispatch


def model_campaigns():
    schedules, peaks = set(), [0, 0, 0]
    for seed in range(32):
        for level in range(3):
            scores = []
            for express in (False, True):
                r = Model("metro_weave")
                r.entropy = lambda seed=seed: seed
                r.init(level)
                p = SimpleNamespace(r=r, s=r.s, press=r.action)
                schedules.add((r.b[9], *r.c[16:19]))
                for _ in range(600):
                    if r.s.mode != 1:
                        break
                    metro_dispatch(p, express)
                    peaks[level] = max(peaks[level], r.s.active)
                    r.tick()
                    render_bounds(r)
                assert (r.s.mode, r.s.done, r.s.hp) == (2, 8, 3), (
                    seed,
                    level,
                    express,
                    vars(r.s),
                )
                scores.append(r.s.score)
            assert scores[0] == 42 and scores[1] > scores[0], (seed, level, scores)
    assert peaks == [2, 3, 3] and len(schedules) > 20, (peaks, len(schedules))

    # Independently fixed boundary: 8 waiting ticks are allowed, 9 lose the fare.
    for wait, hp, score in ((8, 3, 4), (9, 2, 0)):
        r = Model("metro_weave")
        r.b[0] = 8
        r.b[9] = 0
        r.b[15] = 1
        r.b[12] = 26  # Six movement ticks already used from the 32-tick budget.
        r.c[2] = 1
        for _ in range(wait):
            r.env["advance_train"](0)
        assert r.b[0] == 8 and r.s.hp == 3
        r.c[2] = 0
        for _ in range(18):
            r.env["advance_train"](0)
        assert (r.s.hp, r.s.score) == (hp, score), (wait, vars(r.s))

    # Matching deliveries build the multiplier; a wrong station removes it.
    r = Model("metro_weave")
    for route, express, reward in (
        (0, 0, 2),
        (0, 1, 8),
        (0, 1, 12),
        (1, 0, 0),
        (0, 0, 2),
    ):
        r.b[0], r.b[3], r.b[6], r.b[9], r.b[15] = 26, 5 + 5 * route, route, 0, express
        r.s.active = 1
        r.env["arrive"](0)
        assert r.s.reward == reward
    assert (r.s.score, r.s.hp, r.s.chain) == (24, 2, 1)

    # Surviving eight deliveries is insufficient when the shift quota is missed.
    r = Model("metro_weave")
    r.s.done, r.s.score = 7, 0
    r.b[6] = r.b[9]
    r.env["arrive"](0)
    assert r.s.mode == 3 and r.s.hp == 3


def native_campaign(rom, capture):
    p = Player("metro_weave", rom=rom, pad=False)
    initial_mutations = lib.host_mutations(p.m.p)
    original = p.m.read(0xC000, 256)
    concurrency, arrivals = set(), 0
    while True:
        while p.s.mode == 1:
            done = p.s.done
            metro_dispatch(p)
            before = bytes(p.r.b)
            if p.s.mode == 1:
                p.wait()
            concurrency.add((p.s.level, p.s.active))
            arrivals += p.s.done - done
            for i in range(3):
                if 0 < before[i] < 25 and p.r.b[i]:
                    assert 0 <= p.r.b[i] - before[i] <= 1
                    assert 0 <= p.r.b[3 + i] - before[3 + i] <= 1
            bank = p.m.read(0xC000, 256)
            assert bank[:96] == original[:96] and bank[192:] == original[192:]
            if capture and p.s.level == 1 and p.s.active == 3:
                p.m.capture(capture / "three-trains.png")
        assert p.s.mode == 2 and p.s.hp == 3 and p.s.score >= 44
        if not p.next():
            break
    assert arrivals == 24 and (1, 3) in concurrency and (2, 3) in concurrency, (
        arrivals,
        concurrency,
    )
    assert lib.host_mutations(p.m.p) == initial_mutations
    assert lib.audio_peak(p.m.p) > 0


def native_signals(rom, capture):
    p = Player("metro_weave", rom=rom, pad=False)
    p.press(3)  # Hold junction 1, not the entire simulation.
    while p.r.b[0] < 8:
        p.wait()
    p.press(5)
    assert p.s.active == 2 and p.r.b[15 + 1] == 1
    queue = bytes(p.r.c[16:19])
    p.press(5)  # A full yard must not eat the next forecast or change its fare.
    assert p.s.issued == 2 and bytes(p.r.c[16:19]) == queue
    for _ in range(34):
        p.wait()
    assert p.r.b[0] == 8 and p.r.b[1] == 5 and p.r.b[16] == 2
    assert p.s.hp == 3  # The late penalty is explained on arrival, not invisibly.
    if capture:
        p.m.capture(capture / "signal-and-late-express.png")
    if p.r.c[0] != int(p.r.b[9] != 0):
        p.press(4)
    p.press(3)
    while p.s.done < 2:
        metro_dispatch(p, express=False)
        p.wait()
    assert p.s.hp == 2 and p.s.chain == 0 and p.s.reward == 0, vars(p.s)
    if capture:
        p.m.capture(capture / "late-arrival.png")

    # A stopped station queue consumes the express allowance in real time.
    r = Model("metro_weave")
    r.b[0], r.b[3], r.b[6], r.b[9], r.b[15] = 25, 5, 0, 0, 1
    r.c[8] = 3
    for remaining in (2, 1):
        r.tick()
        assert r.c[8] == remaining and r.b[0] == 25
    r.tick()
    assert r.s.done == 1 and r.s.reward == 4

    # Three routing errors end the game; no silent automatic switch changes.
    p = Player("metro_weave", rom=rom, pad=False)
    while p.s.mode == 1:
        for junction, x, y in ((0, 8, 5), (1, 17, 10)):
            approaching = [
                i
                for i in range(3)
                if p.r.b[i] and p.r.b[3 + i] == y and x - 3 <= p.r.b[i] <= x
            ]
            if approaching:
                i = max(approaching, key=lambda i: p.r.b[i])
                wrong = (p.r.b[9 + i] + 1) % 3
                desired = int(wrong != 0) if junction == 0 else int(wrong == 2)
                if p.r.c[junction] != desired:
                    if p.s.cursor != junction:
                        p.press(2)
                    p.press(4)
        settings = bytes(p.r.c[:4])
        p.wait()
        assert bytes(p.r.c[:4]) == settings
    assert p.s.hp == 0 and p.s.mode == 3 and p.s.done == 3
    assert_state(p.m, p.r)


def check(rom=None, capture=None):
    model_campaigns()
    native_campaign(rom, capture)
    native_signals(rom, capture)
    print(
        "PASS: 192 seeded shift/policy runs; three shifts, risk/reward, 8/9-tick deadline boundary, quotas, signals, station queues, live train spacing, PCM and input-only native play"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    if args.capture:
        assert args.rom
        args.capture.mkdir(parents=True, exist_ok=True)
    check(args.rom.read_bytes() if args.rom else None, args.capture)
