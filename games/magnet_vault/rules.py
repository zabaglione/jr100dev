# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = d[i]
    s.pos = 27
    s.facing = 4
    c[d[64]] = 1
    c[d[65]] = 1
    s.limit = 100


def act():
    if s.action < 5:
        s.facing = s.action
        target = move(s.pos, s.action, 8, 8)
        if b[target] != 1 and c[target] == 0:
            s.pos = target
    if s.action == 5:
        front = move(s.pos, s.facing, 8, 8)
        opposite = (
            2
            if s.facing == 1
            else (1 if s.facing == 2 else (4 if s.facing == 3 else 3))
        )
        behind = move(s.pos, opposite, 8, 8)
        if c[front] and not c[behind] and b[behind] != 1:
            c[front] = 0
            c[s.pos] = 1
            s.pos = behind
            s.pulls += 1
            sound(1)
    s.moves += 1
    if c[18] and c[42]:
        win()
    elif s.moves >= s.limit:
        lose()


def tick():
    pass


def draw():
    grid(8, 8, 1, 3)
    for i in range(64):
        if c[i]:
            tile(1 + i % 8 * 2, 3 + i // 8 * 2, 4)
    tile(1 + s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    number(24, 5, s.pulls)
    number(24, 10, s.limit - s.moves)
    number(24, 15, s.facing)
