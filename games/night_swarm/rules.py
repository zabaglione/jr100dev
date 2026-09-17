# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.pos = 27
    s.hp = 4
    for i in range(8):
        b[i] = 255
    s.seed = 23


def act():
    if s.action < 5 or s.action >= 9:
        s.pos = move8(s.pos, s.action)
    if s.action == 5 and s.cooldown == 0:
        for i in range(8):
            if b[i] != 255 and distance(s.pos, b[i]) <= 3:
                vanish(b[i] % 8 * 2, 3 + b[i] // 8 * 2)
                b[i] = 255
                s.kills += 1
        s.cooldown = 6
        sound(1)
        if s.kills >= 18:
            win()


def tick():
    s.time += 1
    if s.cooldown:
        s.cooldown -= 1
    if s.time % 3 == 0:
        for i in range(8):
            if b[i] != 255:
                p = b[i]
                if p % 8 < s.pos % 8:
                    p += 1
                elif p % 8 > s.pos % 8:
                    p -= 1
                elif p // 8 < s.pos // 8:
                    p += 8
                elif p // 8 > s.pos // 8:
                    p -= 8
                b[i] = p
                if p == s.pos:
                    s.hp -= 1
                    impact(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
                    b[i] = 255
                    sound(3)
                    if s.hp == 0:
                        lose()
                        return
    if s.time % 4 == 0:
        placed = 0
        for i in range(8):
            if b[i] == 255 and not placed:
                b[i] = 0 if s.time % 8 == 0 else 63
                placed = 1
    if s.time % 3 == 1:
        for i in range(8):
            if b[i] != 255 and distance(s.pos, b[i]) <= 1:
                vanish(b[i] % 8 * 2, 3 + b[i] // 8 * 2)
                b[i] = 255
                s.kills += 1
                sound(0)
                if s.kills >= 18:
                    win()


def draw():
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0)
    for i in range(8):
        if b[i] != 255:
            tile(b[i] % 8 * 2, 3 + b[i] // 8 * 2, 5)
    tile(s.pos % 8 * 2, 3 + s.pos // 8 * 2, 2)
    number(24, 6, s.hp)
    number(24, 11, s.kills)
    number(24, 16, s.cooldown)
