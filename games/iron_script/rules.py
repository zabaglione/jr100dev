# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    for i in range(64):
        b[i] = d[i]
    s.pos = 9
    s.origin = s.pos
    for i in range(12):
        c[i] = 0
    s.energy = 12


def act():
    if s.action == 3 and s.cursor > 0:
        s.cursor -= 1
    if s.action == 4 and s.cursor < 11:
        s.cursor += 1
    if s.action == 1:
        c[s.cursor] = (c[s.cursor] + 1) % 5
    if s.action == 2:
        c[s.cursor] = (c[s.cursor] + 4) % 5
    if s.action == 5:
        s.pos = 9
        s.origin = s.pos
        s.energy = 12
        s.running = 1
        s.pc = 0
        s.error = 0


def tick():
    if s.running:
        if c[s.pc] > 0:
            s.facing = c[s.pc]
        target = move(s.pos, c[s.pc], 8, 8)
        if b[target] == 1:
            s.error += 1
        else:
            s.origin = s.pos
            s.pos = target
            sound(0)
            animate(2)
            s.origin = s.pos
        s.energy -= 1
        s.pc += 1
        sound(0)
        if b[s.pos] == 3:
            win()
            s.running = 0
        elif s.pc >= 12:
            s.running = 0


def draw():
    face(2, s.facing)
    grid(8, 8, 0, 3)
    mover(s.pos, s.origin, 2, 0)
    number(24, 6, s.energy)
    number(24, 10, s.error)
    for i in range(12):
        letter(19 + i % 4 * 3, 14 + i // 4 * 2, 48 + c[i])
    letter(18 + s.cursor % 4 * 3, 14 + s.cursor // 4 * 2, 62)
