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
            for a in range(4):
                neighbor = move(s.first, a + 1, 4, 4)
                if neighbor != s.first and b[neighbor] + b[s.first] == 10:
                    c[neighbor] = 1
            face(7, 5)
            sound(0)
        else:
            valid = 0
            for a in range(4):
                if s.first != s.cursor and move(s.first, a + 1, 4, 4) == s.cursor:
                    valid = 1
            if valid and b[s.first] + b[s.cursor] == 10:
                s.ax = 2 + s.first % 4 * 4
                s.ay = 4 + s.first // 4 * 4
                s.bx = 2 + s.cursor % 4 * 4
                s.by = 4 + s.cursor // 4 * 4
                s.cx = (s.ax + s.bx) // 2
                s.cy = (s.ay + s.by) // 2
                s.merging = 1
                sound(0)
                if s.ax < s.cx:
                    s.ax += 1
                if s.ax > s.cx:
                    s.ax -= 1
                if s.ay < s.cy:
                    s.ay += 1
                if s.ay > s.cy:
                    s.ay -= 1
                if s.bx < s.cx:
                    s.bx += 1
                if s.bx > s.cx:
                    s.bx -= 1
                if s.by < s.cy:
                    s.by += 1
                if s.by > s.cy:
                    s.by -= 1
                animate(4)
                s.merging = 2
                sound(1)
                animate(9)
                for phase in range(4):
                    s.merging = phase + 3
                    face(7, phase + 1)
                    animate(4)
                b[s.first] = 0
                b[s.cursor] = 0
                s.left -= 2
                s.merging = 0
            else:
                s.errors += 1
                s.reject = 1 if valid == 0 else 2
                sound(3)
                animate(18)
                s.reject = 0
            s.first = 255
            for i in range(16):
                c[i] = 0
            if s.left == 0:
                win()
            elif s.errors >= 6:
                lose()


def tick():
    pass


def big(x, y, value):
    letter(x, y, 160 + value * 2)
    letter(x, y + 1, 161 + value * 2)


def card(x, y, value, chosen, hint):
    if hint:
        letter(x, y, 188)
        letter(x + 2, y, 189)
        letter(x, y + 2, 190)
        letter(x + 2, y + 2, 191)
    else:
        letter(x, y, 180)
        letter(x + 2, y, 182)
        letter(x, y + 2, 185)
        letter(x + 2, y + 2, 186)
    letter(x + 1, y, 187 if chosen else 181)
    letter(x, y + 1, 183)
    letter(x + 2, y + 1, 184)
    big(x + 1, y + 1, value)


def ten(x, y):
    letter(x, y, 180)
    letter(x + 1, y, 187)
    letter(x + 2, y, 187)
    letter(x + 3, y, 182)
    letter(x, y + 1, 183)
    letter(x + 3, y + 1, 184)
    letter(x, y + 2, 185)
    letter(x + 3, y + 2, 186)
    big(x + 1, y + 1, 1)
    big(x + 2, y + 1, 0)


def draw():
    for i in range(16):
        if b[i] and (s.merging == 0 or i != s.first and i != s.cursor):
            card(
                2 + i % 4 * 4,
                4 + i // 4 * 4,
                b[i],
                i == s.first,
                c[i] and s.merging == 0,
            )
    if s.merging == 1:
        card(s.ax, s.ay, b[s.first], 1, 0)
        card(s.bx, s.by, b[s.cursor], 1, 0)
    if s.merging >= 2 and s.merging < 5:
        ten(s.cx, s.cy)
    if s.merging >= 3:
        letter(s.cx - 1, s.cy - 1, 188)
        letter(s.cx + 4, s.cy - 1, 189)
        letter(s.cx - 1, s.cy + 3, 190)
        letter(s.cx + 4, s.cy + 3, 191)
    if s.merging == 0:
        letter(1 + s.cursor % 4 * 4, 5 + s.cursor // 4 * 4, 62)
    if s.first != 255:
        big(23, 10, b[s.first])
        if s.cursor != s.first and b[s.cursor]:
            big(27, 10, b[s.cursor])
        else:
            text(27, 11, "?")
    else:
        text(23, 11, "?")
        text(27, 11, "?")
    big(23, 17, s.left // 10)
    big(24, 17, s.left % 10)
    big(28, 17, s.errors)
    if s.reject == 1:
        text(2, 21, "NEIGHBORS ONLY")
    elif s.reject == 2:
        text(2, 21, "SUM MUST BE 10")
    elif s.merging:
        text(2, 21, "PHASE FUSION!")
    for i in range(8):
        letter(2 + i * 2, 20, 110 if i < (16 - s.left) // 2 else 46)
