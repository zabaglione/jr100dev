# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(25):
        d[i] = 1 if (i * 3 + i // 5 + s.level) % 7 < 3 else 0


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 5, 5)
    if s.action == 5:
        b[s.cursor] ^= 1
        s.moves += 1
        correct = 1
        for i in range(5):
            r = 0
            want = 0
            col = 0
            goal = 0
            for j in range(5):
                r += b[i * 5 + j]
                want += d[i * 5 + j]
                col += b[j * 5 + i]
                goal += d[j * 5 + i]
            if r != want or col != goal:
                correct = 0
        if correct:
            win()
        sound(1)


def tick():
    pass


def draw():
    for i in range(25):
        tile(5 + i % 5 * 3, 5 + i // 5 * 3, 4 if b[i] else 7)
    letter(4 + s.cursor % 5 * 3, 5 + s.cursor // 5 * 3, 62)
    for i in range(5):
        r = 0
        col = 0
        for j in range(5):
            r += d[i * 5 + j]
            col += d[j * 5 + i]
        letter(2, 5 + i * 3, 48 + r)
        letter(5 + i * 3, 2, 48 + col)
    number(25, 10, s.moves)
