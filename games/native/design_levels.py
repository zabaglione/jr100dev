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


def create_gravity(rng):
    while True:
        b = walls(rng, 7)
        free = [i for i in range(64) if b[i] == 0]
        start = tuple(sorted(rng.sample(free, 2)))
        q = deque([start])
        paths = {start: []}
        while q:
            state = q.popleft()
            for a in range(1, 5):
                n = gravity_move(b, state, a)
                if n not in paths:
                    paths[n] = paths[state] + [a]
                    q.append(n)
        target, path = max(paths.items(), key=lambda v: len(v[1]))
        if 6 <= len(path) <= 20:
            board = b[:]
            for p in target:
                board[p] = 3
            return board + list(start), path


def create_iron(rng):
    while True:
        b = walls(rng, 9)
        route = search(
            9,
            lambda p, board=b: (
                (a, step(p, a)) for a in range(1, 5) if board[step(p, a)] != 1
            ),
            lambda p: p == 54,
        )
        if route and 10 <= len(route) <= 12:
            b[54] = 3
            return b, route


def frost_solution(data):
    b = [1 if v == 1 else 0 for v in data[:64]]
    gems = [i for i, v in enumerate(data[:64]) if v == 3]
    bits = {p: 1 << i for i, p in enumerate(gems)}

    def transitions(state):
        p, mask = state
        for a in range(1, 5):
            n = p
            m = mask
            for _ in range(7):
                q = step(n, a)
                if b[q]:
                    break
                n = q
                m |= bits.get(n, 0)
            yield a, (n, m)

    return search((9, 0), transitions, lambda st: st[1] == (1 << len(gems)) - 1)


def create_frost(rng):
    while True:
        b = walls(rng, 7)
        reachable = {9}
        todo = [9]
        for p in todo:
            for a in range(1, 5):
                n = p
                for _ in range(7):
                    q = step(n, a)
                    if b[q]:
                        break
                    n = q
                if n not in reachable:
                    reachable.add(n)
                    todo.append(n)
        if len(reachable) < 10:
            continue
        for p in rng.sample(sorted(reachable - {9}), 6):
            b[p] = 3
        route = frost_solution(b)
        if route and 7 <= len(route) <= 40:
            return b, route


def magnet_solution(data):
    board = data[:64]
    start = (27, 4, tuple(data[64:66]))
    goals = tuple(i for i, v in enumerate(board) if v == 3)

    def transitions(st):
        pos, facing, boxes = st
        for a in range(1, 5):
            p = step(pos, a)
            if board[p] == 1 or p in boxes:
                p = pos
            yield a, (p, a, boxes)
        front = step(pos, facing)
        behind = step(pos, {1: 2, 2: 1, 3: 4, 4: 3}[facing])
        if front in boxes and behind not in boxes and board[behind] != 1:
            yield 5, (behind, facing, tuple(sorted((set(boxes) - {front}) | {pos})))

    return search(start, transitions, lambda st: tuple(sorted(st[2])) == goals)


def create_magnet(rng):
    while True:
        b = walls(rng, 0)
        allowed = [
            19,
            20,
            21,
            22,
            17,
            18,
            41,
            42,
            43,
            44,
            45,
            46,
            27,
            49,
            50,
            51,
            52,
            53,
            54,
        ]
        for i in rng.sample([i for i in range(64) if not b[i] and i not in allowed], 5):
            b[i] = 1
        b[18] = 3
        b[42] = 3
        data = b + [21, 45]
        path = magnet_solution(data)
        if path and 20 <= len(path) < 75:
            return data, path


def glyph_solution(data):
    def transitions(st):
        p, phase = st
        for a in range(1, 5):
            q = step(p, a)
            if (
                data[q] != 1
                and not (data[q] == 4 and phase == 0)
                and not (data[q] == 5 and phase == 1)
            ):
                yield a, (q, phase)
        yield 5, (p, phase ^ 1)

    return search((9, 0), transitions, lambda st: st[0] == 54)


def create_glyph(rng):
    while True:
        b = walls(rng, 4)
        for p in range(64):
            if not b[p] and p not in (9, 54):
                b[p] = rng.choice([0, 4, 5, 4, 5])
        b[54] = 3
        path = glyph_solution(b)
        if path and 3 <= path.count(5) < 10:
            return b, path


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
        ("iron_script", create_iron, 20),
        ("gravity_well", create_gravity, 10),
        ("frost_steps", create_frost, 10),
        ("magnet_vault", create_magnet, 10),
        ("glyph_shift", create_glyph, 10),
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
