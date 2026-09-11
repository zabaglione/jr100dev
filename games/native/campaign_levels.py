"""Author 40 ranked chambers per puzzle; solve clears and rune routes with BFS.

Stored boards are expanded for editing. The build packs two cells per byte.
The solver models automatic completion: a route cannot continue after clearing.
"""

import argparse
import json
import random
from collections import deque
from functools import lru_cache
from pathlib import Path

from design_levels import gravity_move, step, walls

ROOT = Path(__file__).resolve().parents[1]
GAMES = ("frost_steps", "glyph_shift", "gravity_well", "magnet_vault")
OPPOSITE = {1: 2, 2: 1, 3: 4, 4: 3}
# Expanded record: board[64], start, box/ball 1, box 2, rune 1, rune 2, par.


def graph(name, data):
    board = data[:64]
    rune_bits = {data[67]: 1, data[68]: 2}
    gems = {p: 1 << i for i, p in enumerate(p for p, v in enumerate(board) if v == 3)}
    goals = tuple(gems)

    def visits(cells):
        mask = 0
        for p in cells:
            mask |= rune_bits.get(p, 0)
        return mask

    if name == "frost_steps":
        start = (data[64], 0)

        def goal(st):
            return st[1] == (1 << len(gems)) - 1

        @lru_cache(None)
        def edges(st):
            pos, collected = st
            result = []
            for a in range(1, 5):
                p, mask, cells = pos, collected, []
                for _ in range(7):
                    n = step(p, a)
                    if n == p or board[n] == 1:
                        break
                    p = n
                    cells.append(p)
                    mask |= gems.get(p, 0)
                if p != pos:
                    result.append((a, (p, mask), visits(cells)))
            return result

    elif name == "glyph_shift":
        start = (data[64], 0)

        def goal(st):
            return board[st[0]] == 3

        @lru_cache(None)
        def edges(st):
            p, phase = st
            result = [(5, (p, phase ^ 1), 0)]
            for a in range(1, 5):
                n = step(p, a)
                if n != p and board[n] != 1 and board[n] != (4 if phase == 0 else 5):
                    result.append((a, (n, phase), visits([n])))
            return result

    elif name == "gravity_well":
        start = tuple(sorted(data[64:66]))

        def goal(st):
            return st == goals

        @lru_cache(None)
        def edges(st):
            result = []
            for a in range(1, 5):
                occupied, cells = set(st), set()
                for _ in range(6):
                    for p in sorted(occupied, reverse=a in (2, 4)):
                        n = step(p, a)
                        if board[n] != 1 and n not in occupied:
                            occupied.remove(p)
                            occupied.add(n)
                            cells.add(n)
                n = tuple(sorted(occupied))
                if n != st:
                    result.append((a, n, visits(cells)))
            return result

    else:
        start = (data[64], 4, tuple(sorted(data[65:67])))

        def goal(st):
            return st[2] == goals

        @lru_cache(None)
        def edges(st):
            p, face, boxes = st
            result = []
            for a in range(1, 5):
                n = step(p, a)
                if board[n] == 1 or n in boxes:
                    n = p
                # Turning toward a blocked cell is useful for pulling and costs a move.
                if n != p or a != face:
                    result.append((a, (n, a, boxes), visits([n])))
            front, back = step(p, face), step(p, OPPOSITE[face])
            if front in boxes and back != p and back not in boxes and board[back] != 1:
                result.append(
                    (
                        5,
                        (back, face, tuple(sorted((set(boxes) - {front}) | {p}))),
                        visits([back]),
                    )
                )
            return result

    return start, edges, goal


def solve(name, data, limit=300000):
    start, edges, goal = graph(name, data)
    initial = (start, 0)
    q = deque([initial])
    back = {initial: None}
    clear = bonus = None

    def path(st):
        route = []
        while back[st] is not None:
            st, action = back[st]
            route.append(action)
        return route[::-1]

    while q and len(back) < limit:
        current = q.popleft()
        state, mask = current
        if goal(state):
            if clear is None:
                clear = path(current)
            if mask == 3:
                bonus = path(current)
                break
            continue
        for action, nxt, picked in edges(state):
            new = (nxt, mask | picked)
            if new not in back:
                back[new] = (current, action)
                q.append(new)
    return clear, bonus, len(back)


