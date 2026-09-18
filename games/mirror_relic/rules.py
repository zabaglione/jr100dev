# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    for i in range(64):
        b[i] = 1 if i % 8 == 3 or i // 8 == 3 else 0
    for i in range(4):
        b[passages[i]] = 0
    s.pos = 54
    s.origin = s.pos
    c[relics[s.level * 3]] = 1 + (s.level + 1) % 4
    c[relics[s.level * 3 + 1]] = 1 + (s.level + 2) % 4
    c[relics[s.level * 3 + 2]] = 1 + (s.level + 3) % 4
    s.left = 3
    b[53] = 6


def act():
    if s.action < 5:
        s.facing = s.action
    if s.action < 5:
        n = move(s.pos, s.action, 8, 8)
        if b[n] != 1:
            s.origin = s.pos
            s.pos = n
            if s.origin != s.pos:
                sound(0)
                animate(2)
                s.origin = s.pos
    if s.action == 5 or s.action == 7:
        n = (
            (s.pos % 8) * 8 + 7 - s.pos // 8
            if s.action == 5
            else (7 - s.pos % 8) * 8 + s.pos // 8
        )
        if b[n] != 1:
            s.rotating = 1
            sound(2)
            flight(s.pos % 8 * 2, 3 + s.pos // 8 * 2, n % 8 * 2, 3 + n // 8 * 2, 2)
            s.rotating = 0
            s.pos = n
            s.origin = s.pos
            s.turns += 1
            s.phase = (s.phase + (1 if s.action == 5 else 3)) % 4
            sound(1)
    if c[s.pos] == s.phase + 1:
        c[s.pos] = 0
        s.left -= 1
        sound(1)
        sparkle(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
    if s.pos == 53 and s.left == 0:
        win()
    elif s.turns >= 20:
        lose("TWENTY ROTATIONS USED BEFORE EXIT")


def tick():
    pass


def draw():
    face(2, s.facing)
    grid(8, 8, 0, 3)
    for i in range(64):
        if c[i]:
            tile(i % 8 * 2, 3 + i // 8 * 2, 3)
            letter(i % 8 * 2, 3 + i // 8 * 2, 64 + c[i])
    if not s.rotating:
        mover(s.pos, s.origin, 2, 0)
    digits(24, 7, s.left)
    digits(24, 14, s.turns)
    text(19, 17, "PHASE")
    letter(26, 17, 65 + s.phase)
    n = s.pos % 8 * 8 + 7 - s.pos // 8
    if b[n] != 1 and not c[n] and n != s.pos:
        letter(n % 8 * 2, 3 + n // 8 * 2, 62)
    if s.rotating:
        text(1, 20, "MIRROR TURN")
    elif s.left == 0:
        text(1, 20, "EXIT OPEN")
    effect_draw()
