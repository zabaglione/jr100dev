# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(4):
        d[i] = 1 + (s.level + i) % 4
        b[i] = 1


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 3) % 4
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 4
    if s.action == 1:
        b[s.cursor] = b[s.cursor] % 4 + 1
    if s.action == 2:
        b[s.cursor] = (b[s.cursor] + 2) % 4 + 1
    if s.action == 5:
        correct = 1
        for i in range(4):
            if b[i] != d[i]:
                correct = 0
        if correct:
            win()
        else:
            s.errors += 1
            sound(3)
            if s.errors == 5:
                lose()


def tick():
    pass


def draw():
    for i in range(3):
        letter(3, 5 + i * 4, 65 + i)
        letter(5, 5 + i * 4, 43)
        letter(7, 5 + i * 4, 66 + i)
        letter(9, 5 + i * 4, 61)
        number(11, 5 + i * 4, d[i] + d[i + 1])
    text(3, 17, "A =")
    number(9, 17, d[0])
    for i in range(4):
        letter(21, 4 + i * 4, 65 + i)
        letter(25, 4 + i * 4, 48 + b[i])
    letter(19, 4 + s.cursor * 4, 62)
