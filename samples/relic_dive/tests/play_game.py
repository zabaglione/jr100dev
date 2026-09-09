"""Input-only full-game replay. The planner may inspect hidden state, never edit it."""

import heapq
import json

from machine import ROOT, SYMS, Machine, lib

WIDTH = SYMS["MAP_WIDTH"]
HEIGHT = SYMS["MAP_HEIGHT"]

DIRS = {
    1: (0, -1),
    2: (0, 1),
    3: (-1, 0),
    4: (1, 0),
    7: (-1, -1),
    8: (1, -1),
    9: (-1, 1),
    10: (1, 1),
}


def effect(ident, item):
    if 2 <= item <= 6:
        return ident[item - 2]
    if 14 <= item <= 16:
        return ident[item - 9]
    return -1


class Player:
    def __init__(self, difficulty, wait=0):
        self.m = Machine()
        self.actions = []
        self.max_turn = 0
        self.max_floor = 0
        self.m.resume()
        for _ in range(wait):
            self.m.until("IDLE")
        self.wait = wait
        self.policy = 0
        self.route_cache = None
        self.max_floor = self.m.start(difficulty)
        self.difficulty = difficulty

    def press(self, n):
        floor = self.m.get("G_FLOOR")
        c = self.m.action(n, pad=n != 6 and n != 11)
        self.actions.append(n)
        if self.m.get("G_MODE") == 1 and self.m.get("G_FLOOR") == floor:
            self.max_turn = max(self.max_turn, c)

    def menu(self, index):
        self.press(5)
        for _ in range(index):
            self.press(2)
        self.press(5)

    def use(self, slot):
        context = self.m.map()[self.m.get("G_Y") * WIDTH + self.m.get("G_X")] == 3
        self.menu(int(context))
        for _ in range(slot):
            self.press(2)
        self.press(5)
        self.press(5)

    def path(self, grid, target):
        m = self.m
        start = (m.get("G_X"), m.get("G_Y"))
        enemies = {(e[0], e[1]): e for e in m.entities() if e[3]}
        if self.route_cache is not None:
            cost, first = self.route_cache
            return cost.get(target, 1e9), first.get(target)
        q = [(0, start)]
        cost = {start: 0}
        first = {start: None}
        while q:
            d, p = heapq.heappop(q)
            if d != cost[p]:
                continue

            x, y = p
            for action, (dx, dy) in DIRS.items():
                xx, yy = x + dx, y + dy
                if not (0 <= xx < WIDTH and 0 <= yy < HEIGHT) or grid[
                    yy * WIDTH + xx
                ] in (0, 5):
                    continue
                if (
                    dx
                    and dy
                    and (
                        grid[y * WIDTH + xx] in (0, 5) or grid[yy * WIDTH + x] in (0, 5)
                    )
                ):
                    continue
                e = enemies.get((xx, yy))
                penalty = e[3] / max(1, m.get("G_ATTACK") - 1) * 2 if e else 0
                nd = d + 1 + penalty + (5 if grid[yy * WIDTH + xx] >= 6 else 0)
                pos = (xx, yy)
                if nd < cost.get(pos, 1e9):
                    cost[pos] = nd
                    first[pos] = first[p] or action
                    heapq.heappush(q, (nd, pos))
        self.route_cache = cost, first
        return cost.get(target, 1e9), first.get(target)

    def run(self, limit=5000, stop_floor=None, save=True):
        m = self.m
        lastfloor = -1
        for step in range(limit):
            self.route_cache = None
            if stop_floor is not None and m.get("G_FLOOR") >= stop_floor:
                break
            mode = m.get("G_MODE")
            if mode in (8, 9):
                break
            assert mode == 1, (mode, self.actions[-20:])
            floor = m.get("G_FLOOR")
            hp = m.get("G_HP")
            food = m.get("G_FOOD")
            if floor != lastfloor:
                print(
                    f'difficulty={self.difficulty} floor={floor+1} hp={hp} food={food} turns={m.word("G_TURNS")}',
                    flush=True,
                )
                lastfloor = floor
            bag = list(m.read("G_BAG", 6))
            ident = list(m.read("G_IDENTITIES", 8))
            rest = (80, 60, 45)[self.difficulty]
            selected = None
            for i, item in enumerate(bag):
                if item == 21 and 22 not in bag:
                    selected = i
                    break
                if (7 <= item <= 9 and item - 3 > m.get("G_ATTACK")) or (
                    10 <= item <= 12 and item - 9 > m.get("G_DEFENSE")
                ):
                    selected = i
                    break
                if item == 1 and food <= 255 - rest:
                    selected = i
                    break
                if effect(ident, item) in (0, 5) and (
                    hp <= m.get("G_MAX_HP") - (12, 8, 6)[self.difficulty]
                    or m.get("G_POISON")
                ):
                    selected = i
                    break
            ground = next(
                (
                    it
                    for it in m.items()
                    if it[2] and it[:2] == [m.get("G_X"), m.get("G_Y")]
                ),
                None,
            )
            if selected is not None and not (7 <= bag[selected] <= 12 and ground):
                self.use(selected)
                continue
            # Resolve adjacent threats instead of oscillating around a pursuing enemy.
            grid = m.map()
            px, py = m.get("G_X"), m.get("G_Y")
            threats = []
            for ex, ey, kind, ehp, *_ in m.entities():
                if not ehp:
                    continue
                dx, dy = ex - px, ey - py
                if max(abs(dx), abs(dy)) == 1:
                    if (
                        dx
                        and dy
                        and (
                            grid[py * WIDTH + ex] in (0, 5)
                            or grid[ey * WIDTH + px] in (0, 5)
                        )
                    ):
                        continue
                    action = next(a for a, d in DIRS.items() if d == (dx, dy))
                    threats.append((ehp - (8 if kind in (10, 11, 12) else 0), action))
            if threats and self.policy >= 4 and (floor >= 2 or m.get("G_ATTACK") >= 4):
                goal_pos = next(i for i, v in enumerate(grid) if v in (3, 4))
                _, away = self.path(grid, (goal_pos % WIDTH, goal_pos // WIDTH))
                if away:
                    dx, dy = DIRS[away]
                    xx, yy = px + dx, py + dy
                    live = [e for e in m.entities() if e[3]]
                    safe = all(abs(e[0] - xx) + abs(e[1] - yy) >= 2 for e in live)
                    safe &= not any(
                        e[2] in (12, 14)
                        and (e[0] == xx or e[1] == yy)
                        and abs(e[0] - xx) + abs(e[1] - yy) <= 5
                        for e in live
                    )
                    if safe and grid[yy * WIDTH + xx] < 6:
                        self.press(away)
                        continue
                escape = next(
                    (i for i, it in enumerate(bag) if effect(ident, it) == 4),
                    None,
                )
                rust = any(
                    e[2] == 11 and abs(e[0] - px) + abs(e[1] - py) <= 2
                    for e in m.entities()
                    if e[3]
                )
                if escape is not None and (hp < 10 or rust):
                    self.use(escape)
                    continue
            if threats:
                wand = next((i for i, it in enumerate(bag) if 17 <= it <= 19), None)
                if wand is not None:
                    self.use(wand)
                    assert m.get("G_MODE") == 5
                    self.press(min(threats)[1])
                    self.press(5)
                    assert m.get("G_MODE") in (1, 8, 9)
                    continue
                hold = next(
                    (i for i, it in enumerate(bag) if effect(ident, it) == 6), None
                )
                if hold is not None and any(
                    e[3] and not e[7] and abs(e[0] - px) + abs(e[1] - py) <= 3
                    for e in m.entities()
                ):
                    self.use(hold)
                    continue
                strength = next(
                    (i for i, it in enumerate(bag) if effect(ident, it) == 2),
                    None,
                )
                if strength is not None and not m.get("G_BUFF"):
                    self.use(strength)
                    continue
                self.press(min(threats)[1])
                continue
            # Spend surplus food on natural recovery in a safe area.
            nearest = min(
                (abs(e[0] - px) + abs(e[1] - py) for e in m.entities() if e[3]),
                default=99,
            )
            if (
                hp < m.get("G_MAX_HP")
                and food
                > (
                    (220, 180, 130, 100, 255, 220, 180, 130)[self.policy]
                    if self.difficulty == 2
                    else 100
                )
                and nearest > 8
            ):
                self.menu(1 + int(grid[py * WIDTH + px] == 3))
                continue
            grid = m.map()
            goal = next(i for i, v in enumerate(grid) if v in (3, 4))
            targets = []
            goal_distance, _ = self.path(grid, (goal % WIDTH, goal // WIDTH))
            if 0 in bag:
                for x, y, item in m.items():
                    useful = (7 <= item <= 9 and item - 3 > m.get("G_ATTACK")) or (
                        10 <= item <= 12 and item - 9 > m.get("G_DEFENSE")
                    )
                    useful |= item == 21 and 22 not in bag and 21 not in bag
                    useful |= 17 <= item <= 19 and not any(17 <= b <= 19 for b in bag)
                    useful |= item == 1 and (food < 180 or bag.count(1) < 2)
                    useful |= (
                        effect(ident, item) in (0, 5)
                        and sum(effect(ident, b) in (0, 5) for b in bag) < 2
                    )
                    if useful:
                        dist, action = self.path(grid, (x, y))
                        if self.difficulty == 2 and not (7 <= item <= 12 or item == 21):
                            # Reject detours that consume more food than they return.
                            extra = (
                                dist
                                + max(abs(x - goal % WIDTH), abs(y - goal // WIDTH))
                                - goal_distance
                            )
                            if extra > (
                                (20, 30, 40, 50, 0, 10, 20, 30)[self.policy]
                                if item == 1
                                else (8, 16, 24, 32, 0, 8, 12, 16)[self.policy]
                            ):
                                continue
                        # Strong gear makes every subsequent fight cheaper.
                        if 7 <= item <= 12 or item == 21:
                            dist *= 0.35
                        targets.append((dist, action, x, y))
            elif selected is None:
                # Consume a known harmless scroll to free a slot; mapping first.
                scroll = next(
                    (i for i, it in enumerate(bag) if effect(ident, it) == 3),
                    None,
                )
                if scroll is not None:
                    self.use(scroll)
                    continue
                # Drop poison or redundant gear through the ordinary item menu.
                trash = next(
                    (
                        i
                        for i, it in enumerate(bag)
                        if it == 20
                        or (it == 21 and 22 in bag)
                        or (effect(ident, it) in (1, 7))
                        or (7 <= it <= 9 and it - 3 <= m.get("G_ATTACK"))
                        or (10 <= it <= 12 and it - 9 <= m.get("G_DEFENSE"))
                    ),
                    None,
                )
                if trash is not None and not ground:
                    context = grid[m.get("G_Y") * WIDTH + m.get("G_X")] == 3
                    self.menu(int(context))
                    for _ in range(trash):
                        self.press(2)
                    self.press(5)
                    self.press(2)
                    self.press(5)
                    continue
            if (
                self.difficulty == 2
                and floor >= (2 if self.policy >= 4 else 4)
                and food > goal_distance + (5, 15, 35, 60, 0, 5, 15, 25)[self.policy]
            ):
                _, goal_action = self.path(grid, (goal % WIDTH, goal // WIDTH))
                # Descend while supplies suffice; do not tour every optional item.
                if goal_action is not None:
                    targets.append(
                        (
                            goal_distance
                            * (0.4, 0.8, 1.2, 1.6, 0.05, 0.2, 0.4, 0.6)[self.policy],
                            goal_action,
                            goal % WIDTH,
                            goal // WIDTH,
                        )
                    )
                elif grid[m.get("G_Y") * WIDTH + m.get("G_X")] == 3:
                    before = lib.clocks(m.p)
                    self.menu(0)
                    self.max_floor = max(self.max_floor, lib.clocks(m.p) - before)
                    continue
            if targets:
                _, action, x, y = min(targets, key=lambda t: t[0])
                if action is None:
                    # Ground item after a full-bag pickup: step out and back.
                    action = next(
                        (
                            a
                            for a, (dx, dy) in DIRS.items()
                            if a <= 4 and grid[(y + dy) * WIDTH + x + dx] == 1
                        ),
                        None,
                    )
            else:
                _, action = self.path(grid, (goal % WIDTH, goal // WIDTH))
                if action is None and grid[m.get("G_Y") * WIDTH + m.get("G_X")] == 3:
                    before = lib.clocks(m.p)
                    self.menu(0)
                    self.max_floor = max(self.max_floor, lib.clocks(m.p) - before)
                    continue
            if action is None:
                raise AssertionError("No route")
            self.press(action)
        result = {
            "difficulty": self.difficulty,
            "idle_waits": self.wait,
            "mode": m.get("G_MODE"),
            "floor": m.get("G_FLOOR") + 1,
            "hp": m.get("G_HP"),
            "food": m.get("G_FOOD"),
            "turns": m.word("G_TURNS"),
            "attack": m.get("G_ATTACK"),
            "defense": m.get("G_DEFENSE"),
            "inputs": self.actions,
            "max_action_cycles": self.max_turn,
            "max_floor_cycles": self.max_floor,
        }
        if save:
            (ROOT / "build" / f"replay-{self.difficulty}.json").write_text(
                json.dumps(result, indent=2) + "\n"
            )
        print({k: v for k, v in result.items() if k != "inputs"}, flush=True)
        return result


if __name__ == "__main__":
    import sys

    for d in map(int, sys.argv[1:] or ("0", "1", "2")):
        result = Player(d).run()
        assert result["mode"] == 9, {k: v for k, v in result.items() if k != "inputs"}
