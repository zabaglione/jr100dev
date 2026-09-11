# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(16):
        b[i] = (i * 5 + s.level) % 8
    s.first = 255
    s.second = 255
    s.left = 8


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5:
        if s.second != 255:
            if b[s.first] != b[s.second]:
                c[s.first] = 0
                c[s.second] = 0
            s.first = 255
            s.second = 255
        elif not c[s.cursor]:
            c[s.cursor] = 1
            if s.first == 255:
                s.first = s.cursor
            else:
                s.second = s.cursor
                if b[s.first] == b[s.second]:
                    s.left -= 1
                    sound(1)
                else:
                    s.errors += 1
                    sound(3)
                if s.left == 0:
                    win()
                elif s.errors >= 12:
                    lose()


def tick():
    pass


def draw():
    for i in range(16):
        tile(2 + i % 4 * 4, 4 + i // 4 * 4, 7 if c[i] else 4)
        if c[i]:
            letter(3 + i % 4 * 4, 4 + i // 4 * 4, 65 + b[i])
    letter(1 + s.cursor % 4 * 4, 4 + s.cursor // 4 * 4, 62)
    number(24, 7, s.left)
    number(24, 14, s.errors)
