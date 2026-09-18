"""Deterministic original puzzle layouts, independently solved before writing."""

import json
import random
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def step(p, a, w=8, h=8):
    x, y = p % w, p // w
    dx, dy = {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}[a]
    x += dx
    y += dy
    return y * w + x if 0 <= x < w and 0 <= y < h else p


def walls(rng, count=7):
    b = [int(i < 8 or i >= 56 or i % 8 in (0, 7)) for i in range(64)]
    for i in rng.sample([i for i in range(64) if not b[i] and i not in (9, 54)], count):
        b[i] = 1
    return b


def search(start, transitions, goal, limit=200000):
    q = deque([start])
    back = {start: None}
    while q and len(back) < limit:
        state = q.popleft()
        if goal(state):
            path = []
            while back[state] is not None:
                old, action = back[state]
                path.append(action)
                state = old
            return path[::-1]
        for action, state2 in transitions(state):
            if state2 not in back:
                back[state2] = (state, action)
                q.append(state2)
    return None


def gravity_move(b, balls, action):
    occupied = set(balls)
    for _ in range(6):
        for p in sorted(occupied, reverse=action in (2, 4)):
            # Match a synchronous substep: each ball moves at most once per pass.
            n = step(p, action)
            if not b[n] and n not in occupied:
                occupied.remove(p)
                occupied.add(n)
    return tuple(sorted(occupied))


def create_pairs(rng):
    remaining = set(range(16))
    pairs = []

    def match(left):
        if not left:
            return []
        p = min(left)
        opts = [step(p, a, 4, 4) for a in range(1, 5)]
        rng.shuffle(opts)
        for q in opts:
            if q != p and q in left:
                rest = match(left - {p, q})
                if rest is not None:
                    return [(p, q)] + rest
        return None

    pairs = match(remaining)
    b = [0] * 16
    for p, q in pairs:
        b[p] = rng.randrange(1, 10)
        b[q] = 10 - b[p]
    return b, pairs


def main():
    rng = random.Random(1002026)
    for name, factory, count in [
        ("phase_pairs", create_pairs, 10),
    ]:
        boards = []
        solutions = []
        while len(boards) < count:
            board, path = factory(rng)
            if board in boards:
                continue
            boards.append(board)
            solutions.append(path)
        root = ROOT / name
        (root / "levels.json").write_text(json.dumps(boards, indent=2) + "\n")
        (root / "solutions.json").write_text(json.dumps(solutions, indent=2) + "\n")
        meta = json.loads((root / "game.json").read_text())
        meta["levels"] = count
        (root / "game.json").write_text(json.dumps(meta, indent=2) + "\n")
        print(name, count, "solved layouts", flush=True)


if __name__ == "__main__":
    main()
