"""Exercise generated MB8861H games through keyboard/pad and inspect their state."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import EIGHT_KEYS, KEYS, PADS, Machine, lib

ROOT = Path(__file__).resolve().parents[1]


class State:
    def __getattr__(self, name):
        return 0

    def __setattr__(self, name, value):
        self.__dict__[name] = int(value) & 255


class Model:
    def __init__(self, name, machine=None):
        self.name = name
        self.metadata = json.loads((ROOT / name / "game.json").read_text())
        self.best = bytearray(self.metadata.get("levels", 10))
        self.held = 0
        self.s = State()
        self.s.mode = 1
        self.b = bytearray(128)
        self.c = bytearray(128)
        self.d = bytearray(128)
        self.entropy = lambda: 0
        if machine is not None and self.metadata.get("seededDeck"):
            slots = json.loads((ROOT / name / "build/state_slots.json").read_text())
            # The timer is an external input, sampled once at the new-game edge.
            # Read the retained sample; all subsequent PRNG steps are modeled.
            self.entropy = lambda: machine.get(slots["s.origin"])
        self.env = {
            "s": self.s,
            "b": self.b,
            "c": self.c,
            "d": self.d,
            "tile": lambda *a: None,
            "stamp": lambda *a: None,
            "text": lambda *a: None,
            "letter": lambda *a: None,
            "number": lambda *a: None,
            "sound": lambda *a: None,
            "animate": lambda *a: None,
            "hold": lambda *a: None,
            "face": lambda *a: None,
            "flip": lambda *a: None,
            "impact": lambda *a: None,
            "vanish": lambda *a: None,
            "mover": lambda *a: None,
            "held": lambda: self.held,
            "entropy": lambda: self.entropy(),
            "win": self.win,
            "lose": lambda *a: setattr(self.s, "mode", 3),
        }
        self.env.update(
            {
                k: bytearray(v)
                for k, v in json.loads((ROOT / name / "game.json").read_text())
                .get("dataTables", {})
                .items()
            }
        )
        exec(  # noqa: S102 - executes only project-owned rule sources for QA
            (ROOT / "native/support.py").read_text()
            + "\n"
            + (ROOT / name / "rules.py").read_text(),
            self.env,
        )
        self.init()

    def init(self, level=0):
        self.s.__dict__.clear()
        self.s.mode = 1
        self.s.level = level
        self.b[:] = bytes(128)
        self.c[:] = bytes(128)
        self.d[:] = bytes(128)
        levels = ROOT / self.name / "levels.json"
        if levels.exists():
            values = json.loads(levels.read_text())[level]
            self.d[: len(values)] = bytes(values)
        self.env["init"]()

    def action(self, a):
        self.s.action = a
        self.env["act"]()

    def win(self):
        self.s.mode = 2
        if self.metadata.get("rankedCampaign"):
            self.best[self.s.level] = max(self.best[self.s.level], self.s.stars)

    def dispatch_ranked(self, a):
        mode, level = self.s.mode, self.s.level
        if mode == 5:
            self.s.mode = 0
        elif mode == 6:
            if a == 7:
                self.s.mode = 7
            elif a == 5:
                self.init(level)
            elif a == 6:
                self.s.mode = 0
            elif a in (1, 2, 3, 4):
                self.s.level = (level + {1: -5, 2: 5, 3: -1, 4: 1}[a]) % len(self.best)
        elif a == 8:
            self.s.mode = 6
        elif mode == 0:
            if a == 7:
                self.s.mode = 7
            elif a == 5:
                self.init(level)
            else:
                self.s.mode = 5
        elif a == 6:
            self.init(level)
        elif mode == 1:
            self.action(a)
        elif a == 5:
            if mode == 2:
                if level + 1 < len(self.best):
                    self.init(level + 1)
                else:
                    self.s.mode = 4
            else:
                self.s.mode = 0
        self.s.action = a

    def tick(self):
        self.env["tick"]()


def render_bounds(model):
    def check(x, y, width=1, height=1):
        assert 0 <= x and 0 <= y and x + width <= 32 and y + height <= 24, (
            model.name,
            "drawing outside screen",
            x,
            y,
            width,
            height,
        )

    model.env.update(
        {
            "tile": lambda x, y, g: check(x, y, 2, 2),
            "stamp": lambda x, y, g: check(x, y, 2, 2),
            "mover": lambda dest, start, g, left: check(
                left + dest % 8 + start % 8, 3 + dest // 8 + start // 8, 2, 2
            ),
            "letter": lambda x, y, g: check(x, y),
            "number": lambda x, y, n: check(x, y, 3),
            "text": lambda x, y, t: check(x, y, len(t)),
        }
    )
    model.env["draw"]()


def assert_state(machine, model):
    render_bounds(model)
    slots = json.loads((machine.directory / "build/state_slots.json").read_text())
    for key, label in slots.items():
        if key.startswith("s."):
            field = key[2:]
            assert machine.get(label) == getattr(model.s, field), (
                f"{machine.directory.name} {field}: native={machine.get(label)}, model={getattr(model.s, field)}"
            )
    for name in ("b", "c", "d"):
        assert machine.read(name.upper() + "_ARRAY", 128) == bytes(
            getattr(model, name)
        ), f"{machine.directory.name} {name} array differs"
    if machine.metadata.get("rankedCampaign"):
        assert machine.read("BEST", len(model.best)) == bytes(model.best), (
            "Best ratings differ"
        )
    assert lib.min_sp(machine.p) >= 0x3E00, "Stack exceeded reserved 512 bytes"
    assert machine.read(0x300, len(machine.code)) == machine.code, "Code/data changed"


def begin(name, rom=None):
    m = Machine(name, rom=rom)
    m.action(5)
    r = Model(name, machine=m)
    r.s.action = 5
    assert_state(m, r)
    return m, r


def action(m, r, a, pad=False, confirm=None):
    if m.metadata.get("rankedCampaign") and (
        a == 6 and r.s.mode in (1, 2, 3, 4) or a == 8 and r.s.mode == 1
    ):
        assert confirm is not None, "Reset/abandon needs an explicit test answer"
        m.action(a, pad=pad)
        m.answer_reset(confirm, pad=pad)
        if confirm:
            r.dispatch_ranked(a)
        else:
            r.s.action = a
        assert_state(m, r)
        return
    r.held = a
    keys = EIGHT_KEYS if m.metadata.get("directions") == 8 else KEYS
    if pad:
        lib.pad(m.p, PADS[a])
    else:
        lib.key(m.p, *keys[a], 1)
    while True:
        event = lib.until_either(m.p, m.sym["DISPATCH"], m.sym["FN_TICK"], 10_000_000)
        assert event, "No input or clock event"
        if event == 1:
            break
        r.held = m.get("KEY_LAST")  # Input becomes visible at the matrix scan.
        r.tick()
        m.until("FRAME_READY")
        assert_state(m, r)
        if m.get("KEY_LAST") == a and not m.get("KEY_PENDING"):
            # A hit hold intentionally discards input. Issue a fresh edge once
            # the contact scene has finished, just as a player must do.
            if pad:
                lib.pad(m.p, 0)
            else:
                lib.key(m.p, *keys[a], 0)
            m.until("INPUT_DONE")
            if pad:
                lib.pad(m.p, PADS[a])
            else:
                lib.key(m.p, *keys[a], 1)
    if (
        a == 6
        and not m.metadata.get("rankedCampaign")
        and (r.s.mode == 1 or m.metadata.get("endless") and r.s.mode in (2, 3))
    ):
        assert confirm is not None, "Reset needs an explicit test answer"
        m.until("CONFIRM_READY")
        if pad:
            lib.pad(m.p, 0)
        else:
            lib.key(m.p, *keys[a], 0)
        m.until("INPUT_DONE")
        m.answer_reset(confirm, pad=pad)
        if confirm:
            r.init(r.s.level)
        r.s.action = a
        r.held = 0
        assert_state(m, r)
        return
    if r.s.mode == 3 and a == 5 and not m.metadata.get("rankedCampaign"):
        assert confirm is not None, "Retry needs an explicit test answer"
        m.until("CONFIRM_READY")
        if pad:
            lib.pad(m.p, 0)
        else:
            lib.key(m.p, *keys[a], 0)
        m.until("INPUT_DONE")
        m.answer_reset(confirm, pad=pad)
        if confirm:
            r.init(r.s.level)
        r.s.action = a
        r.held = 0
        assert_state(m, r)
        return
    if m.metadata.get("rankedCampaign"):
        r.dispatch_ranked(a)
    elif r.s.mode == 1:
        r.action(a)
    else:
        mode = r.s.mode
        r.s.action = a
        if a == 5:
            if mode == 3:
                r.init(r.s.level)
            elif mode == 2 and m.metadata.get("endless"):
                r.env["advance"]()
            elif mode == 2:
                level = r.s.level + 1
                if level == m.metadata.get("levels", 10):
                    r.s.mode = 4
                else:
                    r.init(level)
            elif mode == 4:
                r.s.mode = 0
            r.s.action = a
    m.until("FRAME_READY", budget=30_000_000)
    r.held = 0
    if pad:
        lib.pad(m.p, 0)
    else:
        lib.key(m.p, *keys[a], 0)
    while True:
        event = lib.until_either(m.p, m.sym["INPUT_DONE"], m.sym["FN_TICK"], 10_000_000)
        assert event
        if event == 1:
            break
        r.held = m.get("KEY_LAST")  # Input becomes visible at the matrix scan.
        r.tick()
        m.until("FRAME_READY")
        assert_state(m, r)
    assert_state(m, r)


def tick(m, r):
    m.until("FN_TICK")
    r.held = m.get("KEY_LAST")
    r.tick()
    m.until("FRAME_READY")
    assert_state(m, r)


def go(m, r, target, width, pad=False):
    while r.s.cursor // width > target // width:
        action(m, r, 1, pad)
    while r.s.cursor // width < target // width:
        action(m, r, 2, pad)
    while r.s.cursor % width > target % width:
        action(m, r, 3, pad)
    while r.s.cursor % width < target % width:
        action(m, r, 4, pad)


def solve_lights(board):
    # Independent GF(2) elimination; do not depend on the scramble recipe.
    rows = []
    for p in range(25):
        mask = 0
        for q in range(25):
            if p == q or abs(p % 5 - q % 5) + abs(p // 5 - q // 5) == 1:
                mask |= 1 << q
        rows.append(mask | (board[p] << 25))
    pivots = []
    row = 0
    for col in range(25):
        candidate = next((i for i in range(row, 25) if rows[i] >> col & 1), None)
        if candidate is None:
            continue
        rows[row], rows[candidate] = rows[candidate], rows[row]
        for i in range(25):
            if i != row and rows[i] >> col & 1:
                rows[i] ^= rows[row]
        pivots.append(col)
        row += 1
    assert all(v & ((1 << 25) - 1) or not (v >> 25) for v in rows)
    return [pivots[i] for i in range(row) if rows[i] >> 25 & 1]


if __name__ == "__main__":
    m, r = begin("lumen_cross")
    for p in solve_lights(r.b):
        go(m, r, p, 5)
        action(m, r, 5)
    assert r.s.mode == 2
    print(
        "PASS: compiler, keyboard input, Lights Out independent solution and complete-state match"
    )
