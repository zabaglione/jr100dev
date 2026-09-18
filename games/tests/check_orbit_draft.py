"""Independent mission/draft checks and native card/rotation animation checks."""

import argparse
import itertools
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, action, assert_state
from machine import KEYS, lib
from replay import Player, orbit_rotate, solve_orbit

LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def oracle(board, level):
    lines = [
        line
        for line in LINES
        if board[line[0]] != 255 and len({board[i] for i in line}) == 1
    ]
    kinds = {board[line[0]] for line in lines}
    progress = (
        len(lines),
        len(kinds),
        sum(all(board[i] == 0 for i in line) for line in LINES[-2:]),
    )[level]
    return len(lines), progress, kinds, {i for line in lines for i in line}


def shifted(board, axis, orbit):
    result = list(board)
    positions = LINES[orbit if axis == 0 else 3 + orbit]
    for source, target in zip(positions, positions[1:] + positions[:1]):
        result[target] = board[source]
    return result


def can_fill(board, level):
    holes = [i for i, value in enumerate(board) if value == 255]
    for values in itertools.product(range(3), repeat=len(holes)):
        trial = list(board)
        for i, value in zip(holes, values):
            trial[i] = value
        if oracle(trial, level)[1] >= (3 if level == 1 else 2):
            return True
    return False


def rules_checks():
    model = Model("orbit_draft")
    rng = random.Random(71)
    boards = [[255] * 9, [0] * 9, [1] * 9, [0, 1, 0, 1, 0, 2, 0, 2, 0]]
    for line in LINES:
        board = [255] * 9
        for i in line:
            board[i] = 2
        boards.append(board)
    boards += [[rng.choice((0, 1, 2, 255)) for _ in range(9)] for _ in range(100)]
    for level in range(3):
        for board in boards:
            model.init(level)
            model.b[:9] = bytes(board)
            expected, progress, kinds, marked = oracle(board, level)
            model.env["evaluate"]()
            assert (model.s.lines, model.s.progress) == (expected, progress)
            assert model.s.types == sum(1 << kind for kind in kinds)
            assert {i for i, value in enumerate(model.c[:9]) if value} == marked
            model.env["evaluate"]()
            assert model.s.gain == 0 and not any(model.d[:9])
            # Breaking a line removes its marks and goal progress immediately.
            model.b[:9] = bytes([255] * 9)
            model.env["evaluate"]()
            assert model.s.lines == model.s.progress == model.s.types == 0
            assert not any(model.c[:9]) and not any(model.d[:9])

        model.init(level)
        start = list(model.b[:9])
        assert can_fill(start, level) == (level == 0)
        one_spin = [
            shifted(start, axis, orbit) for axis in range(2) for orbit in range(3)
        ]
        assert any(can_fill(board, level) for board in one_spin) == (level != 2)
        if level == 2:
            assert any(
                can_fill(shifted(board, axis, orbit), level)
                for board in one_spin
                for axis in range(2)
                for orbit in range(3)
            )
        # Initial blockers cannot meet the later missions with fewer rotations,
        # even when later cards are unrestricted and rotation timing is arbitrary.

    for axis in range(2):
        for orbit in range(3):
            model.init()
            model.b[:9] = bytes([0, 255, 2, 1, 2, 255, 255, 0, 1])
            before = list(model.b[:9])
            model.s.axis, model.s.orbit = axis, orbit
            model.env["rotate"]()
            assert list(model.b[:9]) == shifted(before, axis, orbit)
            assert model.s.spins == 1 and model.s.placed == 3
    model.init()
    model.s.orbit = 1
    model.env["rotate"]()
    assert model.s.notice == 3 and model.s.spins == 2

    for level in range(3):
        # Exhaust every sequence of six left/right draft choices.
        for choices in itertools.product(range(2), repeat=6):
            model.init(level)
            cards = model.metadata["dataTables"]["decks"][level * 7 : level * 7 + 7]
            expected_hand = cards[:2]
            for turn, offer in enumerate(choices):
                if model.s.offer != offer:
                    model.action(4)
                assert model.s.card == expected_hand[offer]
                model.action(5)
                occupied = next(i for i in range(9) if model.b[i] != 255)
                model.s.cursor = occupied
                before = bytes(model.b)
                model.action(5)
                assert bytes(model.b) == before and model.s.placed == turn + 3
                target = next(i for i in range(9) if model.b[i] == 255)
                model.s.cursor = target
                model.action(5)
                assert model.b[target] == expected_hand[offer]
                if turn < 5:
                    expected_hand[offer] = cards[turn + 2]
                assert list(model.d[16:18]) == expected_hand
                assert model.s.drawn == min(turn + 3, 7)
                assert model.s.placed == turn + 4

    # A full board can still be rescued by its remaining spin.
    model.init()
    goal = [0, 1, 2] * 3
    model.b[:9] = bytes(shifted(shifted(goal, 0, 0), 0, 0))
    model.s.placed, model.s.spins = 9, 1
    model.env["evaluate"]()
    model.env["finish"]()
    assert model.s.mode == 1 and model.s.cursor == 10 and model.s.notice == 2
    model.action(5)
    model.action(5)
    assert model.s.mode == 2 and list(model.b[:9]) == goal and model.s.spins == 0

    for level, message in enumerate(
        ("NEED TWO MATCHING LINES", "NEED A, B AND C LINES", "NEED BOTH A DIAGONALS")
    ):
        for spins in (0, 1):
            model.init(level)
            causes = []
            model.env["lose"] = causes.append
            model.b[:9] = bytes([0, 1, 2, 2, 0, 1, 1, 2, 1])
            model.s.placed, model.s.spins = 9, spins
            model.env["evaluate"]()
            model.env["finish"]()
            if spins:
                assert not causes
                model.s.cursor = 9
                model.action(5)
            assert causes == [message]


