# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = d[i]
    s.pos = 9


def act():
    if s.action == 5:
        s.phase ^= 1
        s.changes += 1
        sound(1)
    if s.action < 5:
        n = move(s.pos, s.action, 8, 8)
        if (
            b[n] != 1
            and not (b[n] == 4 and s.phase == 0)
            and not (b[n] == 5 and s.phase == 1)
        ):
            s.pos = n
            s.moves += 1
    if b[s.pos] == 3:
        win()
    elif s.changes >= 12:
        lose()


def tick():
    pass


def draw():
    grid(8, 8, 0, 3)
    tile(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    text(19, 5, "BOX IS WALL")
    text(19, 9, "FOE IS WALL")
    letter(18, 5 if s.phase == 0 else 9, 62)
    number(24, 15, s.changes)
