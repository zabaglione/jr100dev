"""Exercise invalid moves, timed hazards, retries and screen bounds through input."""

import random
import sys

from checks import Machine, Model, action, assert_state, lib, tick


def check(name):
    rng = random.Random(name)
    m = Machine(name)
    # The guide is reachable before a game and returns to an untouched title.
    m.action(6)
    assert m.get("MODE") == 5
    m.action(5)
    assert m.get("MODE") == 0
    m.action(5)
    r = Model(name, machine=m)
    r.s.action = 5
    assert_state(m, r)
    levels = m.metadata.get("levels", 10)
    directions = [1, 2, 3, 4] + (
        [9, 10, 11, 12] if m.metadata.get("directions") == 8 else []
    )
    for i in range(160):
        if r.s.mode != 1:
            if r.metadata.get("endless") and r.s.mode == 2:
                m.action(5)
                r.env["advance"]()
                r.s.action = 5
                assert_state(m, r)
                continue
            level = r.s.level + (1 if r.s.mode == 2 else 0)
            m.action(5)
            if m.get("CN_ACTIVE"):
                m.answer_reset(True)
            if level == levels:
                assert m.get("MODE") == 4
                m.action(5)
                assert m.get("MODE") == 0
                m.action(5)
                level = 0
            r.init(level)
            r.s.action = 5
            assert_state(m, r)
        if i % 31 == 30 and not m.metadata.get("disableSpaceReset"):
            # No writes to game state: retry restores its authored initial data.
            level = r.s.level
            action(m, r, 6, confirm=True)
        elif m.metadata.get("rate", 255) < 255 and i % 3 == 0:
            tick(m, r)
        else:
            action(
                m, r, rng.choice(directions + [5, 5, 5]), pad=bool(i % 2), confirm=True
            )
    # A title melody must keep progressing without input and emit actual PCM.
    title = Machine(name)
    before = title.read("BGM_PTR", 2)
    lib.ticks(title.p, 900_000)
    assert title.read("BGM_PTR", 2) != before and lib.audio_peak(title.p) > 0
    print(
        f"PASS: {name}, 160 mixed keyboard/pad events, retries, screen bounds, title PCM"
    )


if __name__ == "__main__":
    check(sys.argv[1])
