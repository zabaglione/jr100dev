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
        sound(0)
        flight(3 + s.cursor * 6, 3, 3 + s.cursor * 6, 15 - c[s.cursor] * 2, 4)
        b[s.cursor * 4 + c[s.cursor]] = s.weight
        c[s.cursor] += 1
        if s.cursor < 2:
            s.left += s.weight * (3 if s.cursor == 0 else 1)
        else:
            s.right += s.weight * (3 if s.cursor == 3 else 1)
        s.loads += 1
        sound(1)
        s.tilt = 1
        animate(18)
        s.tilt = 0
        if s.left > s.right + 8 or s.right > s.left + 8:
            lose("THE LOAD TIPPED THE SHIP")
        elif s.loads == 12:
            win()
        s.weight = 1 + (s.loads * 7) % 3


def tick():
    pass


def draw():
    for x in range(4):
        for y in range(c[x]):
            tile(3 + x * 6, 15 - y * 2, 4)
            letter(3 + x * 6, 15 - y * 2, 48 + b[x * 4 + y])
    letter(3 + s.cursor * 6, 7, 86)
    text(2, 19, "PORT")
    digits(7, 19, s.left)
    text(15, 19, "STARBOARD")
    digits(26, 19, s.right)
    digits(12, 4, s.weight)
    digits(26, 4, s.loads)
    text(7, 6, "NEXT")
    letter(12, 6, 49 + ((s.loads + 1) * 7) % 3)
    letter(14, 6, 49 + ((s.loads + 2) * 7) % 3)
    text(2, 21, "BALANCE    [.................]")
    delta = s.left - s.right if s.left >= s.right else s.right - s.left
    mark = 21 - min(8, delta) if s.left > s.right else 21 + min(8, delta)
    letter(mark, 21, 94)
    for column in range(30):
        y = 17
        if delta > 1:
            if column < 10:
                y = 18 if s.left > s.right else 16
            elif column > 19:
                y = 16 if s.left > s.right else 18
        letter(1 + column, y, 95)
    effect_draw()
