# ruff: noqa: F821
def init():
    s.seeds = 8
    s.water = 6
    s.quota = 18 + s.level * 6
    s.period = 4 + s.level


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 5)
    if s.action != 5:
        return
    s.notice = 0
    if s.cursor >= 16:
        if s.cursor < 18:
            s.crop = s.cursor - 16
            sound(0)
            return
        if s.cursor == 18:
            s.notice = 3
        else:
            if s.water >= 9:
                return
            s.water = min(9, s.water + 3)
            s.notice = 4
            sound(0)
    else:
        x = 2 + s.cursor % 4 * 3
        y = 4 + s.cursor // 4 * 3
        need = 5 if c[s.cursor] else 3
        if b[s.cursor] == 0:
            if s.seeds == 0:
                s.notice = 5
                sound(3)
                return
            sound(0)
            flight(24, 5, x, y, 1)
            s.seeds -= 1
            b[s.cursor] = 1
            c[s.cursor] = s.crop
        elif b[s.cursor] < need:
            if s.water == 0:
                s.notice = 6
                sound(3)
                return
            s.water -= 1
            s.notice = 1
            sound(0)
            flight(x, 2, x, y, 5)
            d[s.cursor] = 1
        else:
            b[s.cursor] = 0
            s.notice = 2
            s.gain = 7 if c[s.cursor] else 3
            sound(1)
            flight(x, y, 24, 10, 3)
            s.fruit += s.gain
            s.seeds += 1
    s.day += 1
    s.rain = s.day % s.period == 0
    if s.rain:
        s.water = min(9, s.water + 4)
        sound(2)
        animate(12)
    for i in range(16):
        need = 5 if c[i] else 3
        if b[i] and b[i] < need and (d[i] or s.rain):
            b[i] += 1
            s.growing = i + 1
            sound(0)
            animate(4)
        d[i] = 0
    s.growing = 0
    s.rain = 0
    if s.fruit >= s.quota:
        win()
    elif s.day >= 28:
        lose("THE SEASON ENDED BELOW QUOTA")


def tick():
    pass


def draw():
    for i in range(16):
        need = 5 if c[i] else 3
        tile(
            2 + i % 4 * 3,
            4 + i // 4 * 3,
            3 if b[i] >= need else (4 if b[i] >= 3 else b[i]),
        )
        if b[i]:
            letter(2 + i % 4 * 3, 6 + i // 4 * 3, 65 if c[i] else 66)
            letter(3 + i % 4 * 3, 6 + i // 4 * 3, 48 + need - b[i])
    if s.cursor < 16:
        letter(1 + s.cursor % 4 * 3, 4 + s.cursor // 4 * 3, 62)
    else:
        letter((s.cursor - 16) * 8, 18, 62)
    text(1, 17, "BERRY   APPLE   WAIT    WELL")
    letter(1 + s.crop * 8, 18, 94)
    text(19, 3, "SEEDS")
    digits(26, 4, s.seeds)
    text(19, 6, "WATER")
    digits(26, 7, s.water)
    text(19, 9, "FRUIT")
    digits(21, 10, s.fruit)
    letter(23, 10, 47)
    digits(24, 10, s.quota)
    text(19, 12, "RAIN IN")
    letter(28, 13, 48 + s.period - s.day % s.period)
    text(1, 20, "DAY   /28")
    digits(5, 20, s.day)
    if s.notice == 2:
        text(13, 20, "HARVEST +")
        letter(23, 20, 48 + s.gain)
    elif s.notice == 5:
        text(13, 20, "NO SEEDS")
    elif s.notice == 6:
        text(13, 20, "WELL IS EMPTY")
    if s.growing:
        letter(2 + (s.growing - 1) % 4 * 3, 4 + (s.growing - 1) // 4 * 3, 42)
    if s.rain:
        for x in range(7):
            letter(1 + x * 2, 3, 127)
    effect_draw()
