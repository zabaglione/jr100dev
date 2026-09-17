# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    s.pos = 27
    s.origin = s.pos
    s.target = (s.level * 19 + 11) % 64
    s.fuel = 32
    s.digs = 3
    b[s.pos] = 1


def act():
    if s.action < 5:
        s.facing = s.action
    if s.action < 5:
        s.origin = s.pos
        s.pos = move(s.pos, s.action, 8, 8)
        b[s.pos] = 1
        if s.origin != s.pos:
            sound(0)
            animate(2)
            s.origin = s.pos
        s.fuel -= 1
        if s.fuel == 0:
            lose("OUT OF TRAVEL SUPPLIES")
    if s.action == 5:
        if s.pos == s.target:
            sound(1)
            win()
        else:
            s.digs -= 1
            sound(3)
            if s.digs == 0:
                lose("NO DIGS REMAIN")


def tick():
    pass


def draw():
    face(2, s.facing)
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0 if b[i] else 4)
    mover(s.pos, s.origin, 2, 0)
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
