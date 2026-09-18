"""Input-only campaigns and adaptive play-throughs for the compact native games."""

import argparse
import itertools
import json
import sys
from collections import Counter, deque
from pathlib import Path

from checks import ROOT, Model, action, assert_state, begin, lib, solve_lights, tick
from design_levels import search, step

sys.path.insert(0, str(ROOT))


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
        action(self.m, self.r, a, self.pad and a not in (7, 8))
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
        if (
            self.capture
            and self.name == "iron_script"
            and self.s.level == 23
            and self.s.steps == 8
        ):
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
        if self.m.metadata.get("endless"):
            self.m.action(5, pad=self.pad)
            self.r.env["advance"]()
            self.s.action = 5
            assert_state(self.m, self.r)
            return True
        if self.m.metadata.get("rankedCampaign"):
            assert self.s.stars == 3 and self.s.runes == 3
            assert self.s.moves == self.s.par
            assert self.m.read("BEST", self.s.level + 1) == bytes(
                [3] * (self.s.level + 1)
            )
            if self.capture and self.s.level == 0:
                self.m.capture(self.directory / "images/three-stars.png")
        last = self.s.level + 1 == self.m.metadata.get("levels", 10)
        if last and self.m.metadata.get("carryCampaign"):
            self.r.env["checkpoint"]()
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
        endless = self.m.metadata.get("endless")
        assert self.s.mode == (2 if endless else 4)
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
            f"PASS: {self.name}, {self.actions} inputs, {self.ticks} clock steps, "
            f"{'eight continuous rounds' if endless else 'full campaign'}, min SP {lib.min_sp(self.m.p):04X}",
            flush=True,
        )


def metro_dispatch(p, express=True):
    """Read the nearest approaching train; dispatch only after the yard clears."""
    r, s = p.r, p.s
    for junction, x, y in ((0, 8, 5), (1, 17, 10)):
        approaching = [
            i for i in range(3) if r.b[i] and r.b[3 + i] == y and x - 3 <= r.b[i] <= x
        ]
        if approaching:
            i = max(approaching, key=lambda i: r.b[i])
            setting = int(r.b[9 + i] != 0) if junction == 0 else int(r.b[9 + i] == 2)
            if r.c[junction] != setting:
                if s.cursor != junction:
                    p.press(2)
                p.press(4)
    # Reserve unloading time for visible trains bound for the same station.
    # Leave a few spare ticks rather than betting every express on its deadline.
    target = r.c[16]
    available = r.c[8 + target]
    for distance in sorted(
        26 - r.b[i] for i in range(3) if r.b[i] and r.b[9 + i] == target
    ):
        available = max(available, distance) + 12
    if (
        express
        and s.issued < 8
        and s.active < s.capacity
        and available <= 29
        and all(x == 0 or x >= 8 for x in r.b[:3])
    ):
        p.press(5)


def sand_plan(r, extra=0):
    """Compare the six visible crops: near only or near plus far on each route."""
    plans = []
    for choices in itertools.product(range(3), repeat=3):
        reward = sum(
            3 * (choice > 0) + r.b[i + 3] * 2 * (choice == 2)
            for i, choice in enumerate(choices)
        )
        cost = sum(
            r.b[i] * (choice > 0) + (r.b[i + 3] + r.b[i + 6]) * (choice == 2)
            for i, choice in enumerate(choices)
        )
        if reward >= r.s.quota + extra:
            plans.append((cost, -reward, choices))
    return min(plans)[2]


def sand_irrigate(p, extra=0):
    plan = sand_plan(p.r, extra)
    # Commit long pours first; water for a small near crop fills during travel.
    for gate in sorted(range(3), key=lambda i: -plan[i]):
        if plan[gate] == 0:
            continue
        needed = p.r.b[gate]
        if plan[gate] == 2:
            needed += p.r.b[gate + 3] + p.r.b[gate + 6]
        pours = [needed]
        if needed > 9:
            pours = [p.r.b[gate], needed - p.r.b[gate]]
        for amount in pours:
            p.choice("gate", gate)
            p.wait()  # Read the selected route before opening its gate.
            while p.s.tank < amount:
                p.wait()
            p.press(5)
            while p.s.flow:
                p.wait()
    for _ in range(3):
        p.wait()
    p.press(1)  # Bank this harvest; the player may choose to grow more instead.


def runner_steer(p):
    """Aim for the visible crystal, then jump just before the pit reaches us."""
    s, r = p.s, p.r
    target = r.b[6]
    if s.x != target:
        p.press(4 if s.x < target else 3)
        return
    remaining = (18 - s.age) * s.speed - s.pace
    if r.b[7] and s.air == 0 and remaining <= 5:
        p.press(5)


def feedback(guess, code):
    exact = sum(a == b for a, b in zip(guess, code))
    common = sum((Counter(guess) & Counter(code)).values())
    return exact, common - exact


