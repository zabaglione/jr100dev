# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = d[i]
    c[d[64]] = 1
    c[d[65]] = 1


def act():
    if s.action < 5:
        for step in range(6):
            for k in range(64):
                i = 63 - k if s.action == 2 or s.action == 4 else k
                if c[i]:
                    n = move(i, s.action, 8, 8)
                    if b[n] != 1 and not c[n]:
                        c[n] = 1
                        c[i] = 0
        s.moves += 1
        sound(1)
        filled = 0
        for i in range(64):
            if c[i] and b[i] == 3:
                filled += 1
        if filled == 2:
            win()
        elif s.moves >= 30:
            lose()


def tick():
    pass


def draw():
    grid(8, 8, 0, 3)
    for i in range(64):
        if c[i]:
            tile(i % 8 * 2, 3 + i // 8 * 2, 4)
    number(24, 7, s.moves)
    number(24, 14, 30 - s.moves)
