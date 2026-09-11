# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = 1 if i % 8 == 3 or i // 8 == 3 else 0
    s.pos = 54
    c[10] = 1
    c[21] = 1
    c[42] = 1
    s.left = 3
    b[53] = 6


def act():
    if s.action < 5:
        n = move(s.pos, s.action, 8, 8)
        if b[n] != 1:
            s.pos = n
    if s.action == 5:
        n = (s.pos % 8) * 8 + 7 - s.pos // 8
        if b[n] != 1:
            s.pos = n
            s.turns += 1
            sound(1)
    if c[s.pos]:
        c[s.pos] = 0
        s.left -= 1
    if s.pos == 53 and s.left == 0:
        win()
    elif s.turns >= 20:
        lose()


def tick():
    pass


def draw():
    grid(8, 8, 0, 3)
    for i in range(64):
        if c[i]:
            tile(i % 8 * 2, 3 + i // 8 * 2, 3)
    tile(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    number(24, 7, s.left)
    number(24, 14, s.turns)