def candidate(name, rng, tier):
    board = walls(rng, rng.randrange(5, 12))
    free = [i for i, v in enumerate(board) if v == 0]
    start, first, second = rng.sample(free, 3)
    if name == "frost_steps":
        for p in rng.sample([i for i in free if i != start], 2 + tier):
            board[p] = 3
    elif name == "glyph_shift":
        board[first] = 3
        for p in free:
            if board[p] == 0 and p != start:
                board[p] = rng.choice([0, 0, 4, 5] if tier == 0 else [0, 4, 5, 4, 5])
    elif name == "gravity_well":
        initial = tuple(sorted((start, first)))
        states, todo = {initial: 0}, deque([initial])
        while todo:
            st = todo.popleft()
            for a in range(1, 5):
                nxt = gravity_move(board, st, a)
                if nxt not in states:
                    states[nxt] = states[st] + 1
                    todo.append(nxt)
        options = [
            st
            for st, depth in states.items()
            if 2 + tier * 2 <= depth <= 5 + tier * 4 and not set(st) & set(initial)
        ]
        if not options:
            return None
        for p in rng.choice(options):
            board[p] = 3
    else:
        # Start from two sockets, then reverse legal pulls to obtain viable boxes.
        board = walls(rng, 5 + tier)
        free = [i for i, v in enumerate(board) if v == 0]
        goals = rng.sample(free, 2)
        boxes = set(goals)
        p = rng.choice([i for i in free if i not in boxes])
        for _ in range(12 + tier * (80 if tier >= 3 else 15)):
            choices = []
            for a in range(1, 5):
                n = step(p, a)
                if board[n] == 1:
                    continue
                if n in boxes:
                    beyond = step(n, a)
                    if board[beyond] != 1 and beyond not in boxes and beyond != n:
                        choices.append((n, (boxes - {n}) | {beyond}))
                else:
                    choices.append((n, boxes))
            if choices:
                p, boxes = rng.choice(choices)
        if boxes & set(goals):
            return None
        start, (first, second) = p, sorted(boxes)
        for g in goals:
            board[g] = 3
    available = [p for p in free if board[p] == 0 and p not in (start, first, second)]
    if len(available) < 2:
        return None
    runes = rng.sample(available, 2)
    return board + [start, first, second, *runes, 0]


def signature(data):
    # Reject rotations/reflections of the same terrain, even with relocated items.
    walls = [int(v == 1) for v in data[:64]]
    variants = []
    for _ in range(4):
        variants.append(tuple(walls))
        variants.append(tuple(walls[y * 8 + 7 - x] for y in range(8) for x in range(8)))
        walls = [walls[(7 - x) * 8 + y] for y in range(8) for x in range(8)]
    return min(variants)


def generate(name):
    rng = random.Random("ranked-jr100-2026-" + name)
    ranges = {
        "frost_steps": [(3, 6), (7, 10), (11, 14), (15, 19), (20, 30)],
        "glyph_shift": [(4, 10), (11, 16), (17, 22), (23, 30), (31, 50)],
        "gravity_well": [(3, 6), (7, 9), (10, 13), (14, 18), (19, 30)],
        "magnet_vault": [(5, 12), (13, 20), (21, 28), (29, 38), (39, 65)],
    }[name]
    records, proofs, seen = [], [], set()
    for tier, (lo, hi) in enumerate(ranges):
        batch = []
        attempts = 0
        while len(batch) < 8:
            attempts += 1
            if attempts > 100000:
                raise RuntimeError((name, tier, "insufficient chambers", len(batch)))
            data = candidate(name, rng, tier)
            if data is None or signature(data) in seen:
                continue
            clear, bonus, explored = solve(name, data)
            # Every rune pair offers a real detour; clearing without it remains possible.
            if (
                not clear
                or not bonus
                or not lo <= len(bonus) <= hi
                or len(clear) >= len(bonus)
            ):
                continue
            if tier >= 3 and len(clear) < lo // 2:
                continue
            data[69] = len(bonus)
            seen.add(signature(data))
            batch.append(
                (
                    data,
                    {
                        "clear": clear,
                        "bonus": bonus,
                        "explored": explored,
                        "tier": tier + 1,
                    },
                )
            )
        batch.sort(key=lambda item: (len(item[1]["bonus"]), len(item[1]["clear"])))
        for data, proof in batch:
            records.append(data)
            proofs.append(proof)
        print(
            name,
            "tier",
            tier + 1,
            "pars",
            [len(p[1]["bonus"]) for p in batch],
            "attempts",
            attempts,
            flush=True,
        )
    root = ROOT / name
    (root / "levels.json").write_text(json.dumps(records, indent=2) + "\n")
    (root / "solutions.json").write_text(
        json.dumps([p["bonus"] for p in proofs], indent=2) + "\n"
    )
    (root / "challenges.json").write_text(json.dumps(proofs, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game", choices=GAMES)
    generate(parser.parse_args().game)
