"""Input-only campaigns and adaptive play-throughs for the compact native games."""

import argparse
import itertools
import json
from collections import Counter, deque
from pathlib import Path

from checks import ROOT, Model, action, assert_state, begin, lib, solve_lights, tick
from design_levels import search, step


class Player:
    def __init__(self, name, rom=None, capture=False, pad=True):
        self.name = name
        self.pad = pad
        self.capture = capture
        self.actions = 0
        self.ticks = 0
        self.m, self.r = begin(name, rom)
        self.directory = ROOT / name
        if capture:
            assert rom, "Screenshots require the owned BASIC ROM"
            (self.directory / "images").mkdir(exist_ok=True)
            (self.directory / "art").mkdir(exist_ok=True)
            # A separate real-BASIC boot preserves the untouched title frame.
            from machine import Machine

            title = Machine(name, rom=rom)
            title.capture(self.directory / "images/title.png")
            title.export_workbench(self.directory / "art/title.pcg.json")
            self.m.capture(self.directory / "images/play-01.png")
            self.m.export_workbench(self.directory / "art/play.pcg.json")

    @property
    def s(self):
        return self.r.s

    def press(self, a):
        assert self.s.mode == 1, (self.name, self.s.mode, a)
        action(self.m, self.r, a, self.pad)
        self.actions += 1
        if self.capture and self.actions == (
            6 if self.m.metadata.get("levels", 10) == 1 else 30
        ):
            self.m.capture(self.directory / "images/play-02.png")

    def wait(self):
        assert self.s.mode == 1
        tick(self.m, self.r)
        self.ticks += 1
        if self.capture and self.ticks == 30:
            self.m.capture(self.directory / "images/play-02.png")
        if self.capture and self.name == "brick_pulse":
            if (
                self.s.item
                and self.s.iy >= 9
                and abs(self.s.iy - self.s.y) > 1
                and not getattr(self, "item_captured", False)
            ):
                self.m.capture(self.directory / "images/items.png")
                self.item_captured = True
            if (
                self.s.level >= 5
                and self.s.bomb
                and not getattr(self, "drone_captured", False)
            ):
                self.m.capture(self.directory / "images/drone.png")
                self.drone_captured = True
        assert self.ticks < (24000 if self.name == "brick_pulse" else 6000), (
            self.name,
            "tick limit",
        )

    def go(self, target, width):
        while self.s.cursor // width > target // width:
            self.press(1)
        while self.s.cursor // width < target // width:
            self.press(2)
        while self.s.cursor % width > target % width:
            self.press(3)
        while self.s.cursor % width < target % width:
            self.press(4)

    def choice(self, field, target, action_code=4, cap=20):
        for _ in range(cap):
            if getattr(self.s, field) == target:
                return
            self.press(action_code)
        raise AssertionError((self.name, field, target))

    def next(self):
        assert self.s.mode == 2, (self.name, "did not clear", self.s.__dict__)
        if self.m.metadata.get("rankedCampaign"):
            assert self.s.stars == 3 and self.s.runes == 3
            assert self.s.moves == self.s.par
            assert self.m.read("BEST", self.s.level + 1) == bytes(
                [3] * (self.s.level + 1)
            )
            if self.capture and self.s.level == 0:
                self.m.capture(self.directory / "images/three-stars.png")
        last = self.s.level + 1 == self.m.metadata.get("levels", 10)
        self.m.action(5, pad=self.pad)
        if last:
            self.s.mode = 4
            self.s.action = 5
        else:
            self.r.init(self.s.level + 1)
            self.s.action = 5
        assert_state(self.m, self.r)
        if (
            self.capture
            and self.m.metadata.get("rankedCampaign")
            and self.s.level == 39
            and not last
        ):
            self.m.capture(self.directory / "images/play-02.png")
        return not last

    def finish(self):
        assert self.s.mode == 4
        if self.capture:
            self.m.capture(self.directory / "images/ending.png")
            if not (self.directory / "images/play-02.png").exists():
                # Keep the final solved layout as a second representative scene.
                self.m.capture(self.directory / "images/play-02.png")
            if self.m.metadata.get("rankedCampaign"):
                action(self.m, self.r, 8, confirm=True)
                self.m.capture(self.directory / "images/stage-select.png")
        assert lib.audio_peak(self.m.p) > 0, "No PCM produced"
        print(
            f"PASS: {self.name}, {self.actions} inputs, {self.ticks} clock steps, full campaign, min SP {lib.min_sp(self.m.p):04X}",
            flush=True,
        )


