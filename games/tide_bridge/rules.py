# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(36):
        b[i] = 3 if (i // 6 + i % 6 + s.level) % 3 == 0 else 0
    s.pos = 30
    s.cursor = 0
    s.moves = 0


def connected():
    for i in range(36):
        c[i] = 0
    c[30] = 1
    for step in range(36):
        for i in range(36):
            if c[i]:
                for a in range(4):
                    n = move(i, a + 1, 6, 6)
                    if b[n] or n == 5:
                        c[n] = 1
    if c[5]:
        win()


def act():
    if s.action == 1:
        s.cursor = (s.cursor + 5) % 6
    if s.action == 2:
        s.cursor = (s.cursor + 1) % 6
    if s.action == 3 or s.action == 4:
        s.axis ^= 1
    if s.action == 5:
        for i in range(6):
            n = s.cursor * 6 + i if s.axis == 0 else i * 6 + s.cursor
            b[n] = 0 if b[n] else 3
        s.moves += 1
        sound(1)
        connected()
        if s.moves >= 30 and s.mode == 1:
            lose()


def tick():
    pass


def draw():
    grid(6, 6, 2, 5)
    tile(2, 15, 2)
    tile(12, 5, 6)
    number(22, 6, s.cursor + 1)
    text(20, 10, "CHANNEL")
    number(24, 11, s.axis)
    number(24, 16, s.moves)
