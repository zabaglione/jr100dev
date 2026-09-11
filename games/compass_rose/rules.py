# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.pos = 27
    s.target = (s.level * 19 + 11) % 64
    s.fuel = 32
    s.digs = 3
    b[s.pos] = 1


def act():
    if s.action < 5:
        s.pos = move(s.pos, s.action, 8, 8)
        b[s.pos] = 1
        s.fuel -= 1
        if s.fuel == 0:
            lose()
    if s.action == 5:
        if s.pos == s.target:
            sound(1)
            win()
        else:
            s.digs -= 1
            sound(3)
            if s.digs == 0:
                lose()


def tick():
    pass


def draw():
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0 if b[i] else 4)
    tile(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    text(20, 6, "BEARING")
    if s.target // 8 < s.pos // 8:
        letter(23, 8, 78)
    if s.target // 8 > s.pos // 8:
        letter(23, 8, 83)
    if s.target % 8 < s.pos % 8:
        letter(25, 8, 87)
    if s.target % 8 > s.pos % 8:
        letter(25, 8, 69)
    if s.pos == s.target:
        text(21, 8, "HERE")
    number(24, 13, s.fuel)
    number(24, 17, s.digs)
