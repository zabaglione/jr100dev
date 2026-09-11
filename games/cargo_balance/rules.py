# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.weight = 1


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 3) % 4
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 4
    if s.action == 5 and c[s.cursor] < 4:
        b[s.cursor * 4 + c[s.cursor]] = s.weight
        c[s.cursor] += 1
        if s.cursor < 2:
            s.left += s.weight * (3 if s.cursor == 0 else 1)
        else:
            s.right += s.weight * (3 if s.cursor == 3 else 1)
        s.loads += 1
        sound(1)
        if s.left > s.right + 8 or s.right > s.left + 8:
            lose()
        elif s.loads == 12:
            win()
        s.weight = 1 + (s.loads * 7) % 3


def tick():
    pass


def draw():
    for x in range(4):
        for y in range(c[x]):
            tile(3 + x * 6, 15 - y * 3, 4)
            letter(3 + x * 6, 15 - y * 3, 48 + b[x * 4 + y])
    letter(3 + s.cursor * 6, 2, 86)
    text(2, 19, "PORT")
    number(7, 19, s.left)
    text(15, 19, "STARBOARD")
    number(26, 19, s.right)
    number(12, 4, s.weight)
    number(26, 4, s.loads)
