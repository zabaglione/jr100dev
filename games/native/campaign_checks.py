"""Prove ranked chamber data, then exercise ratings and menus on the real CPU."""

import json
import sys
from collections import deque

from campaign_levels import graph, signature, solve
from checks import ROOT, Model, action, begin


def over_par_route(name, data, route, minimum=None):
    state, edges, goal = graph(name, data)
    for i, a in enumerate(route):
        q = deque([(state, [])])
        seen = {state}
        while q and len(seen) < 2000:
            current, path = q.popleft()
            for b, nxt, _ in edges(current):
                if goal(nxt):
                    continue
                if nxt == state:
                    cycle = path + [b]
                    return (
                        route[:i]
                        + cycle * ((minimum or data[69]) // len(cycle) + 1)
                        + route[i:]
                    )
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [b]))
        state = next(nxt for b, nxt, _ in edges(state) if b == a)
    raise AssertionError("No optional detour found")


def check(name):
    directory = ROOT / name
    levels = json.loads((directory / "levels.json").read_text())
    proofs = json.loads((directory / "challenges.json").read_text())
    assert len(levels) == len(proofs) == 40
    assert len({signature(data) for data in levels}) == 40
    for i, (data, proof) in enumerate(zip(levels, proofs)):
        clear, bonus, _ = solve(name, data)
        assert len(clear) == len(proof["clear"]) < len(bonus) == data[69]
        assert len(bonus) == len(proof["bonus"])
        assert len(data) == 70 and all(0 <= v <= 5 for v in data[:64])
        assert data[67] != data[68] and data[data[67]] == data[data[68]] == 0
        # Independent rule interpreter also consumes both solver routes.
        for route, expected in ((proof["clear"], 2), (proof["bonus"], 3)):
            model = Model(name)
            model.init(i)
            for a in route:
                assert model.s.mode == 1, "Route passes an already completed board"
                model.action(a)
            assert model.s.mode == 2 and model.s.stars == expected
    pars = [d[69] for d in levels]
    assert pars == sorted(pars) and pars[32] > pars[7]
    m, r = begin(name)

    def press(a, pad=False):
        action(m, r, a, pad, confirm=True)

    def route(sequence):
        for a in sequence:
            assert r.s.mode == 1
            press(a, pad=True)

    route(proofs[0]["clear"])
    assert r.s.stars == 2 and r.s.runes != 3 and r.best[0] == 2
    press(6)
    route(proofs[0]["bonus"])
    assert r.s.moves == r.s.par and r.s.stars == 3 and r.best[0] == 3
    press(6)
    route(over_par_route(name, levels[0], proofs[0]["bonus"]))
    assert r.s.moves > r.s.par and r.s.stars == 1 and r.best[0] == 3
    press(6)
    route(over_par_route(name, levels[0], proofs[0]["bonus"], minimum=260))
    assert r.s.moves == 255 and r.s.overflow == 1 and r.s.stars == 1
    # All three outcomes allow advancing. Retrying never lowers the best rating.
    press(5, pad=True)
    assert r.s.level == 1 and r.s.mode == 1
    press(8)
    assert r.s.mode == 6
    press(3, pad=True)
    press(3, pad=True)
    assert r.s.level == 39
    press(2, pad=True)
    assert r.s.level == 4
    press(1, pad=True)
    assert r.s.level == 39
    press(5, pad=True)
    assert r.s.par == levels[39][69]
    press(6)
    assert r.s.level == 39 and r.s.moves == 0 and r.best[0] == 3
    route(proofs[39]["bonus"])
    press(5)
    assert r.s.mode == 4
    press(5)
    assert r.s.mode == 0 and r.best[39] == 3
    press(5)
    assert r.s.level == 39 and r.s.mode == 1
    press(8)
    press(6)
    assert r.s.mode == 0 and r.best[0] == 3
    print(
        f"PASS: {name}, 40 distinct solved boards, all rune routes optimal, 1/2/3 stars, pad, retry, stage selection, record retention"
    )


if __name__ == "__main__":
    check(sys.argv[1])
