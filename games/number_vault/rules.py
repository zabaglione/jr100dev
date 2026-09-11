# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(4):
        b[i] = 1
        d[i] = 1 + ((s.level * 23 + 17) >> (i * 2)) % 4


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
        s.exact = 0
        s.near = 0
        for i in range(4):
            c[i] = 0
            c[i + 4] = 0
            if b[i] == d[i]:
                s.exact += 1
                c[i] = 1
                c[i + 4] = 1
        for i in range(4):
            if not c[i]:
                for j in range(4):
                    if not c[i] and not c[j + 4] and b[i] == d[j]:
                        c[i] = 1
                        c[j + 4] = 1
                        s.near += 1
        s.tries += 1
        sound(1)
        if s.exact == 4:
            win()
        elif s.tries >= 10:
            lose()


def tick():
    pass


def draw():
    for i in range(4):
        tile(3 + i * 7, 7, 7)
        letter(3 + i * 7, 7, 48 + b[i])
    letter(3 + s.cursor * 7, 5, 86)
    number(7, 14, s.exact)
    number(23, 14, s.near)
    number(23, 19, 10 - s.tries)
