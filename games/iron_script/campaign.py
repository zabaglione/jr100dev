"""Authored factory rooms and an independent finite-state route solver.

Run this file to regenerate levels.json/solutions.json. The solver first finds
safe action routes, then encodes repeated pairs as L; it never invokes rules.py.
"""

import json
from collections import deque
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TILES = {".": 0, "#": 1, "G": 3, "s": 4, "e": 5, "D": 6, "~": 7, "E": 8}
DIRECTIONS = {"^": 1, "v": 2, "<": 3, ">": 4}
COMMANDS = ".^v<>FUL"

# Name, ammo, usable slots, initial laser phase, six interior rows.
# Side alcoves are deliberate: turning requires a movement command, so a firing
# position, a detour around armor, or a waiting square can change the program.
ROOMS = [
    (
        "BOOT SEQUENCE",
        1,
        12,
        0,
        [">sDe.G", "##.###", "......", ".####.", "......", "######"],
    ),
    (
        "CORNER SHOT",
        1,
        12,
        0,
        [">s....", "##D###", "##..eG", "##.###", ".....#", "######"],
    ),
    (
        "HEAVY GUARD",
        2,
        12,
        0,
        [">sD.EG", ".#####", "......", "####.#", "......", "######"],
    ),
    (
        "TWIN LOCKS",
        1,
        12,
        0,
        [">sD.eD", "##.##.", ".....G", ".#####", "......", "######"],
    ),
    (
        "LASER CLOCK",
        0,
        12,
        0,
        [">~...G", "######", "......", ".####.", "......", "######"],
    ),
    (
        "TIMED CORNER",
        0,
        12,
        0,
        [">..###", "##~###", "##...G", "##.###", "......", "######"],
    ),
    (
        "PULSE AND FIRE",
        1,
        12,
        0,
        [">.~.eG", "##.###", "......", ".####.", "......", "######"],
    ),
    (
        "LIVE CIRCUIT",
        1,
        12,
        1,
        [">sD~eG", "##.###", "......", "####.#", "......", "######"],
    ),
    (
        "PAIR REPLAY",
        0,
        8,
        0,
        [">.....", "#####.", "#####.", "#####.", "#####.", ".....G"],
    ),
    (
        "STAIR MACRO",
        0,
        8,
        0,
        [">.####", "#..###", "##..##", "###..#", "####..", "#####G"],
    ),
    (
        "LOOPED SHOTS",
        2,
        6,
        0,
        [">..eeG", ".#####", "......", "####.#", "......", "######"],
    ),
    (
        "PULSE MACRO",
        0,
        9,
        1,
        [">.....", "#####~", "#####.", "#####.", "#####.", ".....G"],
    ),
    (
        "BACK TO SWITCH",
        1,
        12,
        0,
        ["GDe.##", "##.###", "#s..##", "##^###", "......", "######"],
    ),
    (
        "ARMOR OR DETOUR",
        1,
        12,
        0,
        [">..E.G", ".##..#", "...e..", "#####.", "......", "######"],
    ),
    (
        "CROSS FIRE",
        2,
        12,
        0,
        [">..e..", "#####.", "###G.e", "#####.", "......", "######"],
    ),
    (
        "LOCKED SIGHT",
        2,
        12,
        0,
        [">sD.E.", "#####D", "#####G", "###...", "###.##", "......"],
    ),
    (
        "PHASE SHIFT",
        1,
        12,
        1,
        [">s.~..", "#####D", "###G.e", "#####.", "......", "######"],
    ),
    (
        "SAFE WAITING",
        1,
        12,
        0,
        [">~.~eG", "######", "......", ".####.", "......", "######"],
    ),
    (
        "BENT LASER",
        2,
        12,
        1,
        [">sD.##", "###~##", "###..E", "#####G", "......", "######"],
    ),
    (
        "TWO SENTRY LANES",
        2,
        12,
        0,
        [">...e.", "####.~", "##G.e.", "####.#", "......", "######"],
    ),
    (
        "SWITCH MACRO",
        1,
        10,
        0,
        [">sD...", "#####.", "#####e", "#####.", "#####.", ".....G"],
    ),
    (
        "ARMORED CLOCK",
        2,
        12,
        0,
        [">sD~.E", "#####.", "#####G", "###...", "###.##", "......"],
    ),
    (
        "FINAL APPROACH",
        2,
        12,
        1,
        [">sD.~.", "#####.", "###G.E", "#####.", "......", "######"],
    ),
    (
        "FACTORY CORE",
        3,
        12,
        1,
        [">sD~e.", "#####.", "#####.", "#####E", ".....G", "######"],
    ),
]


