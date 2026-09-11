# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def trace():
    for i in range(49):
        c[i] = 0
    p = 21
    direction = 4
    for i in range(64):
        c[p] = 1
        if s.turns:
            animate(2)
        if p == 6:
            win()
            return
        if b[p] == 1:
            direction = (
                4
                if direction == 1
                else (3 if direction == 2 else (2 if direction == 3 else 1))
            )
        elif b[p] == 2:
            direction = (
                3
                if direction == 1
                else (4 if direction == 2 else (1 if direction == 3 else 2))
            )
        n = move(p, direction, 7, 7)
        if n == p:
            return
        p = n


def init():
    b[23] = 1
    b[37] = 1
    b[40] = 2
    b[12] = 1
    b[8] = 2
    b[1] = 2
    trace()


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 7, 7)
    if s.action == 5 and b[s.cursor]:
        b[s.cursor] = 3 - b[s.cursor]
        s.turns += 1
        sound(1)
        trace()


def tick():
    pass


def draw():
    x = 2
    y = 4
    for i in range(49):
        tile(x, y, 0)
        if c[i]:
            letter(x, y, 46)
        if b[i]:
            tile(x, y, 4 if b[i] == 1 else 5)
        x += 2
        if x == 16:
            x = 2
            y += 2
    tile(14, 4, 3)
    letter(1 + s.cursor % 7 * 2, 4 + s.cursor // 7 * 2, 62)
    number(24, 9, s.turns)
