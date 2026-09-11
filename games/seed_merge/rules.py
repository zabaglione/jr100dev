# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def index(line, offset, action):
    if action == 1:
        return offset * 4 + line
    if action == 2:
        return (3 - offset) * 4 + line
    if action == 3:
        return line * 4 + offset
    return line * 4 + 3 - offset


def spawn():
    s.seed = (s.seed * 5 + 1) & 255
    for i in range(16):
        p = (s.seed + i) % 16
        if b[p] == 0:
            b[p] = 1
            return


def init():
    s.seed = 7
    spawn()
    spawn()
    s.best = 1


def act():
    if s.action >= 5:
        return
    changed = 0
    for line in range(4):
        for i in range(4):
            c[i] = 0
        count = 0
        for i in range(4):
            value = b[index(line, i, s.action)]
            if value:
                c[count] = value
                count += 1
        for i in range(3):
            if c[i] and c[i] == c[i + 1]:
                c[i] += 1
                c[i + 1] = 0
                if c[i] > s.best:
                    s.best = c[i]
        count = 0
        for i in range(4):
            if c[i]:
                c[count] = c[i]
                if count != i:
                    c[i] = 0
                count += 1
        for i in range(4):
            p = index(line, i, s.action)
            if b[p] != c[i]:
                changed = 1
            b[p] = c[i]
    if changed:
        spawn()
        s.moves += 1
        sound(1)
    possible = 0
    for i in range(16):
        if b[i] == 0:
            possible = 1
        for a in range(4):
            n = move(i, a + 1, 4, 4)
            if n != i and b[i] == b[n]:
                possible = 1
    if s.best >= 6:
        win()
    elif not possible:
        lose()


def tick():
    pass


def draw():
    for i in range(16):
        tile(1 + i % 4 * 5, 4 + i // 4 * 4, 7)
        if b[i]:
            number(1 + i % 4 * 5, 5 + i // 4 * 4, 1 << b[i])
    number(26, 7, 1 << s.best)
    number(26, 14, s.moves)