def step(pos, action):
    x, y = pos % 8, pos // 8
    dx, dy = {1: (0, -1), 2: (0, 1), 3: (-1, 0), 4: (1, 0)}[action]
    nx, ny = x + dx, y + dy
    return ny * 8 + nx if 0 <= nx < 8 and 0 <= ny < 8 else pos


def encode(room):
    _, ammo, slots, phase, rows = room
    assert len(rows) == 6 and all(len(row) == 6 for row in rows)
    board = "#" * 8 + "".join("#" + row + "#" for row in rows) + "#" * 8
    starts = [i for i, tile in enumerate(board) if tile in DIRECTIONS]
    assert len(starts) == 1 and board.count("G") == 1
    start = starts[0]
    return [TILES.get(ch, 0) for ch in board] + [
        start,
        DIRECTIONS[board[start]],
        ammo,
        slots,
        phase,
    ]


def initial(level):
    # Position, facing, ammo, gate, phase, surviving sentry hit points.
    return (
        level[64],
        level[65],
        level[66],
        0,
        level[68],
        tuple(2 if v == 8 else 1 for v in level[:64] if v in (5, 8)),
    )


def transition(level, state, command):
    pos, facing, ammo, gate, phase, hp = state
    sentries = [i for i, v in enumerate(level[:64]) if v in (5, 8)]
    health = dict(zip(sentries, hp))
    phase = 1 - phase
    if 1 <= command <= 4:
        target = step(pos, command)
        if (
            level[target] == 1
            or (level[target] == 6 and not gate)
            or health.get(target, 0)
        ):
            return None
        pos, facing = target, command
    elif command == 5:
        if not ammo:
            return None
        ammo -= 1
        target = pos
        for _ in range(7):
            target = step(target, facing)
            if level[target] == 1 or (level[target] == 6 and not gate):
                break
            if health.get(target, 0):
                health[target] -= 1
                break
        hp = tuple(health[p] for p in sentries)
    elif command == 6:
        if level[pos] != 4:
            return None
        gate = 1 - gate
    if level[pos] == 7 and phase:
        return None
    return pos, facing, ammo, gate, phase, hp


def compress(route):
    @lru_cache(None)
    def suffix(index, previous):
        if index == len(route):
            return ()
        command = route[index]
        result = (command,) + suffix(index + 1, (*previous, command)[-2:])
        if (
            len(previous) == 2
            and 7 not in previous
            and tuple(route[index : index + 2]) == previous
        ):
            repeated = (7,) + suffix(index + 2, (previous[-1], 7))
            if len(repeated) < len(result):
                result = repeated
        return result

    return suffix(0, ())


def solve(level, allowed=range(7)):
    start = initial(level)
    queue = deque([(start, ())])
    seen = {start}
    while queue:
        state, route = queue.popleft()
        if level[state[0]] == 3:
            return route
        for command in allowed:
            nxt = transition(level, state, command)
            if nxt is not None and nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, (*route, command)))
    return None


def solve_program(level):
    """Breadth-first search in instruction slots, including both loop actions."""
    start = initial(level)
    queue = deque([(start, (), ())])
    seen = {(start, ())}
    while queue:
        state, previous, program = queue.popleft()
        if level[state[0]] == 3:
            return program
        if len(program) == level[67]:
            continue
        for command in range(8):
            if command == 7 and (len(previous) != 2 or 7 in previous):
                continue
            nxt = state
            for action in previous if command == 7 else (command,):
                nxt = transition(level, nxt, action)
                if nxt is None or level[nxt[0]] == 3:
                    break
            pair = (*previous, command)[-2:]
            if nxt is not None and (nxt, pair) not in seen:
                seen.add((nxt, pair))
                queue.append((nxt, pair, (*program, command)))
    return None


def generate():
    levels, programs = [], []
    for index, room in enumerate(ROOMS):
        level = encode(room)
        route = solve(level)
        assert route is not None, (index + 1, room[0], "unreachable")
        program = compress(route)
        if len(program) > level[67]:
            program = solve_program(level)
        assert program is not None, (room[0], "no program within slot budget")
        print(
            index + 1,
            room[0],
            len(route),
            len(program),
            "".join(COMMANDS[c] for c in program),
            flush=True,
        )
        assert len(program) <= level[67], (room[0], "program too long", program)
        assert len(route) <= 24
        levels.append(level)
        programs.append(program)
    assert len({tuple(b) for b in levels}) == len(ROOMS)
    (ROOT / "levels.json").write_text(json.dumps(levels, indent=2) + "\n")
    (ROOT / "solutions.json").write_text(json.dumps(programs, indent=2) + "\n")


if __name__ == "__main__":
    generate()
