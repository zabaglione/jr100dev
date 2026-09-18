# ruff: noqa: F821
def init():
    s.pos = 27
    s.origin = s.pos
    s.facing = 2
    s.hp = 4
    for i in range(8):
        b[i] = 255


def hurt(i):
    if c[i] > 1:
        c[i] -= 1
        impact(b[i] % 8 * 2, 3 + b[i] // 8 * 2)
        sound(2)
    else:
        vanish(b[i] % 8 * 2, 3 + b[i] // 8 * 2)
        b[i] = 255
        s.kills += 1
        sound(1)
    if s.kills >= 18:
        win()


def act():
    if s.action < 5 or s.action >= 9:
        s.facing = (
            s.action if s.action < 5 else (3 if s.action == 9 or s.action == 11 else 4)
        )
        s.origin = s.pos
        s.pos = move8(s.pos, s.action)
        animate(2)
        s.origin = s.pos
    if s.action == 5 and s.cooldown == 0:
        sound(1)
        for radius in range(3):
            s.pulse = radius + 1
            animate(4)
        s.pulse = 0
        for i in range(8):
            if b[i] != 255 and distance(s.pos, b[i]) <= 3:
                hurt(i)
        s.cooldown = 6


def tick():
    s.time += 1
    if s.cooldown:
        s.cooldown -= 1
    if s.time % 3 == 0:
        moving = 0
        for i in range(8):
            d[i] = b[i]
            if b[i] != 255:
                moving = 1
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
        if moving:
            s.marching = 1
            glide(3)
            s.marching = 0
        for i in range(8):
            if b[i] == s.pos:
                s.hp -= 1
                impact(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
                b[i] = 255
                sound(3)
                if s.hp == 0:
                    lose("THE SWARM BROKE THROUGH")
                    return
    if s.time % 4 == 0:
        placed = 0
        for i in range(8):
            if b[i] == 255 and not placed:
                b[i] = 0 if s.time % 8 == 0 else 63
                c[i] = 2 if s.time % 12 == 0 else 1
                d[i] = b[i]
                placed = 1
    if s.time % 3 == 1:
        for i in range(8):
            if b[i] != 255 and distance(s.pos, b[i]) <= 1:
                hurt(i)


def draw():
    face(2, s.facing)
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0)
        if s.pulse and distance(s.pos, i) == s.pulse:
            letter(i % 8 * 2, 3 + i // 8 * 2, 42)
    for i in range(8):
        if b[i] != 255:
            kind = 1 if c[i] > 1 else 5
            if s.marching:
                mover(b[i], d[i], kind, 0)
            else:
                tile(b[i] % 8 * 2, 3 + b[i] // 8 * 2, kind)
    mover(s.pos, s.origin, 2, 0)
    digits(24, 6, s.hp)
    digits(24, 11, s.kills)
    digits(24, 16, s.cooldown)
    if s.cooldown == 0:
        text(19, 18, "PULSE READY")
