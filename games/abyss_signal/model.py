"""Independent turn rules and route search, without emulator state injection."""

import json
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path

WORLD = json.loads(Path(__file__).with_name("world.json").read_text())
GRID = WORLD["map"]
SITES = [(s["x"], s["y"]) for s in WORLD["sites"]]
DIR = {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}
CURRENTS = {2: 4, 3: 2, 4: 3, 5: 1}


@dataclass
class State:
    x: int = 2
    y: int = 2
    oxygen: int = 220
    hull: int = 5
    flags: int = 0
    sight: int = 0
    noise: int = 0
    quiet: int = 0
    turn: int = 0
    hx: int = 22
    hy: int = 16
    grace: int = 0
    mode: int = 1


def advance(state, action):
    s = replace(state)
    if action == 10:
        s.quiet ^= 1
        return s
    if action == 9:
        site = next(
            (
                i
                for i, (x, y) in enumerate(SITES)
                if not (s.flags >> i & 1) and abs(s.x - x) + abs(s.y - y) <= 1
            ),
            None,
        )
        if site is None:
            return s
        s.flags |= 1 << site
        s.oxygen = max(0, s.oxygen - 2)
    elif action == 8:
        s.oxygen = max(0, s.oxygen - 2)
        s.sight = 7
        s.noise = 9
    else:
        s.oxygen = max(0, s.oxygen - 1 - s.quiet)
        if action in DIR:
            dx, dy = DIR[action]
            nx, ny = s.x + dx, s.y + dy
            if GRID[ny][nx] == 1:
                s.hull = max(0, s.hull - 1)
            else:
                s.x, s.y = nx, ny
    s.turn = (s.turn + 1) % 256
    s.sight = max(0, s.sight - 1)
    s.noise = max(0, s.noise - 1)
    s.grace = max(0, s.grace - 1)
    tile = GRID[s.y][s.x]
    if tile in CURRENTS:
        dx, dy = DIR[CURRENTS[tile]]
        nx, ny = s.x + dx, s.y + dy
        if GRID[ny][nx] != 1:
            s.x, s.y = nx, ny
            s.oxygen = max(0, s.oxygen - 1)
    if s.turn % (4 if s.quiet else 2) == 0:
        target = (
            (s.x, s.y)
            if abs(s.x - s.hx) + abs(s.y - s.hy) <= 6 or s.noise
            else ((22, 20) if s.turn & 16 else (18, 14))
        )
        tx, ty = target
        nx = s.hx + (tx > s.hx) - (tx < s.hx)
        if nx != s.hx and GRID[s.hy][nx] != 1:
            s.hx = nx
        else:
            ny = s.hy + (ty > s.hy) - (ty < s.hy)
            if GRID[ny][s.hx] != 1:
                s.hy = ny
    if abs(s.x - s.hx) + abs(s.y - s.hy) <= 1 and not s.grace:
        s.hull = max(0, s.hull - 1)
        s.grace = 4
    if not s.hull or not s.oxygen:
        s.mode = 4
    elif s.flags == 31 and (s.x, s.y) == (2, 2):
        s.mode = 5
    elif action == 9:
        s.mode = 3
    return s


def route(state, target, radius=1):
    queue = deque([(state.x, state.y, [])])
    seen = {(state.x, state.y)}
    while queue:
        x, y, path = queue.popleft()
        if abs(x - target[0]) + abs(y - target[1]) <= radius:
            return path
        for a, (dx, dy) in DIR.items():
            nx, ny = x + dx, y + dy
            if GRID[ny][nx] == 1:
                continue
            tile = GRID[ny][nx]
            if tile in CURRENTS:
                cx, cy = DIR[CURRENTS[tile]]
                if GRID[ny + cy][nx + cx] != 1:
                    nx += cx
                    ny += cy
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                queue.append((nx, ny, [*path, a]))
    raise AssertionError("No route")
