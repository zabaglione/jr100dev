# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def ray_count(pos, direction, mark):
    p = ray(pos, direction)
    count = 0
    for i in range(7):
        if p == 255:
            return 0
        if b[p] == 0:
            return 0
        if b[p] == mark:
            return count
        count += 1
        p = ray(p, direction)
    return 0


def flips(pos, mark, apply):
    if b[pos] != 0:
        return 0
    total = 0
    for direction in range(8):
        count = ray_count(pos, direction, mark)
        total += count
        if apply:
            p = pos
            for i in range(count):
                p = ray(p, direction)
                b[p] = mark
    if apply and total:
        b[pos] = mark
    return total


def available(mark):
    for i in range(64):
        if b[i] == 0 and flips(i, mark, 0):
            return 1
    return 0


def totals():
    s.white = 0
    s.black = 0
    for i in range(64):
        if b[i] == 1:
            s.white += 1
        if b[i] == 2:
            s.black += 1


def init():
    b[27] = 2
    b[28] = 1
    b[35] = 1
    b[36] = 2
    s.cursor = 19
    totals()


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 8, 8)
    if s.action == 5:
        count = flips(s.cursor, 1, 0)
        if count == 0 and available(1):
            sound(3)
            return
        if count:
            flips(s.cursor, 1, 1)
        best = 0
        chosen = 255
        for i in range(64):
            count = flips(i, 2, 0)
            if count > best:
                best = count
                chosen = i
        if chosen != 255:
            flips(chosen, 2, 1)
        totals()
        sound(1)
        if not available(1) and not available(2):
            if s.white > s.black:
                win()
            else:
                lose()


def tick():
    pass


def draw():
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0 if b[i] == 0 else (2 if b[i] == 1 else 5))
    letter(s.cursor % 8 * 2, 3 + s.cursor // 8 * 2, 62)
    number(24, 7, s.white)
    number(24, 14, s.black)
