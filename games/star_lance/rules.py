# ruff: noqa: F821
def init():
    s.ship = 3
    s.hp = 3
    s.left = 18
    s.direction = 1
    for i in range(3):
        c[i] = 255
    for i in range(24):
        b[i] = (2 if i < 8 or s.level >= 3 and i < 16 else 1) if i % 8 < 6 else 0


def act():
    before = s.ship
    if s.action == 3 and s.ship > 0:
        s.ship -= 1
    if s.action == 4 and s.ship < 7:
        s.ship += 1
    if before != s.ship:
        s.moving = 1
        cruise(1 + before * 4, 19, 1 + s.ship * 4, 19, 2)
        s.moving = 0
    if (s.action == 5 or s.action == 1) and s.cool == 0:
        heat = 4 if s.action == 1 else 2
        if s.heat + heat > 8:
            s.notice = 1
            sound(3)
            return
        s.notice = 0
        s.heat += heat
        hit = 0
        s.shot = 1
        s.power = 2 if s.action == 1 else 1
        s.shot_end = 2
        for k in range(24):
            i = 23 - k
            if not hit and b[i] and (i % 8 + s.shift) % 8 == s.ship:
                s.shot_end = 3 + i // 8 * 3
                hit = i + 1
        sound(2 if s.power == 2 else 0)
        for frame in range(6):
            s.sy = 18 - (18 - s.shot_end) * frame // 5
            animate(2)
        s.shot = 0
        if hit:
            i = hit - 1
            b[i] = b[i] - s.power if b[i] > s.power else 0
            if b[i]:
                impact(1 + s.ship * 4, 3 + i // 8 * 3)
            else:
                vanish(1 + s.ship * 4, 3 + i // 8 * 3)
                s.left -= 1
            sound(1)
        s.cool = 2 if s.power == 1 else 3
        if s.left == 0:
            win()


def tick():
    s.time += 1
    if s.cool:
        s.cool -= 1
    if s.heat and s.time % 2 == 0:
        s.heat -= 1
    if s.time % (8 if s.level < 3 else 6) == 0:
        if s.time % 32 == 0:
            s.direction ^= 1
        s.shift = (s.shift + (1 if s.direction else 7)) % 8
        s.marching = 1
        glide(2)
        s.marching = 0
    if s.time % (10 if s.level < 2 else 7) == 0:
        placed = 0
        for i in range(1 + min(s.level, 2)):
            if c[i] == 255 and not placed:
                c[i] = 0
                d[i] = s.ship if s.level >= 2 else (s.time // 10 * 3) % 8
                placed = 1
    hit = 0
    for i in range(3):
        if c[i] != 255:
            c[i] += 1
            if c[i] == 8:
                if d[i] == s.ship:
                    hit = 1
                c[i] = 255
    if hit:
        s.hp -= 1
        impact(1 + s.ship * 4, 19)
        sound(3)
    if s.hp == 0:
        lose("HIT BY ENEMY SHOT")
    elif s.time == 240:
        lose("THE FORMATION ESCAPED")


def draw():
    for i in range(24):
        if b[i]:
            tile(1 + (i % 8 + s.shift) % 8 * 4, 3 + i // 8 * 3, 1 if b[i] > 1 else 5)
    if not s.moving:
        tile(1 + s.ship * 4, 19, 2)
    for i in range(3):
        if c[i] != 255:
            letter(1 + d[i] * 4, 3 + c[i] * 2, 86)
    digits(8, 15, s.hp)
    digits(25, 15, s.left)
    text(1, 17, "HEAT [........]")
    for i in range(s.heat):
        letter(7 + i, 17, 42)
    if s.notice:
        text(17, 17, "TOO HOT")
    if s.shot:
        letter(1 + s.ship * 4, s.sy, 145)
        letter(1 + s.ship * 4, s.sy + 1, 145)
        if s.power == 2:
            letter(2 + s.ship * 4, s.sy, 145)
    effect_draw()
