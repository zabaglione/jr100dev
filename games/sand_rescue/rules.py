# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    box()
    for i in range(6):
        b[24 + i + 1] = 1
    b[26] = 1
    b[28] = 1
    b[30] = 1
    b[50] = 3
    b[52] = 3
    b[54] = 3
    s.gate = 1


def act():
    if s.action == 3:
        s.gate = (s.gate + 2) % 3
    if s.action == 4:
        s.gate = (s.gate + 1) % 3
    if s.action == 5:
        p = 26 + s.gate * 2
        for i in range(3):
            b[26 + i * 2] = 1
        b[p] = 0
        sound(0)


def tick():
    for i in range(64):
        d[i] = 0
    for k in range(64):
        i = 63 - k
        if c[i]:
            if b[i] == 3:
                s.water += 1
                if i == 50:
                    s.crop0 += 1
                if i == 52:
                    s.crop1 += 1
                if i == 54:
                    s.crop2 += 1
                sound(1)
            else:
                p = move(i, 2, 8, 8)
                if b[p] == 1 or d[p]:
                    p = move(i, 3 if s.time % 2 else 4, 8, 8)
                if b[p] == 1 or d[p]:
                    p = i
                d[p] = 1
    for i in range(64):
        c[i] = d[i]
    s.time += 1
    if s.time % 3 == 0:
        source = 10 + (s.released // 4) % 3 * 2
        if c[source]:
            s.spill += 1
        else:
            c[source] = 1
            s.released += 1
    if s.crop0 >= 4 and s.crop1 >= 4 and s.crop2 >= 4:
        win()
    elif s.spill >= 6 or s.released >= 30:
        lose()


def draw():
    grid(8, 8, 0, 3)
    for i in range(64):
        if c[i]:
            tile(i % 8 * 2, 3 + i // 8 * 2, 4)
    letter(4 + s.gate * 4, 8, 86)
    number(23, 5, s.crop0)
    number(23, 7, s.crop1)
    number(23, 9, s.crop2)
    number(24, 11, s.spill)
    number(24, 16, s.released)
