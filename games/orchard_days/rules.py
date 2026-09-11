# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.seeds = 8


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5:
        if b[s.cursor] == 0:
            if s.seeds == 0:
                return
            s.seeds -= 1
            b[s.cursor] = 1
        elif b[s.cursor] < 4:
            c[s.cursor] = 1
        else:
            b[s.cursor] = 0
            s.fruit += 3
            s.seeds += 2
        s.day += 1
        for i in range(16):
            if b[i] > 0 and b[i] < 4 and (c[i] or s.day % 4 == 0):
                b[i] += 1
            c[i] = 0
        sound(1)
        if s.fruit >= 18:
            win()
        elif s.day >= 28:
            lose()


def tick():
    pass


def draw():
    for i in range(16):
        tile(2 + i % 4 * 3, 4 + i // 4 * 4, 3 if b[i] == 4 else (4 if b[i] else 0))
        if b[i]:
            letter(2 + i % 4 * 3, 6 + i // 4 * 4, 48 + b[i])
    letter(1 + s.cursor % 4 * 3, 4 + s.cursor // 4 * 4, 62)
    number(24, 5, s.seeds)
    number(24, 10, s.fruit)
    number(24, 15, s.day)
