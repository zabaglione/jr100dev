# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = d[i]
        c[64 + i] = i
    c[d[64]] = 1
    c[d[65]] = 1
    s.par = d[69]


def act():
    if s.action < 5:
        changed = 0
        for step in range(6):
            moved = 0
            for k in range(64):
                i = 63 - k if s.action == 2 or s.action == 4 else k
                if c[i]:
                    n = move(i, s.action, 8, 8)
                    if b[n] != 1 and not c[n]:
                        c[n] = 1
                        c[64 + n] = i
                        c[i] = 0
                        changed = 1
                        moved = 1
                        take_rune(n)
            if moved:
                sound(0)
                animate(2)
                for i in range(64):
                    c[64 + i] = i
        if changed:
            spend_move()
            sound(1)
        s.filled = 0
        for i in range(64):
            if c[i] and b[i] == 3:
                s.filled += 1
        if s.filled == 2:
            ranked_clear()


def tick():
    pass


def draw():
    x = 0
    y = 3
    for i in range(64):
        kind = b[i]
        if i == d[67] and not (s.runes & 1) or i == d[68] and not (s.runes & 2):
            kind = 6
        tile(x, y, kind)
        x += 2
        if x == 16:
            x = 0
            y += 2
    for i in range(64):
        if c[i]:
            mover(i, c[64 + i], 4, 0)
    number(22, 7, s.filled)
    tile(20, 12, 4)
    tile(25, 12, 6)
    text(19, 16, "ROLL / RUNE")
    ranked_hud()
