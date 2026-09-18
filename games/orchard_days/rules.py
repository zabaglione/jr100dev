# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.seeds = 8


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5:
        s.notice = 0
        x = 2 + s.cursor % 4 * 3
        y = 4 + s.cursor // 4 * 4
        if b[s.cursor] == 0:
            if s.seeds == 0:
                return
            sound(0)
            flight(24, 5, x, y, 1)
            s.seeds -= 1
            b[s.cursor] = 1
        elif b[s.cursor] < 4:
            s.notice = 1
            sound(0)
            flight(x, 2, x, y, 5)
            c[s.cursor] = 1
        else:
            b[s.cursor] = 0
            s.notice = 2
            sound(1)
            flight(x, y, 24, 10, 3)
            s.fruit += 3
            s.seeds += 2
        s.day += 1
        for i in range(16):
            if b[i] > 0 and b[i] < 4 and (c[i] or s.day % 4 == 0):
                b[i] += 1
                s.growing = i + 1
                sound(0)
                animate(4)
            c[i] = 0
        sound(1)
        s.growing = 0
        if s.fruit >= 18:
            win()
        elif s.day >= 28:
            lose("DAY 28 ENDED BELOW 18 FRUIT")


def tick():
    pass


def draw():
    for i in range(16):
        tile(
            2 + i % 4 * 3,
            4 + i // 4 * 4,
            3 if b[i] == 4 else (4 if b[i] == 3 else b[i]),
        )
        if b[i]:
            letter(2 + i % 4 * 3, 6 + i // 4 * 4, 48 + b[i])
    letter(1 + s.cursor % 4 * 3, 4 + s.cursor // 4 * 4, 62)
    digits(24, 5, s.seeds)
    digits(24, 10, s.fruit)
    digits(24, 15, s.day)
    text(19, 18, "RAIN IN")
    letter(28, 18, 48 + 4 - s.day % 4)
    if s.growing:
        letter(2 + (s.growing - 1) % 4 * 3, 4 + (s.growing - 1) // 4 * 4, 42)
    if s.notice == 1:
        text(1, 21, "WATER GIVEN - WATCH IT GROW")
    elif s.notice == 2:
        text(1, 21, "HARVEST: +3 FRUIT  +2 SEEDS")
    effect_draw()
