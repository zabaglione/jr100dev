# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(64):
        b[i] = d[i]
    s.pos = d[64]
    s.origin = s.pos
    s.facing = 4
    c[d[65]] = 1
    c[d[66]] = 1
    s.par = d[69]


def act():
    before = s.pos
    facing = s.facing
    if s.action < 5:
        s.facing = s.action
        target = move(s.pos, s.action, 8, 8)
        if b[target] != 1 and c[target] == 0:
            s.pos = target
    if s.action == 5:
        front = move(s.pos, s.facing, 8, 8)
        opposite = (
            2
            if s.facing == 1
            else (1 if s.facing == 2 else (4 if s.facing == 3 else 3))
        )
        behind = move(s.pos, opposite, 8, 8)
        if c[front] and not c[behind] and b[behind] != 1:
            c[front] = 0
            c[s.pos] = 1
            s.pulling = 1
            s.block_origin = front
            s.pos = behind
            if s.pulls < 255:
                s.pulls += 1
            sound(1)
    if s.pos != before:
        s.origin = before
        if not s.pulling:
            sound(0)
        animate(2)
        s.origin = s.pos
        s.pulling = 0
    if s.pos != before or s.facing != facing:
        spend_move()
        take_rune(s.pos)
    filled = 0
    for i in range(64):
        if b[i] == 3 and c[i]:
            filled += 1
    if filled == 2:
        ranked_clear()


def tick():
    pass


def draw():
    face(2, s.facing)
    grid(8, 8, 1, 3)
    draw_runes(1)
    for i in range(64):
        if c[i]:
            if s.pulling and i == s.origin:
                mover(i, s.block_origin, 4, 1)
            else:
                tile(1 + i % 8 * 2, 3 + i // 8 * 2, 4)
    mover(s.pos, s.origin, 2, 1)
    number(24, 5, s.pulls)
    letter(
        23,
        10,
        78
        if s.facing == 1
        else (83 if s.facing == 2 else (87 if s.facing == 3 else 69)),
    )
    tile(23, 13, 6)
    text(20, 16, "RUNES")
    ranked_hud()
