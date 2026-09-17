# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    for i in range(64):
        b[i] = 1 if d[i] == 1 else 0
        c[i] = 1 if d[i] == 3 else 0
        s.left += c[i]
    s.pos = d[64]
    s.origin = s.pos
    s.par = d[69]


def act():
    if s.action < 5:
        s.facing = s.action
    if s.action < 5:
        before = s.pos
        for i in range(7):
            target = move(s.pos, s.action, 8, 8)
            if target != s.pos and b[target] != 1:
                if s.pos == before:
                    spend_move()
                s.origin = s.pos
                s.pos = target
                take_rune(s.pos)
                if c[target]:
                    c[target] = 0
                    s.left -= 1
                    sound(1)
                else:
                    sound(0)
                animate(2)
                s.origin = s.pos
        if s.left == 0:
            ranked_clear()


def tick():
    pass


def draw():
    face(2, s.facing)
    x = 0
    y = 3
    for i in range(64):
        kind = 3 if c[i] else b[i]
        if i == d[67] and not (s.runes & 1) or i == d[68] and not (s.runes & 2):
            kind = 6
        tile(x, y, kind)
        x += 2
        if x == 16:
            x = 0
            y += 2
    mover(s.pos, s.origin, 2, 0)
    tile(20, 7, 3)
    number(24, 7, s.left)
    text(19, 9, "COLLECT ALL")
    text(19, 11, "ICE RUNES")
    tile(22, 13, 6)
    text(19, 16, "OPTIONAL")
    ranked_hud()