def walk_plan(player, path):
    for a in path:
        if player.s.mode != 1:
            break
        player.press(a)


def fuse_plan(rows, cols):
    """Fill the largest rows using columns with the most switches still needed."""
    assert len(rows) == len(cols) == 5
    assert all(0 <= count <= 5 for count in (*rows, *cols))
    assert sum(rows) == sum(cols), "Inconsistent fuse totals"
    remaining = list(cols)
    plan = []
    cursor_col = 0
    # Equal row totals are read top to bottom. Equal column deficits need no
    # deduction: prefer a nearby switch, then the left one, to avoid detours.
    for row in sorted(range(5), key=lambda row: (-rows[row], row)):
        available = set(range(5))
        for _ in range(rows[row]):
            col = min(
                available,
                key=lambda col: (-remaining[col], abs(col - cursor_col), col),
            )
            assert remaining[col] > 0, "Inconsistent fuse totals"
            plan.append(row * 5 + col)
            available.remove(col)
            remaining[col] -= 1
            cursor_col = col
    assert not any(remaining), "Inconsistent fuse totals"
    return plan


def orbit_tool(p, tool):
    if p.s.phase == 0:
        p.press(2)
    p.go(16 + tool, 4)
    p.press(5)


def orbit_rotate(p, axis, orbit):
    if p.s.tool != axis + 1 or p.s.phase == 0:
        orbit_tool(p, axis + 1)
    target = orbit * 4 + p.s.cursor % 4 if axis == 0 else p.s.cursor // 4 * 4 + orbit
    p.go(target, 4)
    p.press(5)


