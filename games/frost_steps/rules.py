# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = 1 if d[i] == 1 else 0
        c[i] = 1 if d[i] == 3 else 0
        s.left += c[i]
    s.pos = 9


def act():
    if s.action < 5:
        for i in range(7):
            target = move(s.pos, s.action, 8, 8)
            if b[target] != 1:
                s.pos = target
                if c[target]:
                    c[target] = 0
                    s.left -= 1
                    sound(1)
        s.moves += 1
        if s.left == 0:
            win()
        elif s.moves >= 80:
            lose()


def tick():
    pass


def draw():
    grid(8, 8, 0, 3)
    for i in range(64):
        if c[i]:
            tile(i % 8 * 2, 3 + i // 8 * 2, 3)
    tile(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    number(24, 6, s.left)
    number(24, 13, s.moves)
