"""Independent rules model and bounded breadth-first search for authored rooms."""

import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DELTA = {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}


class Room:
    def __init__(self, data):
        self.data = data
        grid = data["map"]
        self.walls = {
            (x, y) for y, r in enumerate(grid) for x, c in enumerate(r) if c == "#"
        }
        self.guards = tuple(
            (x, y, "^v<>".index(c) + 1)
            for y, r in enumerate(grid)
            for x, c in enumerate(r)
            if c in "^v<>"
        )
        self.start = next(
            (x, y) for y, r in enumerate(grid) for x, c in enumerate(r) if c == "@"
        )
        self.exit = next(
            (x, y) for y, r in enumerate(grid) for x, c in enumerate(r) if c == "X"
        )
        self.initial = (*self.start, data["ammo"], (1 << len(self.guards)) - 1, 2, ())

    def step(self, state, action):
        x, y, ammo, alive, phase, bolts = state
        if action in DELTA:
            dx, dy = DELTA[action]
            x, y = x + dx, y + dy
            if (x, y) in self.walls:
                return None
            for i, (gx, gy, _) in enumerate(self.guards):
                if (x, y) == (gx, gy):
                    alive &= ~(1 << i)
            if any((x, y) == b[:2] for b in bolts if b is not None):
                return None
        elif action >= 9:  # Free aim in the menu, then shoot in this direction.
            if not ammo:
                return None
            ammo -= 1
            dx, dy = DELTA[action - 8]
            for distance in range(1, 5):
                target = (x + dx * distance, y + dy * distance)
                if target in self.walls:
                    break
                hit = next(
                    (
                        i
                        for i, g in enumerate(self.guards)
                        if alive & (1 << i) and target == g[:2]
                    ),
                    None,
                )
                if hit is not None:
                    alive &= ~(1 << hit)
                    break
        elif action != 7:
            raise ValueError(action)
        # Slots retain order. The allocation order is part of friendly-fire rules.
        slots = list(bolts)
        for index, bolt in enumerate(slots):
            if bolt is None:
                continue
            bx, by, direction = bolt
            dx, dy = DELTA[direction]
            target = bx + dx, by + dy
            if target in self.walls:
                slots[index] = None
            elif target == (x, y):
                return None
            else:
                hit = next(
                    (
                        i
                        for i, g in enumerate(self.guards)
                        if alive & (1 << i) and target == g[:2]
                    ),
                    None,
                )
                if hit is not None:
                    alive &= ~(1 << hit)
                    slots[index] = None
                else:
                    slots[index] = (*target, direction)
        phase = (phase + 1) % 3
        if phase == 0:
            for i, (gx, gy, direction) in enumerate(self.guards):
                if not alive & (1 << i):
                    continue
                dx, dy = DELTA[direction]
                target = gx + dx, gy + dy
                if target in self.walls:
                    continue
                if target == (x, y):
                    return None
                hit = next(
                    (
                        j
                        for j, g in enumerate(self.guards)
                        if alive & (1 << j) and target == g[:2]
                    ),
                    None,
                )
                if hit is not None:
                    alive &= ~(1 << hit)
                    continue
                try:
                    index = slots.index(None)
                    slots[index] = (*target, direction)
                except ValueError:
                    if len(slots) < 16:
                        slots.append((*target, direction))
        while slots and slots[-1] is None:
            slots.pop()
        return x, y, ammo, alive, phase, tuple(slots)

    def won(self, state):
        return state[:2] == self.exit and not state[3]

    def solve(self, limit=500_000):
        initial = self.initial
        previous = {initial: None}
        queue = deque([initial])
        while queue:
            state = queue.popleft()
            for action in (1, 2, 3, 4, 7, 9, 10, 11, 12):
                new = self.step(state, action)
                if new is None or new in previous:
                    continue
                previous[new] = state, action
                if self.won(new):
                    path = []
                    while previous[new] is not None:
                        new, action = previous[new]
                        path.append(action)
                    return list(reversed(path)), len(previous)
                queue.append(new)
            if len(previous) > limit:
                raise RuntimeError(f'search limit: {self.data["name"]}')
        raise RuntimeError(f'unsolvable: {self.data["name"]}')


if __name__ == "__main__":
    rooms = json.loads((ROOT / "levels.json").read_text())
    solutions = []
    for i, data in enumerate(rooms):
        room = Room(data)
        actions, visited = room.solve()
        print(
            f'{i+1:02} {data["name"]}: {len(actions)} acts, {visited} states',
            flush=True,
        )
        solutions.append({"sector": i + 1, "actions": actions})
    (ROOT / "solutions.json").write_text(json.dumps(solutions, indent=2) + "\n")
