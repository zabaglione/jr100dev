# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(9):
        b[i] = 255
    s.card = (s.level + 1) % 3


def line(a, middle, end):
    if b[a] != 255 and b[a] == b[middle] and b[a] == b[end]:
        c[a] = 1
        c[middle] = 1
        c[end] = 1
        return 3
    return 0


def evaluate():
    score = 0
    for i in range(9):
        d[i] = c[i]
        c[i] = 0
    for i in range(3):
        score += line(i * 3, i * 3 + 1, i * 3 + 2)
        score += line(i, i + 3, i + 6)
    score += line(0, 4, 8)
    score += line(2, 4, 6)
    s.gain = score - s.score
    s.score = score
    for i in range(9):
        d[i] = 1 if c[i] and d[i] == 0 else 0


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 3, 3)
        s.gain = 0
    if s.action == 5 and b[s.cursor] == 255:
        s.gain = 0
        s.flying = 1
        target_x = 3 + s.cursor % 3 * 6
        target_y = 6 + s.cursor // 3 * 5
        sound(0)
        for step in range(5):
            s.fx = 24 - (24 - target_x) * step // 4
            s.fy = 5 + (target_y - 5) * step // 4
            animate(4)
        s.flying = 0
        b[s.cursor] = s.card
        s.placed += 1
        sound(1)
        evaluate()
        animate(12)
        if s.gain:
            sound(1)
            for glow in range(3):
                s.glow = glow + 1
                animate(8)
            s.glow = 0
            animate(24)
        s.card = (s.placed * 2 + s.level + 1) % 3
        if s.placed == 9:
            if s.score >= 6:
                win()
            else:
                lose("SCORE BELOW SIX")


def tick():
    pass


def card(x, y, i):
    if b[i] == 255:
        letter(x + 2, y + 2, 43)
    else:
        letter(x + 1, y + 1, 65 + b[i])
        tile(x + 2, y + 2, 3 if s.glow and d[i] else b[i])
    if c[i]:
        letter(x + 3, y, 42)


def small_number(x, y, value):
    if value >= 10:
        letter(x, y, 48 + value // 10)
    letter(x + 1, y, 48 + value % 10)


def draw():
    if s.glow:
        face(3, s.glow)
    for i in range(9):
        card(1 + i % 3 * 6, 4 + i // 3 * 5, i)
    if s.mode == 1 and s.flying == 0 and s.glow == 0:
        letter(s.cursor % 3 * 6, 6 + s.cursor // 3 * 5, 62)
        letter(6 + s.cursor % 3 * 6, 6 + s.cursor // 3 * 5, 60)
    if s.flying:
        text(22, 3, "IN FLIGHT")
        tile(s.fx, s.fy, s.card)
    elif s.placed < 9:
        tile(24, 5, s.card)
        letter(25, 8, 65 + s.card)
    else:
        text(23, 6, "EMPTY")
    small_number(24, 12, s.score)
    small_number(24, 18, s.placed)
    for i in range(6):
        letter(23 + i, 14, 35 if i < s.score else 46)
    if s.gain:
        text(2, 21, "RESONANCE +")
        small_number(13, 21, s.gain)
    else:
        text(2, 21, "A:STAR B:RING C:MOON")
