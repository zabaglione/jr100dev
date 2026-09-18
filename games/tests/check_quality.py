"""Independent puzzle invariants and bounds at every intermediate drawing phase."""

import itertools
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "native"))
from checks import Model, render_bounds


def check():
    decks = set()
    for seed in range(64):
        r = Model("memory_mosaic")
        r.entropy = lambda seed=seed: seed
        r.init()
        assert Counter(r.b[:16]) == Counter({i: 2 for i in range(8)})
        decks.add(bytes(r.b[:16]))
    assert len(decks) >= 50, len(decks)

    tables = set()
    r = Model("circuit_works")
    for level in range(r.metadata["levels"]):
        r.init(level)
        table = tuple(r.d[:8])
        assert table not in tables
        tables.add(table)

        def gate(a, b, choice):
            return (a & b, a | b, a ^ b)[choice]

        assert any(
            all(
                gate(gate(gate(i >> 2, i >> 1 & 1, a), i & 1, b), i >> 2, c) == table[i]
                for i in range(8)
            )
            for a, b, c in itertools.product(range(3), repeat=3)
        )
    assert len(tables) == 22

    r = Model("ruin_lexicon")
    clues = set()
    for level in range(20):
        r.init(level)
        sums = tuple(r.d[i] + r.d[i + 1] for i in range(3))
        relation = r.d[0] < r.d[3]
        answers = [
            p
            for p in itertools.permutations(range(1, 5))
            if tuple(p[i] + p[i + 1] for i in range(3)) == sums
            and (p[0] < p[3]) == relation
        ]
        assert len(answers) == 1
        clues.add((sums, relation))
    assert len(clues) == 20

    r = Model("shadow_archive")
    cases = set()
    traits = set()
    for level in range(12):
        r.init(level)
        assert set(r.b[:6]) == set(range(1, 7))
        cases.add((bytes(r.b[:6]), r.s.culprit))
        traits.add(r.b[r.s.culprit])
    assert len(cases) == 12 and len(traits) == 6

    from check_second_review import auction_house

    auction_house()

    from check_star_lance import constraints

    constraints()

    review = json.loads((ROOT / "quality/review.json").read_text())
    phases = 0
    for item in review["remaining"]:
        name = item["directory"]
        if not (ROOT / name / "rules.py").exists():
            continue
        r = Model(name)

        def frame(*unused, model=r):
            nonlocal phases
            render_bounds(model)
            phases += 1

        r.env["animate"] = frame
        r.env["hold"] = frame
        r.env["glide"] = frame
        rng = random.Random(name)
        for event in range(100):
            if r.s.mode != 1:
                r.init(event % r.metadata["levels"])
            if r.metadata.get("rate", 255) < 255 and event % 2:
                r.tick()
            else:
                r.action(rng.choice((1, 2, 3, 4, 5, 5)))
            render_bounds(r)
    assert phases > 500
    print(
        f"PASS: 64 shuffled decks, 22 truth tables, 20 unique deductions, auction choices, armour and {phases} intermediate frames"
    )


if __name__ == "__main__":
    check()
