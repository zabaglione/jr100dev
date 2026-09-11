"""Floor-level beam search in disposable emulator instances, followed by real replay."""

import contextlib
import hashlib
import io
import json

from machine import ROOT, SYMS, Machine, lib
from play_game import Player, effect


def score(p):
    m = p.m
    bag = m.read("G_BAG", 6)
    ident = m.read("G_IDENTITIES", 8)
    return (
        m.get("G_HP") * 3
        + m.get("G_FOOD") * 0.35
        + m.get("G_DEFENSE") * 15
        + m.get("G_ATTACK") * 12
        + bag.count(1) * 18
        + bag.count(22) * 100
        + sum((20 - v) * 8 for v in bag if 17 <= v <= 19)
        + sum(effect(ident, v) in (0, 5, 6) for v in bag) * 15
        - m.word("G_TURNS") * 0.015
    )


def search(wait=0, width=4, difficulty=2):
    lib.headless_search(SYMS["RENDER_SCREEN"], SYMS["G_MODE"])
    root = Player(difficulty, wait=wait)
    beam = [(score(root), lib.snapshot(root.m.p), [], root.max_turn, root.max_floor)]
    root.m.close()
    for floor in range((5, 10, 20)[difficulty]):
        candidates = []
        for _, state, actions, ma, mf, *_ in beam:
            for policy in range(8):
                p = Player.__new__(Player)
                p.m = Machine()
                lib.restore(p.m.p, state)
                p.actions = list(actions)
                p.max_turn = ma
                p.max_floor = mf
                p.difficulty = difficulty
                p.wait = wait
                p.policy = policy
                p.route_cache = None
                with contextlib.redirect_stdout(io.StringIO()):
                    r = p.run(limit=600, stop_floor=floor + 1, save=False)
                if r["mode"] == 9:
                    p.m.close()
                    (ROOT / "build" / f"replay-{difficulty}-{wait}.json").write_text(
                        json.dumps(r, indent=2) + "\n"
                    )
                    print(
                        "Clear plan found",
                        {k: v for k, v in r.items() if k != "inputs"},
                        flush=True,
                    )
                    return r
                if r["mode"] == 1 and r["floor"] == floor + 2:
                    candidates.append(
                        (
                            score(p),
                            lib.snapshot(p.m.p),
                            p.actions,
                            p.max_turn,
                            p.max_floor,
                            hashlib.sha256(
                                p.m.read(0x3300, 64)
                                + p.m.read(SYMS["FLOORS"], SYMS["FLOOR_DATA_END"])
                            ).digest(),
                        )
                    )
                p.m.close()
            lib.snapshot_free(state)
        candidates.sort(key=lambda x: x[0], reverse=True)
        # Keep distinct resulting states, even when policies happen to agree.
        distinct = []
        seen = set()
        for c in candidates:
            key = c[5]
            if key not in seen and len(distinct) < width:
                distinct.append(c)
                seen.add(key)
            else:
                lib.snapshot_free(c[1])
        beam = distinct
        print(
            f"seed_wait={wait} search floor={floor+1} survivors={len(beam)} scores={[round(c[0],1) for c in beam]}",
            flush=True,
        )
        if not beam:
            return None
    return None


def worker(wait):
    return search(wait=wait, width=6)


if __name__ == "__main__":
    import multiprocessing
    import sys
    from concurrent.futures import ProcessPoolExecutor

    waits = list(map(int, sys.argv[1:])) or [148, 444, 703, 1073]
    with ProcessPoolExecutor(
        max_workers=min(4, len(waits)), mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        results = list(pool.map(worker, waits))
    print(
        "Fixed-seed parallel search completed",
        sum(r is not None for r in results),
        "/",
        len(results),
    )
