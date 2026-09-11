# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(9):
        b[i] = 255
    s.card = (s.level + 1) % 3


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 3, 3)
    if s.action == 5 and b[s.cursor] == 255:
        b[s.cursor] = s.card
        s.placed += 1
        s.card = (s.placed * 2 + s.level + 1) % 3
        score = 0
        for i in range(3):
            if (
                b[i * 3] != 255
                and b[i * 3] == b[i * 3 + 1]
                and b[i * 3] == b[i * 3 + 2]
            ):
                score += 3
            if b[i] != 255 and b[i] == b[i + 3] and b[i] == b[i + 6]:
                score += 3
        if b[0] != 255 and b[0] == b[4] and b[0] == b[8]:
            score += 3
        if b[2] != 255 and b[2] == b[4] and b[2] == b[6]:
            score += 3
        s.score = score
        sound(1)
        if s.placed == 9:
            if score >= 6:
                win()
            else:
                lose()


def tick():
    pass


def draw():
    for i in range(9):
        tile(3 + i % 3 * 5, 5 + i // 3 * 5, 7)
        if b[i] != 255:
            letter(3 + i % 3 * 5, 5 + i // 3 * 5, 65 + b[i])
    letter(2 + s.cursor % 3 * 5, 5 + s.cursor // 3 * 5, 62)
    letter(24, 6, 65 + s.card)
    number(23, 12, s.score)
    number(23, 17, s.placed)
