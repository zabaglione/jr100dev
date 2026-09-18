# ruff: noqa: F821
def init():
    s.culprit = who[s.level]
    for i in range(6):
        b[i] = suspects[s.level * 6 + i]


def act():
    if s.action == 1 or s.action == 2:
        s.mode_choice ^= 1
        sound(0)
    if s.action == 3 or s.action == 4:
        if s.mode_choice:
            s.choice = (s.choice + (5 if s.action == 3 else 1)) % 6
        else:
            s.file = (s.file + (2 if s.action == 3 else 1)) % 3
    if s.action == 5:
        if s.mode_choice:
            s.accusing = 1
            sound(0)
            animate(24)
            if s.choice == s.culprit:
                sparkle(2 + s.choice % 3 * 5, 4 + s.choice // 3 * 6)
                win()
            else:
                lose("THE SUSPECT DOES NOT FIT THE FILES")
        else:
            if c[s.file]:
                sound(0)
                return
            s.opening = 1
            for frame in range(3):
                s.page = frame
                sound(0)
                animate(6)
            c[s.file] = 1
            s.read += 1
            s.opening = 0
            sound(1)


def tick():
    pass


def draw():
    for i in range(6):
        x = 2 + i % 3 * 5
        y = 4 + i // 3 * 6
        letter(x, y, 160 + (b[i] - 1) * 2)
        letter(x, y + 1, 161 + (b[i] - 1) * 2)
        letter(x, y + 2, 65 + i)
        for trait in range(3):
            letter(x - 1 + trait, y + 3, 89 if b[i] & (1 << trait) else 78)
        wrong = 0
        for trait in range(3):
            if c[trait] and (b[i] & (1 << trait)) != (b[s.culprit] & (1 << trait)):
                wrong = 1
        if wrong:
            letter(x + 1, y + 2, 88)
    if s.mode_choice:
        letter(1 + s.choice % 3 * 5, 4 + s.choice // 3 * 6, 62)
    else:
        letter(17, 6 + s.file * 4, 62)
    text(19, 3, "CASE FILES")
    text(18, 6, "1 HAT")
    text(18, 10, "2 GLASSES")
    text(18, 14, "3 TIE")
    for trait in range(3):
        if c[trait]:
            if b[s.culprit] & (1 << trait):
                text(20, 7 + trait * 4, "YES")
            else:
                text(20, 7 + trait * 4, "NO")
    text(1, 18, "FILES READ")
    letter(12, 18, 48 + s.read)
    if s.mode_choice:
        text(2, 20, "ACCUSE")
        letter(10, 20, 65 + s.choice)
    else:
        text(2, 20, "OPEN FILE")
        letter(12, 20, 49 + s.file)
    if s.opening:
        text(19, 18 - s.page, "__________")
    if s.mode == 2:
        if s.read <= 2:
            text(13, 20, "GOLD DETECTIVE")
        else:
            text(13, 20, "CASE CLOSED")
    if s.accusing:
        letter(4 + s.choice % 3 * 5, 4 + s.choice // 3 * 6, 33)
    effect_draw()
