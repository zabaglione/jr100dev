# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.ship = 3
    s.hp = 3
    s.left = 18
    s.bullet = 255
    for i in range(24):
        b[i] = (2 if i < 8 else 1) if i % 8 < 6 else 0


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
                s.shot = 1
                s.shot_end = 3 + i // 8 * 3
                sound(0)
                for frame in range(6):
                    s.sy = 18 - (18 - s.shot_end) * frame // 5
                    animate(2)
                s.shot = 0
                b[i] -= 1
                if b[i]:
                    impact(1 + s.ship * 4, 3 + i // 8 * 3)
                else:
                    vanish(1 + s.ship * 4, 3 + i // 8 * 3)
                    s.left -= 1
                hit = 1
                sound(1)
        if not hit:
            s.shot = 1
            sound(0)
            for frame in range(6):
                s.sy = 18 - frame * 3
                animate(2)
            s.shot = 0
        s.cool = 2
        if s.left == 0:
            win()


def tick():
    s.time += 1
    if s.cool:
        s.cool -= 1
    if s.time % 8 == 0:
        s.shift = (s.shift + 1) % 8
        s.marching = 1
        glide(2)
        s.marching = 0
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
            tile(1 + (i % 8 + s.shift) % 8 * 4, 3 + i // 8 * 3, 1 if b[i] > 1 else 5)
    tile(1 + s.ship * 4, 19, 2)
    if s.bullet != 255:
        letter(1 + s.bx * 4, 3 + s.bullet * 2, 86)
    digits(8, 15, s.hp)
    digits(25, 15, s.left)
    if s.shot:
        letter(1 + s.ship * 4, s.sy, 145)
        letter(1 + s.ship * 4, s.sy + 1, 145)
