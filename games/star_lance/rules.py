# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.ship = 3
    s.hp = 3
    s.left = 18
    s.bullet = 255
    for i in range(24):
        b[i] = 1 if i % 8 < 6 else 0


def act():
    if s.action == 3:
        s.ship = (s.ship + 7) % 8
    if s.action == 4:
        s.ship = (s.ship + 1) % 8
    if s.action == 5 and s.cool == 0:
        hit = 0
        for k in range(24):
            i = 23 - k
            if not hit and b[i] and (i % 8 + s.shift) % 8 == s.ship:
                vanish(1 + (i % 8 + s.shift) % 8 * 4, 3 + i // 8 * 3)
                b[i] = 0
                s.left -= 1
                hit = 1
                sound(1)
        s.cool = 2
        if s.left == 0:
            win()


def tick():
    s.time += 1
    if s.cool:
        s.cool -= 1
    if s.time % 8 == 0:
        s.shift = (s.shift + 1) % 8
    if s.time % 10 == 0 and s.bullet == 255:
        s.bullet = 0
        s.bx = (s.time // 10 * 3) % 8
    if s.bullet != 255:
        s.bullet += 1
        if s.bullet == 8:
            if s.bx == s.ship:
                s.hp -= 1
                impact(1 + s.ship * 4, 19)
                sound(3)
            s.bullet = 255
    if s.hp == 0:
        lose("HIT BY ENEMY SHOT")
    elif s.time == 220:
        lose("TIME EXPIRED")


def draw():
    for i in range(24):
        if b[i]:
            tile(1 + (i % 8 + s.shift) % 8 * 4, 3 + i // 8 * 3, 5)
    tile(1 + s.ship * 4, 19, 2)
    if s.bullet != 255:
        letter(1 + s.bx * 4, 3 + s.bullet * 2, 86)
    number(8, 15, s.hp)
    number(25, 15, s.left)
