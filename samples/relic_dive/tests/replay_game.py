"""Fixed-input acceptance replay: full rendering, no state writes after start."""

import argparse
import hashlib
import json
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from machine import ROOT, Machine, lib


def replay(path):
    path = Path(path)
    plan = json.loads(path.read_text())
    m = Machine()
    assert (
        not lib.headless_search_enabled()
    ), "Rendering must execute in acceptance replay"
    m.resume()
    for _ in range(plan.get("idle_waits", 0)):
        m.until("IDLE")
    lib.reset_min_sp()
    max_floor = m.start(plan["difficulty"])
    initial_seed = m.word("G_SEED")
    mutation_baseline = lib.mutations()
    max_turn = 0
    for action in plan["inputs"]:
        before = m.get("G_FLOOR")
        cycles = m.action(action, pad=action not in (6, 11))
        if m.get("G_FLOOR") != before:
            max_floor = max(max_floor, cycles)
        elif m.get("G_MODE") in (1, 9):
            max_turn = max(max_turn, cycles)
    assert (
        lib.mutations() == mutation_baseline
    ), "Host modified state during acceptance replay"
    actual = {
        "mode": m.get("G_MODE"),
        "floor": m.get("G_FLOOR") + 1,
        "hp": m.get("G_HP"),
        "food": m.get("G_FOOD"),
        "turns": m.word("G_TURNS"),
    }
    assert actual["mode"] == 9, actual
    for name, value in actual.items():
        assert value == plan[name], (name, value, plan[name])
    assert m.read(0x300, len(m.code)) == m.code, "Game wrote into code"
    stack_used = 0x3FFF - lib.min_sp()
    assert stack_used <= 512, stack_used
    result = {
        **actual,
        "difficulty": plan["difficulty"],
        "initial_rng_seed": initial_seed,
        "input_count": len(plan["inputs"]),
        "host_state_writes": lib.mutations() - mutation_baseline,
        "full_rendering": True,
        "stack_used_bytes": stack_used,
        "max_turn_cycles": max_turn,
        "max_floor_cycles": max_floor,
        "max_turn_ms": round(max_turn / 894, 3),
        "max_floor_ms": round(max_floor / 894, 3),
        "binary_sha256": hashlib.sha256(m.code).hexdigest(),
    }
    m.close()
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("plans", nargs="*", type=Path)
    args = p.parse_args()
    paths = args.plans or sorted(Path(__file__).with_name("replays").glob("*.json"))
    assert paths, "No replay plans"
    started = time.monotonic()
    with ProcessPoolExecutor(
        max_workers=min(3, len(paths)), mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        results = list(pool.map(replay, paths))
    report = {
        "replays": results,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "workers": min(3, len(paths)),
        "physical_device": "not tested",
    }
    (ROOT / "build/replay-verification.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
