# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    s.pos = 27
    s.origin = s.pos
    s.target = goals[s.level]
    s.fuel = 32
    s.digs = 3
    for i in range(6):
        c[17 + i] = 1 if i != s.level % 6 else 0
        c[41 + i] = 1 if i != (s.level + 3) % 6 else 0
    c[s.target] = 0
    b[s.pos] = 1


def act():
    if s.action < 5:
        s.facing = s.action
    if s.action < 5:
        target = move(s.pos, s.action, 8, 8)
        if target == s.pos or c[target]:
            sound(3)
            return
        s.origin = s.pos
        s.pos = target
        b[s.pos] = 1
        if s.origin != s.pos:
            sound(0)
            animate(2)
            s.origin = s.pos
        s.fuel -= 1
        if s.fuel == 0:
            lose("OUT OF TRAVEL SUPPLIES")
    if s.action == 5:
        s.digging = 1
        for frame in range(3):
            s.dig_frame = frame
            sound(0)
            animate(6)
        s.digging = 0
        d[s.pos] = 1
        if s.pos == s.target:
            sparkle(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
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
        tile(i % 8 * 2, 3 + i // 8 * 2, 1 if c[i] else (0 if b[i] else 4))
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
    digits(24, 13, s.fuel)
    digits(24, 17, s.digs)
    for i in range(64):
        if d[i]:
            letter(i % 8 * 2, 3 + i // 8 * 2, 79)
    if s.digging:
        letter(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 47 if s.dig_frame == 1 else 45)
    text(1, 21, "FOLLOW N/E/S/W AROUND THE ROCKS")
    effect_draw()