class MotionPlayer(Player):
    def __init__(self, rom, capture):
        super().__init__("orbit_draft", rom, pad=False)
        self.motion_capture = capture
        self.slots = json.loads((self.directory / "build/state_slots.json").read_text())
        self.bank = self.m.read(0xC000, 256)
        self.flights = self.rotations = self.matches = 0

    def field(self, name):
        return self.m.get(self.slots["s." + name])

    def press(self, a):
        placement = (
            self.s.phase == 1 and self.s.cursor < 9 and self.r.b[self.s.cursor] == 255
        )
        rotation = self.s.phase == 2
        if a != 5 or not (placement or rotation):
            return super().press(a)
        before = bytes(self.r.b)
        hand = bytes(self.r.d[16:18])
        placed, spins, offer = self.s.placed, self.s.spins, self.s.offer
        target = (3 + self.s.cursor % 3 * 6, 6 + self.s.cursor // 3 * 5)
        self.r.action(5)
        motions, slides, glows = [], [], []
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
            assert self.m.get("MODE") == 1
            assert self.m.read("D_ARRAY", 18)[16:18] == hand
            bank = self.m.read(0xC000, 256)
            assert bank[:96] == self.bank[:96] and bank[128:] == self.bank[128:]
            if self.field("flying") or self.field("rotating"):
                assert self.m.read("B_ARRAY", 128) == before
                assert self.field("placed") == placed and self.field("spins") == spins
                if self.field("flying"):
                    motions.append((self.field("fx"), self.field("fy")))
                else:
                    slides.append(self.field("slide"))
            else:
                assert self.m.read("B_ARRAY", 128) == bytes(self.r.b)
                glows.append(self.field("glow"))
                assert self.field("progress") == oracle(self.r.b, self.s.level)[1]
            if self.motion_capture and (self.rotations == 0 or self.s.gain):
                self.m.capture(
                    self.motion_capture
                    / f"action-{self.actions:02}-frame-{frame:02}.png"
                )
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
        if placement:
            assert len(motions) == len(set(motions)) == 5
            assert motions[0] == (23 + offer * 4, 5) and motions[-1] == target
            self.flights += 1
        else:
            assert slides == ([0, 2, 4, 6] if self.s.axis == 0 else [0, 2, 4, 5])
            self.rotations += 1
        assert glows == ([0, 1, 2, 3, 0] if self.s.gain else [0])
        self.matches += int(self.s.gain > 0)
        self.actions += 1


def check(rom=None, capture=None):
    rules_checks()
    p = MotionPlayer(rom, capture)
    for level in range(3):
        solve_orbit(p)
        assert p.s.mode == 2 and p.s.level == level
        assert p.s.progress >= p.s.target
        p.next()
    assert p.flights == 18 and p.rotations == 4 and p.matches >= 7
    p.finish()
    # Exercise cancellation, no-op and depleted-spin menu through the CPU too.
    p = Player("orbit_draft")
    p.press(2)
    p.go(10, 3)
    p.press(5)
    p.press(2)
    p.press(5)
    assert p.s.phase == 2 and p.s.notice == 3 and p.s.spins == 2
    p.press(3)
    assert p.s.phase == 1 and p.s.spins == 2
    orbit_rotate(p, 1, 0)
    p.go(11, 3)
    p.press(5)
    p.press(1)
    assert p.s.phase == 1 and p.s.spins == 1
    orbit_rotate(p, 1, 0)
    p.go(11, 3)
    p.press(5)
    assert p.s.phase == 1 and p.s.notice == 1 and p.s.spins == 0
    p = Player("orbit_draft", rom, pad=False)
    for message in (
        "NEED TWO MATCHING LINES",
        "NEED A, B AND C LINES",
        "NEED BOTH A DIAGONALS",
    ):
        for _ in range(6):
            p.press(5)
            p.go(next(i for i in range(9) if p.r.b[i] == 255), 3)
            p.press(5)
        assert p.s.mode == 1 and p.s.placed == 9 and p.s.spins == 2
        p.go(9, 3)
        p.press(5)
        assert p.s.mode == 3
        address = p.m.get("LOSS_MESSAGE") * 256 + p.m.get(p.m.sym["LOSS_MESSAGE"] + 1)
        assert p.m.read(address, len(message)) == message.encode("ascii")
        assert p.m.read(0xC100 + 21 * 32 + 1, len(message)) == bytes(
            64 if c == " " else ord(c) - 32 for c in message
        )
        action(p.m, p.r, 5, confirm=True)
        assert p.s.placed == 3 and p.s.spins == 2
        solve_orbit(p)
        p.next()
    print(
        "PASS: orbit_draft, independent three-mission oracle, minimum spins, all drafts, cyclic rows/columns, full-board rescue, failure causes, three-stage native motion and input isolation"
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
