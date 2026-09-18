"""Input-only play policies, using public board information and previews."""

from collections import deque
from functools import lru_cache
from itertools import product


def lights(board):
    answers = []
    for first in range(32):
        state, path = list(board[:25]), []

        def press(pos, state=state, path=path):
            path.append(pos)
            for other in range(25):
                if abs(pos % 5 - other % 5) + abs(pos // 5 - other // 5) <= 1:
                    state[other] ^= 1

        for x in range(5):
            if first >> x & 1:
                press(x)
        for pos in range(5, 25):
            if state[pos - 5]:
                press(pos)
        if not any(state):
            answers.append(path)
    return min(answers, key=len)


@lru_cache(None)
def stone_win(piles, misere):
    if not any(piles):
        return misere
    return any(
        not stone_win(piles[:i] + (count - take,) + piles[i + 1 :], misere)
        for i, count in enumerate(piles)
        for take in range(1, min(3, count) + 1)
    )


def solve(p):
    from checks import Model
    from design_levels import search, step
    from replay import restore, snapshot, walk_plan

    name, r, s = p.name, p.r, p.s
    if name == "lumen_cross":
        for pos in lights(r.b):
            p.go(pos, 5)
            p.press(5)
    elif name == "stone_balance":
        while s.mode == 1:
            piles = tuple(r.b[:3])
            pile, take = next(
                (i, n)
                for i, count in enumerate(piles)
                for n in range(1, min(3, count) + 1)
                if not stone_win(
                    piles[:i] + (count - n,) + piles[i + 1 :], bool(s.misere)
                )
            )
            p.choice("pile", pile, 2)
            p.choice("take", take, 3)
            p.press(5)
    elif name == "quiet_route":
        sim = Model(name)
        restore(sim, snapshot(r))
        todo = deque([(snapshot(sim), [])])
        best = {}
        while todo:
            state, path = todo.popleft()
            restore(sim, state)
            key = tuple(
                getattr(sim.s, n)
                for n in ("pos", "guard", "direction", "quiet", "key", "intel")
            )
            if sim.s.mode == 2 and sim.s.intel:
                walk_plan(p, path)
                break
            if sim.s.mode != 1 or best.get(key, -1) >= sim.s.battery:
                continue
            best[key] = sim.s.battery
            for a in range(1, 6):
                restore(sim, state)
                sim.action(a)
                todo.append((snapshot(sim), path + [a]))
        else:
            raise AssertionError((name, s.level, "No route with optional intelligence"))
    elif name == "mirror_relic":
        jewels = [i for i in range(64) if r.c[i]]
        bits = {pos: 1 << i for i, pos in enumerate(jewels)}

        def transitions(state):
            pos, mask, phase = state
            for a in (1, 2, 3, 4, 5, 7):
                turn = a in (5, 7)
                dest = (
                    (
                        pos % 8 * 8 + 7 - pos // 8
                        if a == 5
                        else (7 - pos % 8) * 8 + pos // 8
                    )
                    if turn
                    else step(pos, a)
                )
                if dest is None or r.b[dest] == 1:
                    continue
                next_phase = (phase + (1 if a == 5 else 3)) % 4 if turn else phase
                collected = bits.get(dest, 0) if r.c[dest] == next_phase + 1 else 0
                yield a, (dest, mask | collected, next_phase)

        route = search(
            (s.pos, 0, 0), transitions, lambda st: st[0] == 53 and st[1] == 7
        )
        assert route and sum(a in (5, 7) for a in route) <= 20
        walk_plan(p, route)
    elif name == "compass_rose":
        candidates = {i for i in range(64) if not r.c[i]}

        def reading(origin, target):
            dy, dx = target // 8 - origin // 8, target % 8 - origin % 8
            distance = abs(dy) + abs(dx)
            return (
                1 if dy < 0 else 2 if dy > 0 else 0,
                1 if dx < 0 else 2 if dx > 0 else 0,
                0 if distance <= 2 else 1 if distance <= 5 else 2,
            )

        def routes():
            result = {s.pos: []}
            q = deque([s.pos])
            while q:
                pos = q.popleft()
                for a in range(1, 5):
                    dest = step(pos, a)
                    if dest is not None and dest not in result and not r.c[dest]:
                        result[dest] = result[pos] + [a]
                        q.append(dest)
            return result

        while s.mode == 1:
            observed = (s.north, s.east, s.band)
            candidates = {i for i in candidates if reading(s.survey_pos, i) == observed}
            assert candidates
            paths = routes()
            if len(candidates) == 1:
                target = next(iter(candidates))
                assert len(paths[target]) < s.fuel
                walk_plan(p, paths[target])
                p.press(5)
                break
            assert s.surveys

            def score(pos, candidates=candidates, paths=paths):
                groups = {}
                for target in candidates:
                    key = reading(pos, target)
                    groups[key] = groups.get(key, 0) + 1
                return max(groups.values()), len(paths[pos])

            target = min(
                (pos for pos in paths if len(paths[pos]) + 3 < s.fuel), key=score
            )
            walk_plan(p, paths[target])
            p.press(7)
    elif name == "potion_path":

        def transitions(st):
            x, y, stock = st
            for i, (dx, dy) in enumerate(((-2, 0), (1, 2), (0, -1), (3, 1))):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 8 and 0 <= ny < 8 and stock[i] and not r.b[ny * 8 + nx]:
                    yield i, (nx, ny, stock[:i] + (stock[i] - 1,) + stock[i + 1 :])

        route = search(
            (s.x, s.y, tuple(r.c[:4])), transitions, lambda st: st[:2] == (s.tx, s.ty)
        )
        assert route and len(route) <= 12
        for i in route:
            p.choice("ingredient", i)
            p.press(5)
    elif name == "word_foundry":
        words = [bytes(r.env["words"][i * 3 : i * 3 + 3]) for i in range(16)]
        for target in (s.via, s.goal):
            route = search(
                s.word,
                lambda i: (
                    (j, j)
                    for j in range(16)
                    if sum(a != b for a, b in zip(words[i], words[j])) == 1
                ),
                lambda i, target=target: i == target,
            )
            assert route
            for i in route:
                p.go(i, 4)
                p.press(5)
    elif name == "shadow_archive":
        candidates = set(range(6))
        while len(candidates) > 1:
            trait = min(
                (i for i in range(3) if not r.c[i]),
                key=lambda bit: abs(
                    sum(bool(r.b[i] & (1 << bit)) for i in candidates) * 2
                    - len(candidates)
                ),
            )
            p.choice("file", trait)
            p.press(5)
            # This is the YES/NO answer now printed in the opened file.
            observed = bool(r.b[s.culprit] & (1 << trait))
            candidates = {
                i for i in candidates if bool(r.b[i] & (1 << trait)) == observed
            }
        p.press(2)
        p.choice("choice", next(iter(candidates)))
        p.press(5)
    elif name == "hearth_zero":
        while s.mode == 1:
            forecast = r.env["weather"][
                s.level * 12 + s.day : s.level * 12 + min(12, s.day + 3)
            ]

            def future(day, food, wood, heat, wall, forecast=forecast):
                if day == len(forecast):
                    return (min(food, 8) + min(wood, 9) + min(heat, 18) + wall * 5, 0)
                best = (-1000, 0)
                for job in range(4):
                    f, w, h, ins = food, wood, heat, wall
                    if job == 0:
                        w = min(30, w + 7)
                    elif job == 1:
                        f = min(30, f + 7)
                    elif job == 2 and w >= 3:
                        w -= 3
                        h = min(24, h + 9)
                    elif job == 3 and w >= 4 and ins < 2:
                        w -= 4
                        ins += 1
                    else:
                        continue
                    cost = forecast[day] - ins
                    if f < 2 or h <= cost:
                        continue
                    rating = future(day + 1, f - 2, w, h - cost, ins)[0]
                    best = max(best, (rating, job))
                return best

            rating, job = future(0, s.food, s.wood, s.heat, s.insulation)
            assert rating > -1000, (name, s.day)
            p.choice("choice", job)
            p.press(5)
    elif name == "orchard_days":
        p.go(17, 4)
        p.press(5)
        plots = (s.quota + 6) // 7
        for i in range(plots):
            p.go(i, 4)
            p.press(5)
        while s.mode == 1:
            ripe = next((i for i in range(plots) if r.b[i] >= 5), None)
            if ripe is not None:
                target = ripe
            elif s.water:
                target = max((i for i in range(plots) if r.b[i]), key=lambda i: r.b[i])
            else:
                target = 19
            p.go(target, 4)
            p.press(5)
    elif name == "tidal_nets":
        while s.mode == 1:
            near = (s.fish + s.tide * s.force) % 8
            deep = (s.deep + s.tide * s.force * 2) % 8
            candidates = []
            for wide, column in product(range(2), range(8)):
                if 1 + wide > s.rope:
                    continue
                columns = (column, (column + 1) % 8) if wide else (column,)
                gain = 2 * (near in columns) + 4 * (deep in columns)
                # Reserve at least one rope for each remaining cast.
                reserve = s.rope - 1 - wide >= 8 - s.casts
                candidates.append(
                    ((gain if reserve else gain - 6, -wide), column, wide)
                )
            _, column, wide = max(candidates)
            if s.wide != wide:
                p.press(1)
            p.choice("cursor", column)
            p.press(5)
    elif name == "cargo_balance":
        while s.mode == 1:
            weights = r.env["cargo"][
                s.level * 12 + s.loads : s.level * 12 + min(12, s.loads + 3)
            ]

            def future(depth, heights, left, right, weights=weights):
                if depth == len(weights):
                    return -abs(left + s.wind - right) - sum(n * n for n in heights)
                best = -10000
                for i in range(4):
                    if heights[i] == 4:
                        continue
                    weight = weights[depth]
                    nl = left + (weight * (3 if i == 0 else 1) if i < 2 else 0)
                    nr = right + (weight * (3 if i == 3 else 1) if i >= 2 else 0)
                    if abs(nl + s.wind - nr) > s.tolerance:
                        continue
                    counts = heights[:i] + (heights[i] + 1,) + heights[i + 1 :]
                    best = max(
                        best,
                        future(depth + 1, counts, nl, nr)
                        + weight * (2 if i in (0, 3) else 1),
                    )
                return best

            ratings = []
            for i in range(4):
                if r.c[i] >= 4:
                    continue
                nl = s.left + (s.weight * (3 if i == 0 else 1) if i < 2 else 0)
                nr = s.right + (s.weight * (3 if i == 3 else 1) if i >= 2 else 0)
                if abs(nl + s.wind - nr) <= s.tolerance:
                    heights = tuple(r.c[:i]) + (r.c[i] + 1,) + tuple(r.c[i + 1 : 4])
                    ratings.append((future(1, heights, nl, nr), i))
            assert ratings, (name, s.level, s.loads)
            p.choice("cursor", max(ratings)[1])
            p.press(5)
    elif name == "auction_house":
        while s.mode == 1:
            # Inspection is valuable only near the displayed lower bound.
            if not s.inspected and s.bid + 2 >= s.low - 2 and s.bid + 2 <= s.high - 2:
                choice = 2
            else:
                choice = (
                    3 if s.bid + 2 > s.low - 2 else (1 if s.bid + 6 <= s.low - 2 else 0)
                )
            p.choice("choice", choice)
            p.press(5)
    elif name == "twenty_one" and hasattr(p, "pacing"):
        while s.mode == 1:
            up = min(10, r.c[0] % 13 + 1)
            value = s.player
            soft = (
                any(card % 13 == 0 for card in r.b[: s.np])
                and sum(min(10, card % 13 + 1) for card in r.b[: s.np]) + 10 == value
            )
            if (
                s.np == 2
                and s.coins >= 4
                and not soft
                and value in (10, 11)
                and 2 <= up <= 9
            ):
                choice = 2
            elif soft:
                choice = int(value >= 19 or value == 18 and 2 <= up <= 8)
            else:
                choice = int(
                    value >= 17
                    or value >= 13
                    and 2 <= up <= 6
                    or value == 12
                    and 4 <= up <= 6
                )
            p.choice("choice", choice)
            p.press(5)
    elif name in (
        "orbit_dodge",
        "echo_parry",
        "pendulum_port",
        "lunar_touchdown",
        "night_swarm",
        "star_lance",
        "ribbon_snake",
    ):
        play_action(p)
    else:
        return False
    return True


def play_action(p):
    from replay import snake_route

    r, s, name = p.r, p.s, p.name
    iterations = 0
    while s.mode == 1:
        iterations += 1
        assert iterations < 3000, (name, "policy stalled", vars(s))
        if name == "orbit_dodge":
            danger = {(s.ring, s.target)} | (
                {(s.ring ^ 1, s.other)} if s.dual else set()
            )
            distance = min((s.gem - s.pos) % 8, (s.pos - s.gem) % 8) + (
                s.orbit != s.gem_ring
            )
            if distance < s.window - s.age:
                if s.orbit != s.gem_ring:
                    p.press(5)
                elif s.pos != s.gem:
                    p.press(4 if (s.gem - s.pos) % 8 <= 4 else 3)
            elif (s.orbit, s.pos) in danger:
                if (s.orbit ^ 1, s.pos) not in danger:
                    p.press(5)
                else:
                    p.press(4)
        elif name == "echo_parry":
            if s.stance != s.attack:
                p.press(1 if s.attack == 0 else 2)
            if s.phase == 1 and s.age == 1 and not s.guarded:
                p.press(5)
        elif name == "pendulum_port":
            if r.env["landing"]() == s.target:
                p.press(5)
        elif name == "lunar_touchdown":
            target = s.target + 1
            if s.x != target:
                p.press(4 if s.x < target else 3)
            if s.speed >= 2:
                p.press(5)
        elif name == "star_lance":
            danger = {r.d[i] for i in range(3) if 5 <= r.c[i] < 8}
            if s.ship in danger:
                choices = [
                    x
                    for x in (s.ship - 1, s.ship + 1)
                    if 0 <= x <= 7 and x not in danger
                ]
                if choices:
                    p.press(3 if choices[0] < s.ship else 4)
            elif s.cool == 0:
                targets = [
                    (abs((i % 8 + s.shift) % 8 - s.ship), i)
                    for i in range(24)
                    if r.b[i]
                ]
                if targets:
                    _, enemy = min(targets)
                    target = (enemy % 8 + s.shift) % 8
                    if s.ship != target:
                        p.press(4 if target > s.ship else 3)
                    elif s.heat <= 4:
                        bottom = max(
                            i
                            for i in range(24)
                            if r.b[i] and (i % 8 + s.shift) % 8 == s.ship
                        )
                        p.press(1 if r.b[bottom] > 1 else 5)
        elif name == "night_swarm":
            distance = lambda a, b: abs(a % 8 - b % 8) + abs(a // 8 - b // 8)
            enemies = [pos for pos in r.b[:8] if pos != 255]
            nearby = [pos for pos in enemies if distance(pos, s.pos) <= 3]
            if s.cooldown == 0 and nearby:
                p.press(5)
            elif enemies:
                choices = [(0, s.pos)] + [
                    (a, r.env["move8"](s.pos, a)) for a in (1, 2, 3, 4, 9, 10, 11, 12)
                ]

                def score(item, distance=distance, enemies=enemies):
                    action, pos = item
                    nearest = min(distance(pos, e) for e in enemies)
                    safety = min(nearest, 3) * 10
                    salvage = max(0, 8 - distance(pos, s.cell)) if s.cell != 255 else 0
                    return safety + salvage - (3 if nearest > 3 else 0) - bool(action)

                direction, _ = max(choices, key=score)
                if direction:
                    p.press(direction)
        elif name == "ribbon_snake":
            route = snake_route(
                r.b[: s.length], s.food, blocked={i for i in range(64) if r.d[i]}
            )
            desired = route[0]
            if s.dir != desired:
                p.press(desired)
        if s.mode == 1:
            p.wait()
