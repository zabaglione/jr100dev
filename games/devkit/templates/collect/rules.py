# ruff: noqa: F821
"""Collect two crystals, avoid spikes, and reach the gate within the step budget."""


def init():
    # d[0:64] is the level map; d[64] is the start; d[65] is the step budget.
    for i in range(64):
        b[i] = d[i]
    s.player = d[64]
    s.steps = d[65]
    s.gems = 0
    s.phase = 0


def act():
    target = move(s.player, s.action, 8, 8)
    if target == s.player or b[target] == 1:
        return
    s.player = target
    s.steps -= 1
    sound(0)
    if b[target] == 3:
        b[target] = 0
        s.gems += 1
        sound(1)
    if b[target] == 5:
        lose("SPIKES - WATCH YOUR ROUTE")
    elif b[target] == 6 and s.gems == 2:
        win()
    elif s.steps == 0:
        lose("OUT OF STEPS - PLAN AHEAD")


def tick():
    # Optional time-based behavior. rate in game.json is measured in 60 Hz ticks.
    s.phase = (s.phase + 1) % 2


def draw():
    grid(8, 8, 1, 3)
    tile(1 + s.player % 8 * 2, 3 + s.player // 8 * 2, 2)
    text(19, 4, "CRYSTALS")
    number(19, 6, s.gems)
    text(23, 6, "/ 002")
    text(19, 10, "STEPS")
    number(19, 12, s.steps)
    tile(19, 16, 6)
    if s.gems < 2:
        text(22, 16, "LOCKED")
    else:
        text(22, 16, "OPEN")
