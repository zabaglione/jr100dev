"""Independent 4x4 scoring, draft, gravity and input-only native motion checks."""

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, action, assert_state
from machine import KEYS, Machine, lib
from orbit_draft.strategy import EMPTY, LINES, View, matches, play, resolve
from replay import Player, orbit_rotate, orbit_tool, solve_orbit


def rules_checks():
    r = Model("orbit_draft")
    rng = random.Random(71)
    assert len(set(LINES)) == 24
    assert set(LINES) == {tuple(r.env["paths"][i : i + 3]) for i in range(0, 72, 3)}
    # Exhaust all occupied-cell masks to bound each 8-bit score addition.
    maximum = [0] * 17
    masks = [sum(1 << i for i in line) for line in LINES]
    for mask in range(1 << 16):
        lines = sum(mask & line == line for line in masks)
        count = mask.bit_count()
        maximum[count] = max(maximum[count], lines)
    for chain in range(1, 6):
        for count in range(3, 17 - (chain - 1) * 3):
            assert count * 2 * chain + max(0, maximum[count] - 1) * 2 < 100

    boards = [[EMPTY] * 16, [0] * 16]
    for line in LINES:
        board = [EMPTY] * 16
        for i in line:
            board[i] = 2
        boards.append(board)
    boards += [
        [rng.choice((0, 1, 2, 3, 4, EMPTY)) for _ in range(16)] for _ in range(400)
    ]
    chains = set()
    for board in boards:
        r.init()
        r.b[:16] = bytes(board)
        lines, marked = matches(board)
        r.env["evaluate"]()
        assert r.s.lines == len(lines)
        assert {i for i, v in enumerate(r.c[:16]) if v} == marked
        expected, waves = resolve(tuple(board))
        r.env["resolve"]()
        assert tuple(r.b[:16]) == expected
        points = sum(w[2] for w in waves)
        assert r.s.score_hi * 100 + r.s.score_lo == points
        assert r.s.progress == min(99, points)
        assert r.s.chain == len(waves)
        assert r.s.spins == min(4, 2 + len(waves))
        chains.add(len(waves))
    assert {0, 1, 2} <= chains
    # Cross-check more action outcomes, including both offers and both axes.
    for _ in range(160):
        r.init()
        board = [rng.choice((0, 1, 2, 3, 4, EMPTY)) for _ in range(16)]
        r.b[:16] = bytes(board)
        view = View(tuple(board), tuple(r.d[16:18]), tuple(r.d[18:21]), r.s.spins)
        spin = rng.randrange(2)
        pick, target = rng.randrange(2), rng.randrange(4)
        choice = ("spin" if spin else "drop", pick, target)
        expected = play(view, choice)
        r.s.phase = 1
        r.s.tool = pick + 1 if spin else 0
        r.s.cursor = target * 4 if spin and pick == 0 else target
        r.s.offer = pick
        r.s.card = r.d[16 + pick]
        r.action(5)
        if expected:
            future, points, waves = expected
            assert tuple(r.b[:16]) == future.board
            assert r.s.spins == future.spins
            assert r.s.score_hi * 100 + r.s.score_lo == points
            if not spin:
                assert tuple(r.d[16:18]) == future.hand
                assert tuple(r.d[18:20]) == future.forecast
        if spin:
            assert r.s.tool == pick + 1 and r.s.phase == 1

    # Every external timer seed starts with four distinct cards and two offers.
    decks = set()
    for seed in range(256):
        r.entropy = lambda seed=seed: seed
        r.init()
        assert len(set(r.b[12:16])) == 4
        assert r.d[16] not in r.b[12:16] and r.d[17] in r.b[12:16]
        decks.add(tuple(r.d[16:21]))
    assert len(decks) > 100
    start = (r.s.rng_hi, r.s.rng_lo)
    seen = set()
    counts = [0] * 5
    for _ in range(65535):
        key = (r.s.rng_hi, r.s.rng_lo)
        assert key not in seen
        seen.add(key)
        counts[r.env["deal"]()] += 1
    assert (r.s.rng_hi, r.s.rng_lo) == start
    assert max(counts) - min(counts) < 300
    r.init()
    r.s.score_hi, r.s.score_lo, r.s.points = 99, 96, 78
    r.env["credit"]()
    assert (r.s.score_hi, r.s.score_lo) == (99, 99)
    r.env["credit"]()
    assert (r.s.score_hi, r.s.score_lo) == (99, 99)
    for _ in range(300):
        r.env["advance"]()
    assert r.s.level == 254 and r.s.target == 60
    r.init()
    r.b[:16] = bytes((row + 2 * col) % 5 for row in range(4) for col in range(4))
    r.s.phase, r.s.tool, r.s.cursor = 1, 2, 4
    r.env["finish"]()
    assert r.s.mode == 1 and r.s.tool == 2 and r.s.cursor == 4
    r.s.spins = 0
    r.env["finish"]()
    assert r.s.mode == 3
    r.init()
    r.b[:16] = bytes([EMPTY] * 16)
    r.s.phase, r.s.tool = 1, 1
    r.action(5)
    assert r.s.spins == 2 and r.s.notice == 4 and r.s.tool == 1
    r.s.cursor = 18
    r.action(4)
    assert r.s.cursor == 18
    print(
        "PASS: independent 24-line oracle, 4x4 gravity/chains, five-card drafts, 65535-state deck, score bounds and saturation"
    )


