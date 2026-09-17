# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    for i in range(64):
        b[i] = d[i]
    s.pos = d[64]
    s.origin = s.pos
    s.par = d[69]


def act():
    if s.action < 5:
        s.facing = s.action
    if s.action == 5:
        s.phase ^= 1
        if s.changes < 255:
            s.changes += 1
        spend_move()
        sound(1)
    if s.action < 5:
        n = move(s.pos, s.action, 8, 8)
        if (
            n != s.pos
            and b[n] != 1
            and not (b[n] == 4 and s.phase == 0)
            and not (b[n] == 5 and s.phase == 1)
        ):
            s.origin = s.pos
            s.pos = n
            sound(0)
            animate(2)
            s.origin = s.pos
            spend_move()
            take_rune(s.pos)
    if b[s.pos] == 3:
        ranked_clear()


def tick():
    pass


def draw():
    face(2, s.facing)
    grid(8, 8, 0, 3)
    draw_runes(0)
    mover(s.pos, s.origin, 2, 0)
    text(19, 5, "BOX IS WALL")
    text(19, 9, "FOE IS WALL")
    letter(18, 5 if s.phase == 0 else 9, 62)
    number(24, 15, s.changes)
    ranked_hud()