def feedback(guess, code):
    exact = sum(a == b for a, b in zip(guess, code))
    common = sum((Counter(guess) & Counter(code)).values())
    return exact, common - exact


def walk_plan(player, path):
    for a in path:
        if player.s.mode != 1:
            break
        player.press(a)


def solve_stage(p):
    name = p.name
    s = p.s
    r = p.r
    solutions = p.directory / "solutions.json"
    if name in ("gravity_well", "frost_steps", "magnet_vault", "glyph_shift"):
        walk_plan(p, json.loads(solutions.read_text())[s.level])
        return
    if name == "iron_script":
        route = json.loads(solutions.read_text())[s.level]
        for i, a in enumerate(route):
            p.choice("cursor", i)
            while r.c[i] != a:
                p.press(1)
        p.press(5)
        while s.mode == 1 and s.running:
            p.wait()
        return
    if name == "phase_pairs":
        for a, b in json.loads(solutions.read_text())[s.level]:
            p.go(a, 4)
            p.press(5)
            p.go(b, 4)
            p.press(5)
        return
    if name == "lumen_cross":
        for i in solve_lights(r.b):
            p.go(i, 5)
            p.press(5)
        return
    if name == "memory_mosaic":
        memory = {}
        matched = set()
        while s.mode == 1:
            first = next(i for i in range(16) if i not in memory and i not in matched)
            p.go(first, 4)
            p.press(5)
            memory[first] = r.b[first]
            second = next(
                (
                    i
                    for i, v in memory.items()
                    if i != first and i not in matched and v == memory[first]
                ),
                None,
            )
            if second is None:
                second = next(
                    i for i in range(16) if i not in memory and i not in matched
                )
            p.go(second, 4)
            p.press(5)
            memory[second] = r.b[second]
            if memory[first] == memory[second]:
                matched.update((first, second))
            if s.mode == 1:
                p.press(5)
        return
    if name == "stone_balance":
        while s.mode == 1:
            choice = next(
                (
                    (i, n)
                    for i in range(3)
                    for n in (1, 2, 3)
                    if r.b[i] >= n
                    and not (
                        ((r.b[0] - n if i == 0 else r.b[0]) % 4)
                        ^ ((r.b[1] - n if i == 1 else r.b[1]) % 4)
                        ^ ((r.b[2] - n if i == 2 else r.b[2]) % 4)
                    )
                ),
                None,
            )
            assert choice, "Initial heap configuration is losing against perfect play"
            i, n = choice
            p.choice("pile", i, 2)
            p.choice("take", n, 3)
            p.press(5)
        return
    if name == "hearth_zero":
        for c in [3, 1, 2, 0, 3, 2, 1, 0]:
            p.choice("choice", c)
            p.press(5)
        assert (s.food, s.wood, s.heat, s.insulation) == (8, 8, 8, 2)
        return
    if name == "orchard_days":
        for i in range(8):
            p.go(i, 4)
            p.press(5)
        while s.mode == 1:
            i = next((i for i, v in enumerate(r.b[:16]) if v == 4), None)
            if i is None:
                i = max((i for i in range(16) if r.b[i]), key=lambda j: r.b[j])
            p.go(i, 4)
            p.press(5)
        return
    if name == "cargo_balance":
        while s.mode == 1:

            def score(i):
                left = s.left + (s.weight * (3 if i == 0 else 1) if i < 2 else 0)
                right = s.right + (s.weight * (3 if i == 3 else 1) if i >= 2 else 0)
                return abs(left - right)

            target = min((i for i in range(4) if r.c[i] < 4), key=score)
            p.choice("cursor", target)
            p.press(5)
        return
    if name == "tidal_nets":
        while s.mode == 1:
            p.choice("cursor", (s.fish + s.tide) % 8)
            p.press(5)
        return
    if name == "auction_house":
        for _ in range(100):
            if s.mode != 1:
                return
            p.press(5)
        raise AssertionError("Auction did not finish")
    if name == "potion_path":
        start = (s.x, s.y)
        target = (s.tx, s.ty)

        def transitions(st):
            x, y = st
            for i, (dx, dy) in enumerate(((-2, 0), (1, 2), (0, -1), (3, 1))):
                if 0 <= x + dx < 8 and 0 <= y + dy < 8:
                    yield i, (x + dx, y + dy)

        route = search(start, transitions, lambda st: st == target)
        assert route is not None and len(route) <= 12
        # Initial positions that already satisfy an order should not be generated.
        assert route
        for i in route:
            p.choice("ingredient", i)
            p.press(5)
        return
    if name == "number_vault":
        candidates = list(itertools.product(range(1, 5), repeat=4))
        guess = (1, 1, 2, 2)
        while s.mode == 1:
            for i, v in enumerate(guess):
                p.choice("cursor", i)
                while r.b[i] != v:
                    p.press(1)
            p.press(5)
            if s.mode != 1:
                break
            observed = (s.exact, s.near)
            candidates = [c for c in candidates if feedback(guess, c) == observed]
            assert candidates
            # Minimax among remaining candidates is independent of the secret.
            guess = min(
                candidates,
                key=lambda g: max(Counter(feedback(g, c) for c in candidates).values()),
            )
        return
    if name == "fuse_box":
        # Construct one valid matrix from the displayed row/column totals.
        rows = [sum(r.d[i * 5 : i * 5 + 5]) for i in range(5)]
        cols = [sum(r.d[i + 5 * j] for j in range(5)) for i in range(5)]

        def arrange(row, left, placed):
            if row == 5:
                return placed if not any(left) else None
            for selected in itertools.combinations(range(5), rows[row]):
                if all(left[i] > 0 for i in selected):
                    new = left[:]
                    for i in selected:
                        new[i] -= 1
                    result = arrange(
                        row + 1, new, placed + [row * 5 + i for i in selected]
                    )
                    if result is not None:
                        return result
            return None

        result = arrange(0, cols, [])
        assert result
        for i in result:
            p.go(i, 5)
            p.press(5)
        return
    if name == "circuit_works":

        def gate(a, b, k):
            return (a & b, a | b, a ^ b)[k]

        gates = next(
            combo
            for combo in itertools.product(range(3), repeat=3)
            if all(
                gate(
                    gate(gate(i // 2, i % 2, combo[0]), i // 2, combo[1]),
                    i % 2,
                    combo[2],
                )
                == r.d[i]
                for i in range(4)
            )
        )
        for i, v in enumerate(gates):
            p.choice("cursor", i, 2)
            while r.c[i] != v:
                p.press(4)
        p.press(5)
        return
    if name == "orbit_draft":
        # Place the three equal cards in separate complete rows.
        counts = [0] * 3
        while s.mode == 1:
            i = s.card
            target = i * 3 + counts[i]
            counts[i] += 1
            p.go(target, 3)
            p.press(5)
        return
    if name in ("twenty_one", "chain_suit"):
        return solve_cards(p)
    if name == "compass_rose":
        while s.pos != s.target:
            a = (
                1
                if s.target // 8 < s.pos // 8
                else (
                    2
                    if s.target // 8 > s.pos // 8
                    else (3 if s.target % 8 < s.pos % 8 else 4)
                )
            )
            p.press(a)
        p.press(5)
        return
    if name == "ruin_lexicon":
        known = [r.d[0]]
        for i in range(3):
            known.append(r.d[i] + r.d[i + 1] - known[-1])
        for i, v in enumerate(known):
            p.choice("cursor", i)
            while r.b[i] != v:
                p.press(1)
        p.press(5)
        return
    if name == "shadow_archive":
        p.press(5)
        p.press(4)
        p.press(5)
        answer = (s.culprit // 3) * 3 + s.culprit % 3
        p.choice("choice", answer)
        p.press(2)
        p.press(5)
        return
    if name == "word_foundry":
        words = [bytes(r.env["words"][i * 3 : i * 3 + 3]) for i in range(16)]
        path = search(
            s.word,
            lambda i: (
                (j, j)
                for j in range(16)
                if sum(a != b for a, b in zip(words[i], words[j])) == 1
            ),
            lambda i: i == s.goal,
        )
        assert path is not None and len(path) <= 8
        for i in path:
            p.go(i, 4)
            p.press(5)
        return
    if name == "prism_trace":
        for i in (23, 37, 40, 12, 1):
            if s.mode != 1:
                break
            p.go(i, 7)
            p.press(5)
        return
    if name in ("quiet_route", "mirror_relic", "tide_bridge", "peg_garden"):
        return solve_search(p)
    if name in ("five_forge", "corner_crown"):
        return solve_board_match(p)
    if name == "seed_merge":
        return solve_merge(p)
    return solve_realtime(p)


def snapshot(r):
    return (r.s.__dict__.copy(), bytes(r.b), bytes(r.c), bytes(r.d))


def restore(r, state):
    r.s.__dict__.clear()
    r.s.__dict__.update(state[0])
    r.b[:] = state[1]
    r.c[:] = state[2]
    r.d[:] = state[3]


def solve_cards(p):
    # Exhaust the bounded decision tree offline, then replay only legal keys.
    sim = Model(p.name)
    restore(sim, snapshot(p.r))
    failed = set()

    def visit(depth):
        if sim.s.mode != 1:
            return [] if sim.s.mode == 2 else None
        if depth > 25:
            return None
        state = snapshot(sim)
        key = (tuple(sorted(state[0].items())), state[1], state[2])
        if key in failed:
            return None
        options = (
            [("stand", 0), ("stand", 1)]
            if p.name == "twenty_one"
            else [("score", 0)]
            + ([("draw", i) for i in range(5)] if sim.s.discards else [])
        )
        for kind, i in options:
            restore(sim, state)
            if kind == "stand":
                sim.s.choice = i
                sim.action(5)
            elif kind == "score":
                sim.action(5)
            else:
                sim.s.cursor = i
                sim.action(1)
            tail = visit(depth + 1)
            if tail is not None:
                return [(kind, i)] + tail
        restore(sim, state)
        failed.add(key)
        return None

    path = visit(0)
    assert path is not None, (p.name, "No winning decision tree")
    for kind, i in path:
        if kind == "stand":
            p.choice("choice", i)
            p.press(5)
        elif kind == "score":
            p.press(5)
        else:
            p.choice("cursor", i)
            p.press(1)


def solve_search(p):
    name = p.name
    if name == "mirror_relic":
        jewels = [i for i in range(64) if p.r.c[i]]
        bits = {v: 1 << i for i, v in enumerate(jewels)}

        def transitions(st):
            pos, mask = st
            for a in range(1, 6):
                n = step(pos, a) if a < 5 else pos % 8 * 8 + 7 - pos // 8
                if p.r.b[n] != 1:
                    yield a, (n, mask | bits.get(n, 0))

        path = search((p.s.pos, 0), transitions, lambda st: st == (53, 7))
        assert path
        walk_plan(p, path)
        return
    if name == "quiet_route":
        sim = Model(name)
        q = deque([(snapshot(sim), [])])
        seen = set()
        while q:
            state, path = q.popleft()
            restore(sim, state)
            key = (sim.s.pos, sim.s.guard, sim.s.direction, sim.s.quiet, sim.s.key)
            if key in seen:
                continue
            seen.add(key)
            if sim.s.mode == 2:
                walk_plan(p, path)
                return
            if sim.s.mode != 1:
                continue
            for a in range(1, 6):
                restore(sim, state)
                sim.action(a)
                q.append((snapshot(sim), path + [a]))
        raise AssertionError("Stealth exit is unreachable")
    if name == "tide_bridge":
        original = tuple(bool(v) for v in p.r.b[:36])

        def connected(mask):
            board = [
                original[i] ^ bool(mask >> (i // 6) & 1) ^ bool(mask >> (6 + i % 6) & 1)
                for i in range(36)
            ]
            seen = {30}
            todo = [30]
            for i in todo:
                for a in range(1, 5):
                    n = step(i, a, 6, 6)
                    if n not in seen and (board[n] or n == 5):
                        seen.add(n)
                        todo.append(n)
            return 5 in seen

        mask = min((m for m in range(4096) if connected(m)), key=int.bit_count)
        for i in range(12):
            if mask >> i & 1:
                if p.s.axis != i // 6:
                    p.press(4)
                p.choice("cursor", i % 6, 2)
                p.press(5)
                if p.s.mode != 1:
                    return
        return
    if name == "peg_garden":
        valid = {i for i in range(25) if p.r.b[i] != 1}
        moves = []
        for i in valid:
            for a in range(1, 5):
                mid = step(i, a, 5, 5)
                end = step(mid, a, 5, 5)
                if mid != i and end != mid and mid in valid and end in valid:
                    moves.append((i, mid, end))
        initial = sum(1 << i for i in valid if p.r.b[i] == 4)
        dead = set()

        def dfs(mask):
            if mask.bit_count() <= 5:
                return []
            if mask in dead:
                return None
            for a, b, c in moves:
                if mask >> a & 1 and mask >> b & 1 and not (mask >> c & 1):
                    result = dfs(mask ^ (1 << a) ^ (1 << b) ^ (1 << c))
                    if result is not None:
                        return [(a, c)] + result
            dead.add(mask)
            return None

        route = dfs(initial)
        assert route
        for a, c in route:
            p.go(a, 5)
            p.press(5)
            p.go(c, 5)
            p.press(5)


def solve_realtime(p):
    s = p.s
    r = p.r
    name = p.name
    snake_cycle = []
    if name == "ribbon_snake":
        snake_cycle = [i * 8 for i in range(8)]
        for x in range(1, 8):
            snake_cycle += [
                y * 8 + x for y in (range(7, 0, -1) if x % 2 else range(1, 8))
            ]
        snake_cycle += list(range(7, 0, -1))
        assert len(set(snake_cycle)) == 64
    while s.mode == 1:
        if name == "orbit_dodge":
            if s.pos == s.target:
                p.press(3)
        elif name == "gate_runner":
            if s.kind == 1 and s.lane == s.obstacle and s.age == 4:
                p.press(5)
            elif s.kind == 0 and s.lane == s.obstacle:
                p.press(3 if s.lane else 4)
        elif name == "echo_parry":
            if s.stance != s.attack:
                p.press(1 if s.attack == 0 else 2)
            if s.phase == 1 and not s.guarded:
                p.press(5)
        elif name == "pendulum_port":
            if abs(s.swing - s.target) <= 1:
                p.press(5)
        elif name == "lunar_touchdown":
            if s.x < s.target + 1:
                p.press(4)
            elif s.x > s.target + 1:
                p.press(3)
            if s.speed >= 2:
                p.press(5)
        elif name == "night_swarm":
            if s.cooldown == 0 and any(
                v != 255 and abs(v % 8 - s.pos % 8) + abs(v // 8 - s.pos // 8) <= 3
                for v in r.b[:8]
            ):
                p.press(5)
        elif name == "metro_weave":
            desired = [0, 0] if s.dest == 0 else [1, 0 if s.dest == 1 else 1]
            if s.age < 3:
                for i, v in enumerate(desired):
                    if r.c[i] != v:
                        if s.cursor != i:
                            p.press(2)
                        p.press(5)
        elif name == "sand_rescue":
            desired = (s.released // 4) % 3
            oldgate = next((i for i in range(3) if r.b[26 + i * 2] == 0), None)
            if oldgate is None or (
                oldgate != desired
                and not r.c[10 + oldgate * 2]
                and not r.c[18 + oldgate * 2]
            ):
                p.choice("gate", desired)
                p.press(5)
        elif name == "star_lance":
            if s.cool == 0:
                enemy = next((i for i in range(23, -1, -1) if r.b[i]), None)
                if enemy is not None:
                    target = (enemy % 8 + s.shift) % 8
                    if s.ship != target:
                        p.press(4 if (target - s.ship) % 8 <= 4 else 3)
                    else:
                        p.press(5)
            if s.mode == 1 and s.bullet >= 6 and s.bullet != 255 and s.ship == s.bx:
                p.press(4)
        elif name == "ribbon_snake":
            current = r.b[0]
            target = snake_cycle[(snake_cycle.index(current) + 1) % 64]
            desired = next(a for a in range(1, 5) if step(current, a) == target)
            if s.dir != desired:
                p.press(desired)
        elif name == "brick_pulse":
            from sys import path

            if str(p.directory) not in path:
                path.insert(0, str(p.directory))
            from ai import target as paddle_target

            # Replan after every rebound, damage, power-up or changed brick.
            key = (s.bounces, s.hp, s.enemy, sum(r.b), s.width, s.caught)
            if getattr(p, "brick_key", None) != key:
                p.brick_key = key
                p.brick_target = paddle_target(r)
            target = p.brick_target
            if s.paddle + 1 < target:
                p.press(4)
            elif s.paddle > target + 1:
                p.press(3)
        else:
            raise ValueError(name)
        if s.mode == 1:
            p.wait()


def solve_merge(p):
    sim = Model("seed_merge")

    def rating():
        empty = sum(v == 0 for v in sim.b[:16])
        total = sum(2**v for v in sim.b[:16])
        maximum = max(sim.b[:16])
        corner = max(sim.b[i] for i in (0, 3, 12, 15))
        smooth = sum(
            abs(sim.b[i] - sim.b[j])
            for i in range(16)
            for j in (step(i, 2, 4, 4), step(i, 4, 4, 4))
        )
        return empty * 80 + corner * 20 + total - smooth * 3 + maximum * 20

    while p.s.mode == 1:
        start = snapshot(p.r)
        best = None
        for seq in itertools.product(range(1, 5), repeat=3):
            restore(sim, start)
            valid = True
            for a in seq:
                before = bytes(sim.b)
                sim.action(a)
                if sim.s.mode == 3:
                    valid = False
                    break
                if sim.s.mode == 2:
                    break
                if bytes(sim.b) == before:
                    valid = False
                    break
            if valid:
                score = 100000 if sim.s.mode == 2 else rating()
                if best is None or score > best[0]:
                    best = (score, seq[0])
        assert best, "No merge strategy found"
        p.press(best[1])
        assert p.actions < 1000


def solve_board_match(p):
    sim = Model(p.name)
    turns = 0
    import random

    rng = random.Random(0)
    while p.s.mode == 1:
        restore(sim, snapshot(p.r))
        best = None
        for i in range(64):
            if sim.b[i]:
                continue
            if p.name == "corner_crown":
                gain = sim.env["flips"](i, 1, 0)
                if not gain:
                    continue
                value = gain + (
                    80
                    if i in (0, 7, 56, 63)
                    else (8 if i // 8 in (0, 7) or i % 8 in (0, 7) else 0)
                )
                if i in (1, 6, 8, 9, 14, 15, 48, 49, 54, 55, 57, 62):
                    value -= 35
            else:
                offense = sim.env["line"](i, 1)
                defense = sim.env["line"](i, 2)
                value = offense * 6 + defense * 4 + rng.random() * 8
                if defense >= 5:
                    value = 1000 + rng.random()
                if offense >= 5:
                    value = 2000 + rng.random()
            if best is None or value > best[0]:
                best = (value, i)
        target = best[1] if best else p.s.cursor
        p.go(target, 8)
        p.press(5)
        turns += 1
        assert turns < 65


def replay(name, rom=None, capture=False, pad=True):
    p = Player(name, rom, capture, pad)
    while True:
        solve_stage(p)
        if not p.next():
            break
    p.finish()
    return {
        "actions": p.actions,
        "ticks": p.ticks,
        "min_sp": lib.min_sp(p.m.p),
        "levels": p.m.metadata.get("levels", 10),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game")
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", action="store_true")
    parser.add_argument("--keyboard", action="store_true")
    args = parser.parse_args()
    replay(
        args.game,
        args.rom.read_bytes() if args.rom else None,
        args.capture,
        not args.keyboard,
    )
