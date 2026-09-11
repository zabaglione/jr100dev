# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def gate(a, b, kind):
    if kind == 0:
        return a & b
    if kind == 1:
        return a | b
    return a ^ b


def output(a, b, p, q, r):
    first = gate(a, b, p)
    second = gate(first, a, q)
    return gate(second, b, r)


def init():
    for i in range(4):
        d[i] = output(i // 2, i % 2, s.level % 3, (s.level // 3) % 3, (s.level + 1) % 3)


def act():
    if s.action == 1:
        s.cursor = (s.cursor + 2) % 3
    if s.action == 2:
        s.cursor = (s.cursor + 1) % 3
    if s.action == 3:
        c[s.cursor] = (c[s.cursor] + 2) % 3
    if s.action == 4:
        c[s.cursor] = (c[s.cursor] + 1) % 3
    if s.action == 5:
        correct = 0
        for i in range(4):
            b[i] = output(i // 2, i % 2, c[0], c[1], c[2])
            if b[i] == d[i]:
                correct += 1
        s.tests += 1
        sound(1)
        if correct == 4:
            win()


def tick():
    pass


def draw():
    for i in range(3):
        tile(5, 5 + i * 4, 6)
        letter(9, 5 + i * 4, 65 + c[i])
    letter(3, 5 + s.cursor * 4, 62)
    for i in range(4):
        letter(19, 6 + i * 3, 48 + i // 2)
        letter(21, 6 + i * 3, 48 + i % 2)
        letter(25, 6 + i * 3, 48 + d[i])
        letter(29, 6 + i * 3, 48 + b[i])
    number(26, 19, s.tests)