class MotionPlayer(Player):
    def __init__(self, rom, capture):
        super().__init__("orbit_draft", rom, pad=False)
        self.motion_capture = capture
        self.slots = json.loads((self.directory / "build/state_slots.json").read_text())
        self.bank = self.m.read(0xC000, 256)
        self.covered = set()
        self.flights = self.rotations = self.matches = 0

    def field(self, name):
        return self.m.get(self.slots["s." + name])

    def press(self, a):
        moving = self.s.phase == 1 and self.s.cursor < 16
        if a != 5 or not moving:
            return super().press(a)
        before = bytes(self.r.b)
        hand = bytes(self.r.d[16:21])
        tool, cursor = self.s.tool, self.s.cursor
        self.r.action(5)
        flights, slides, glows, falls = [], [], [], []
        lib.key(self.m.p, *KEYS[5], 1)
        self.m.until("DISPATCH")
        frame = 0
        while True:
            event = lib.until_either(
                self.m.p,
                self.m.sym["N_MOTION_ENTER"],
                self.m.sym["FRAME_READY"],
                12_000_000,
            )
            assert event
            if event == 2:
                break
            self.m.until("MOTION_VISIBLE")
            frame += 1
            assert self.m.read(0xC000, 256) == self.bank
            assert self.m.read("D_ARRAY", 21)[16:21] == hand
            stage = None
            if self.field("flying"):
                flights.append((self.field("fx"), self.field("fy")))
                stage = "flight"
            elif self.field("rotating"):
                slides.append(self.field("slide"))
                stage = "row" if tool == 1 else "col"
            elif self.field("glow"):
                glows.append(self.field("glow"))
                stage = "burst"
            elif self.field("falling"):
                falls.append(self.field("slide"))
                stage = "fall"
            if self.field("flying") or self.field("rotating"):
                assert self.m.read("B_ARRAY", 128) == before
            if stage:
                if self.motion_capture and stage not in self.covered:
                    self.m.capture(self.motion_capture / f"{stage}-{frame:02}.png")
                if (
                    stage == "burst"
                    and self.field("glow") == 3
                    or stage == "fall"
                    and self.field("slide") == 4
                    or stage == "flight"
                    and len(flights) == 5
                    or stage in ("row", "col")
                    and len(slides) == 4
                ):
                    self.covered.add(stage)
            lib.key(self.m.p, *KEYS[5], 0)
            if frame == 2:
                lib.key(self.m.p, *KEYS[4], 1)
            if frame == 4:
                lib.key(self.m.p, *KEYS[4], 0)
        lib.key(self.m.p, *KEYS[5], 0)
        lib.key(self.m.p, *KEYS[4], 0)
        self.m.until("INPUT_DONE")
        assert_state(self.m, self.r)
        assert self.m.get("MOTION_ACTIVE") == self.m.get("KEY_PENDING") == 0
        if flights:
            assert len(flights) == 5
            target = max(i for i in range(cursor % 4, 16, 4) if before[i] == EMPTY)
            assert flights[0] == (2 + cursor % 4 * 5, 3)
            assert flights[-1] == (2 + cursor % 4 * 5, 4 + target // 4 * 4)
            self.flights += 1
        if slides:
            assert slides == ([0, 1, 3, 5] if tool == 1 else [0, 1, 2, 4])
            self.rotations += 1
        assert glows == [1, 2, 3] * (len(glows) // 3)
        assert falls == [0, 2, 4] * (len(falls) // 3)
        self.matches += len(glows) // 3
        self.actions += 1


def check(rom=None, capture=None):
    rules_checks()
    p = MotionPlayer(rom, capture)
    # Explicit repeat inputs keep either tool selected, even at zero budget.
    orbit_rotate(p, 0, 3)
    p.press(5)
    assert p.s.tool == 1 and p.s.spins == 0
    p.press(5)
    assert p.s.tool == 1 and p.s.notice == 1
    orbit_tool(p, 2)
    p.press(5)
    assert p.s.tool == 2 and p.s.notice == 1
    orbit_tool(p, 0)
    assert p.s.tool == 0 and p.s.phase == 0
    # Restart through the confirmation to restore budget and draw a new deck.
    action(p.m, p.r, 6, confirm=True)
    orbit_rotate(p, 1, 0)
    p.press(5)
    assert p.s.tool == 2
    action(p.m, p.r, 6, confirm=True)
    for level in range(8):
        solve_orbit(p)
        assert p.s.mode == 2 and p.s.level == level
        assert p.s.progress >= p.s.target
        if level < 7:
            before = (
                bytes(p.r.b),
                bytes(p.r.d),
                p.s.rng_hi,
                p.s.rng_lo,
                p.s.tool,
                p.s.score_hi,
                p.s.score_lo,
                p.s.spins,
            )
            goal = p.s.target
            p.next()
            after = (
                bytes(p.r.b),
                bytes(p.r.d),
                p.s.rng_hi,
                p.s.rng_lo,
                p.s.tool,
                p.s.score_hi,
                p.s.score_lo,
                p.s.spins,
            )
            assert (
                before == after
                and p.s.progress == 0
                and p.s.target == min(60, goal + 6)
            )
    assert {"flight", "row", "col", "burst", "fall"} <= p.covered
    p.finish()
    # A new game after round eight must not index a nonexistent level table.
    old_score = p.s.score_hi, p.s.score_lo
    action(p.m, p.r, 6, confirm=False)
    assert p.s.level == 7 and (p.s.score_hi, p.s.score_lo) == old_score
    action(p.m, p.r, 6, confirm=True)
    assert p.s.level == 0 and p.s.target == 12 and p.s.score_hi == p.s.score_lo == 0
    # Reach defeat with ordinary inputs while deliberately avoiding matches.
    failed = Player("orbit_draft", rom, pad=False)
    orbit_rotate(failed, 0, 3)
    failed.press(5)
    orbit_tool(failed, 0)
    for _ in range(12):
        view = View(
            tuple(failed.r.b[:16]),
            tuple(failed.r.d[16:18]),
            tuple(failed.r.d[18:21]),
            failed.s.spins,
        )
        choices = []
        for offer in range(2):
            for col in range(4):
                result = play(view, ("drop", offer, col))
                if result and result[1] == 0:
                    choices.append((offer, col))
        assert choices
        offer, col = choices[0]
        if failed.s.offer != offer:
            failed.press(4)
        failed.press(5)
        failed.go(failed.s.cursor // 4 * 4 + col, 4)
        failed.press(5)
    assert failed.s.mode == 3 and failed.s.spins == 0
    address = failed.m.get("LOSS_MESSAGE") * 256 + failed.m.get(
        failed.m.sym["LOSS_MESSAGE"] + 1
    )
    message = b"FULL BOARD - NO SPINS"
    assert failed.m.read(address, len(message)) == message
    action(failed.m, failed.r, 5, confirm=False)
    assert failed.s.mode == 3
    action(failed.m, failed.r, 5, confirm=True)
    assert failed.s.mode == 1 and failed.s.level == 0
    origins = set()
    for delay in (10000, 120000, 280000, 610000):
        m = Machine("orbit_draft", rom=rom)
        lib.ticks(m.p, delay)
        m.action(5)
        r = Model("orbit_draft", machine=m)
        r.s.action = 5
        assert_state(m, r)
        origins.add(r.s.origin)
    assert len(origins) > 1
    print(
        "PASS: persistent ROW/COL, eight rounds carry state, new-game reset, timer seeds, five motion types, immutable PCG and input isolation"
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
