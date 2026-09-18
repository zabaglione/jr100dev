# ruff: noqa: F821
def deck_height(column):
    port = s.left + s.wind
    delta = port - s.right if port >= s.right else s.right - port
    if delta <= 1 or s.tilt == 1 or column == 1 or column == 2:
        return 17
    if column == 0:
        return 18 if port > s.right else 16
    return 16 if port > s.right else 18


def init():
    s.weight = cargo[s.level * 12]
    s.wind = s.level % 3
    s.tolerance = 10 - s.level // 2


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 3) % 4
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 4
    if s.action == 5 and c[s.cursor] >= 4:
        s.notice = 1
        sound(3)
    if s.action == 5 and c[s.cursor] < 4:
        s.notice = 0
        sound(0)
        flight(
            3 + s.cursor * 6,
            3,
            3 + s.cursor * 6,
            deck_height(s.cursor) - 2 - c[s.cursor] * 2,
            4,
        )
        b[s.cursor * 4 + c[s.cursor]] = s.weight
        c[s.cursor] += 1
        if s.cursor < 2:
            s.left += s.weight * (3 if s.cursor == 0 else 1)
        else:
            s.right += s.weight * (3 if s.cursor == 3 else 1)
        s.loads += 1
        s.fare += s.weight * (2 if s.cursor == 0 or s.cursor == 3 else 1)
        sound(1)
        for frame in range(3):
            s.tilt = 1 if frame == 1 else 0
            animate(6)
        s.tilt = 0
        if (
            s.left + s.wind > s.right + s.tolerance
            or s.right > s.left + s.wind + s.tolerance
        ):
            lose("THE LOAD TIPPED THE SHIP")
        elif s.loads == 12:
            win()
        if s.loads < 12:
            s.weight = cargo[s.level * 12 + s.loads]


def tick():
    pass


def draw():
    for x in range(4):
        for y in range(c[x]):
            tile(3 + x * 6, deck_height(x) - 2 - y * 2, 4)
            letter(3 + x * 6, deck_height(x) - 2 - y * 2, 48 + b[x * 4 + y])
    letter(3 + s.cursor * 6, 7, 86)
    text(2, 19, "PORT")
    digits(7, 19, s.left)
    text(15, 19, "STARBOARD")
    digits(26, 19, s.right)
    digits(12, 4, s.weight)
    digits(26, 4, s.loads)
    text(7, 6, "NEXT")
    letter(12, 6, 48 + cargo[s.level * 12 + min(11, s.loads + 1)])
    letter(14, 6, 48 + cargo[s.level * 12 + min(11, s.loads + 2)])
    text(2, 21, "BALANCE    [.................]")
    delta = (
        s.left + s.wind - s.right
        if s.left + s.wind >= s.right
        else s.right - s.left - s.wind
    )
    mark = 21 - min(8, delta) if s.left + s.wind > s.right else 21 + min(8, delta)
    letter(mark, 21, 94)
    for column in range(30):
        letter(
            1 + column, deck_height(0 if column < 10 else (3 if column > 19 else 1)), 95
        )
    text(1, 2, "FARE")
    digits(6, 2, s.fare)
    text(13, 2, "WIND")
    letter(18, 2, 48 + s.wind)
    text(21, 2, "LIMIT")
    digits(27, 2, s.tolerance)
    if s.notice:
        text(10, 7, "HOLD FULL")
    effect_draw()