def solve_orbit(p):
    from orbit_draft.strategy import View, choose

    start = p.actions
    while p.s.mode == 1:
        view = View(
            tuple(p.r.b[:16]), tuple(p.r.d[16:18]), tuple(p.r.d[18:21]), p.s.spins
        )
        kind, pick, target = choose(view, p.s.target - p.s.progress)
        if kind == "drop":
            if p.s.tool != 0 or p.s.phase != 0:
                orbit_tool(p, 0)
            if p.s.offer != pick:
                p.press(4)
            p.press(5)
            p.go(p.s.cursor // 4 * 4 + target, 4)
            p.press(5)
        else:
            orbit_rotate(p, pick, target)
        assert p.actions - start < 600, ("Orbit round stalled", vars(p.s))


def solve_stage(p):
    if p.r.metadata.get("secondReview"):
        from quality.strategies import solve

        if solve(p):
            return
    if p.name == "sand_rescue":
        sand_irrigate(p, extra=3 if p.s.level == 0 else 0)
        return
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
                p.press(1 if (a - r.c[i]) % 8 <= 4 else 2)
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
            known_pair = next(
                (
                    (i, j)
                    for i in memory
                    for j in memory
                    if i < j
                    and i not in matched
                    and j not in matched
                    and memory[i] == memory[j]
                ),
                None,
            )
            if known_pair:
                first, second = known_pair
            else:
                first = next(
                    i for i in range(16) if i not in memory and i not in matched
                )
                second = None
            p.go(first, 4)
            p.press(5)
            memory[first] = r.b[first]
            if second is None:
                second = next(
                    (
                        i
                        for i, value in memory.items()
                        if i != first and i not in matched and value == memory[first]
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
        weather = r.env["weather"][s.level * 12 : (s.level + 1) * 12]
        dead = set()

        def survive(st):
            day, food, wood, heat, wall = st
            if day == 12:
                return []
            if st in dead:
                return None
            # Prepare insulation early; burn only when useful and keep food ahead.
            for job in (3, 2, 1, 0):
                f, w, h, ins = food, wood, heat, wall
                if job == 0:
                    w = min(30, w + 7)
                elif job == 1:
                    f = min(30, f + 7)
                elif job == 2:
                    if w < 3:
                        continue
                    w -= 3
                    h = min(24, h + 9)
                else:
                    if w < 4 or ins == 2:
                        continue
                    w -= 4
                    ins += 1
                cost = weather[day] - ins
                if f < 2 or h <= cost:
                    continue
                tail = survive((day + 1, f - 2, w, h - cost, ins))
                if tail is not None:
                    return [job] + tail
            dead.add(st)
            return None

        route = survive((0, 10, 8, 12, 0))
        assert route is not None, (name, s.level)
        for job in route:
            p.choice("choice", job)
            p.press(5)
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
            near = (s.fish + s.tide * s.force) % 8
            deep = (s.deep + s.tide * s.force * 2) % 8
            target = max(
                range(8),
                key=lambda i: (
                    2 * (near in (i, (i + 1) % 8)) + 3 * (deep in (i, (i + 1) % 8))
                ),
            )
            p.choice("cursor", target)
            p.press(5)
        return
    if name == "auction_house":
        while s.mode == 1:
            # A cautious bidder uses the public lower appraisal, never the rival limit.
            p.choice("choice", int(s.bid + 2 > s.low - 2))
            p.press(5)
        return
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
        # Use only visible totals, never the hidden reference arrangement.
        rows = [sum(r.d[i * 5 : i * 5 + 5]) for i in range(5)]
        cols = [sum(r.d[i + 5 * j] for j in range(5)) for i in range(5)]
        for i in fuse_plan(rows, cols):
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
                    gate(gate(i // 4, i // 2 % 2, combo[0]), i % 2, combo[1]),
                    i // 4,
                    combo[2],
                )
                == r.d[i]
                for i in range(8)
            )
        )
        for i, v in enumerate(gates):
            p.choice("cursor", i, 2)
            while r.c[i] != v:
                p.press(4)
        p.press(5)
        return
    if name == "orbit_draft":
        solve_orbit(p)
        return
    if name in ("twenty_one", "chain_suit"):
        return solve_cards(p)
    if name == "compass_rose":

        def transitions(pos):
            for a in range(1, 5):
                n = step(pos, a)
                if n != pos and not r.c[n]:
                    yield a, n

        route = search(s.pos, transitions, lambda pos: pos == s.target)
        assert route is not None and len(route) < s.fuel
        walk_plan(p, route)
        p.press(5)
        return
    if name == "ruin_lexicon":
        sums = [r.d[i] + r.d[i + 1] for i in range(3)]
        before = r.d[0] < r.d[3]
        known = next(
            values
            for values in itertools.permutations(range(1, 5))
            if all(values[i] + values[i + 1] == sums[i] for i in range(3))
            and (values[0] < values[3]) == before
        )
        for i, v in enumerate(known):
            p.choice("cursor", i)
            while r.b[i] != v:
                p.press(1)
        p.press(5)
        return
    if name == "shadow_archive":
        for clue in range(3):
            p.choice("choice", clue)
            p.press(5)
        notes = [bool(r.b[s.culprit] & (1 << bit)) for bit in range(3)]
        answer = next(
            i
            for i in range(6)
            if [bool(r.b[i] & (1 << bit)) for bit in range(3)] == notes
        )
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


def snake_route(body, food, blocked=()):
    """Approach the visible food while accounting for the moving tail."""
    body = tuple(body)
    todo = deque([(body, [])])
    seen = {body}
    while todo and len(seen) < 20000:
        occupied, path = todo.popleft()
        for direction in range(1, 5):
            target = step(occupied[0], direction)
            retained = len(occupied) - (target != food)
            if target is None or target in blocked or target in occupied[:retained]:
                continue
            route = path + [direction]
            if target == food:
                return deque(route)
            moved = (target,) + occupied[:retained]
            if moved not in seen:
                seen.add(moved)
                todo.append((moved, route))
    raise AssertionError("No safe route to the visible food")


def solve_realtime(p):
    s = p.s
    r = p.r
    name = p.name
    snake_path = deque()
    while s.mode == 1:
        if name == "orbit_dodge":
            danger = {s.target}
            if s.waves >= 6:
                danger.add((s.target + 3 + s.waves % 3) % 8)
            if s.pos in danger:
                p.press(3 if (s.pos + 7) % 8 not in danger else 4)
        elif name == "gate_runner":
            runner_steer(p)
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
            metro_dispatch(p)
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
            if not snake_path:
                snake_path = snake_route(r.b[: s.length], s.food)
            desired = snake_path.popleft()
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
    if p.name == "five_forge":
        # Start in the centre and build an open diagonal in both directions.
        # Both ends remain threats, so the final stone completes five.
        for target in (27, 20, 13, 34, 41):
            p.go(target, 8)
            p.press(5)
        return
    sim = Model(p.name)
    turns = 0
    while p.s.mode == 1:
        restore(sim, snapshot(p.r))
        best = None
        for i in range(64):
            if sim.b[i]:
                continue
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
            if best is None or value > best[0]:
                best = (value, i)
        target = best[1] if best else p.s.cursor
        p.go(target, 8)
        p.press(5)
        turns += 1
        assert turns < 65


def replay(name, rom=None, capture=False, pad=True):
    p = Player(name, rom, capture, pad)
    if p.m.metadata.get("endless"):
        for round_number in range(8):
            solve_stage(p)
            if capture and round_number == 0:
                p.m.capture(p.directory / "images/play-02.png")
            if round_number < 7:
                p.next()
    else:
        while True:
            solve_stage(p)
            if not p.next():
                break
    p.finish()
    return {
        "actions": p.actions,
        "ticks": p.ticks,
        "min_sp": lib.min_sp(p.m.p),
        "levels": 8 if p.m.metadata.get("endless") else p.m.metadata.get("levels", 10),
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
