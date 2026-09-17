# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def food():
    for k in range(64):
        p = (s.eaten * 13 + k * 7 + 26) % 64
        found = 0
        for j in range(s.length):
            if b[j] == p:
                found = 1
        if not found:
            s.food = p
            return


def init():
    s.length = 3
    b[0] = 8
    b[1] = 0
    b[2] = 1
    s.dir = 2
    food()


def act():
    if s.action < 5:
        opposite = 2 if s.dir == 1 else (1 if s.dir == 2 else (4 if s.dir == 3 else 3))
        if s.action != opposite:
            s.dir = s.action


def tick():
    p = move(b[0], s.dir, 8, 8)
    if p == b[0]:
        lose()
        return
    eating = p == s.food
    for i in range(s.length - 1 + eating):
        if b[i] == p:
            lose()
            return
    for k in range(s.length):
        i = s.length - k
        b[i] = b[i - 1]
    b[0] = p
    if eating:
        s.length += 1
        s.eaten += 1
        food()
        sound(1)
        if s.eaten == 12:
            win()


def draw():
    face(2, s.dir)
    for i in range(64):
        tile(1 + i % 8 * 2, 3 + i // 8 * 2, 0)
    for i in range(s.length):
        tile(1 + b[i] % 8 * 2, 3 + b[i] // 8 * 2, 4 if i else 2)
    tile(1 + s.food % 8 * 2, 3 + s.food // 8 * 2, 3)
    number(24, 7, s.length)
    number(24, 14, s.eaten)
