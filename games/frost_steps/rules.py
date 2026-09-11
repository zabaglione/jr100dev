# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = 1 if d[i] == 1 else 0
        c[i] = 1 if d[i] == 3 else 0
        s.left += c[i]
    s.pos = d[64]
    s.par = d[69]


def act():
    if s.action < 5:
        before = s.pos
        for i in range(7):
            target = move(s.pos, s.action, 8, 8)
            if b[target] != 1:
                s.pos = target
                take_rune(s.pos)
                if c[target]:
                    c[target] = 0
                    s.left -= 1
                    sound(1)
        if s.pos != before:
            spend_move()
        if s.left == 0:
            ranked_clear()


def tick():
    pass


def draw():
    grid(8, 8, 0, 3)
    for i in range(64):
        if c[i]:
            tile(i % 8 * 2, 3 + i // 8 * 2, 3)
    draw_runes(0)
    tile(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    number(23, 7, s.left)
    text(19, 11, "ICE RUNES")
    tile(22, 13, 6)
    text(19, 16, "OPTIONAL")
    ranked_hud()
