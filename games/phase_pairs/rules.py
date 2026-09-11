# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(16):
        b[i] = d[i]
    s.left = 16
    s.first = 255


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5 and b[s.cursor]:
        if s.first == 255:
            s.first = s.cursor
        else:
            valid = 0
            for a in range(4):
                if move(s.first, a + 1, 4, 4) == s.cursor:
                    valid = 1
            if valid and b[s.first] + b[s.cursor] == 10:
                b[s.first] = 0
                b[s.cursor] = 0
                s.left -= 2
                sound(1)
            else:
                s.errors += 1
                sound(3)
            s.first = 255
            if s.left == 0:
                win()
            elif s.errors >= 6:
                lose()


def tick():
    pass


def draw():
    for i in range(16):
        tile(2 + i % 4 * 4, 4 + i // 4 * 4, 7)
        if b[i]:
            letter(3 + i % 4 * 4, 4 + i // 4 * 4, 48 + b[i])
    letter(1 + s.cursor % 4 * 4, 4 + s.cursor // 4 * 4, 62)
    number(24, 7, s.left)
    number(24, 14, s.errors)
