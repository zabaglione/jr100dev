# ruff: noqa: F821
def spawn_preview():
    s.portal = (s.spawn % 28 * 9) % 28
    s.portal = (s.portal + s.level * 7) % 28
    if s.portal < 8:
        s.entry = s.portal
    elif s.portal < 14:
        s.entry = (s.portal - 7) * 8 + 7
    elif s.portal < 22:
        s.entry = 63 - (s.portal - 14)
    else:
        s.entry = (28 - s.portal) * 8


def init():
    s.pos = 27
    s.origin = s.pos
    s.facing = 2
    s.hp = 4
    s.limit = 12 + s.level * 2
    s.period = 4 if s.level < 3 else 3
    s.cell = 255
    for i in range(8):
        b[i] = 255
    spawn_preview()


def hurt(i):
    if c[i] > 1:
        c[i] -= 1
        impact(b[i] % 8 * 2, 3 + b[i] // 8 * 2)
        sound(2)
    else:
        vanish(b[i] % 8 * 2, 3 + b[i] // 8 * 2)
        if s.kills % 4 == 3:
            s.cell = b[i]
        b[i] = 255
        s.kills += 1
        sound(1)
    if s.kills >= s.limit:
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
        if s.pos == s.cell:
            s.cell = 255
            s.hp = min(4, s.hp + 1)
            s.cooldown = 0
            s.salvage += 1
            sparkle(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
            sound(1)
    if s.action == 5 and s.cooldown == 0:
        sound(1)
        for radius in range(3):
            s.pulse = radius + 1
            animate(3)
        s.pulse = 0
        for i in range(8):
            if s.mode == 1 and b[i] != 255 and distance(s.pos, b[i]) <= 3:
                hurt(i)
        s.cooldown = 8


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
                if (s.time + i) % 2 == 0 and p // 8 != s.pos // 8:
                    p = p + 8 if p // 8 < s.pos // 8 else p - 8
                elif p % 8 != s.pos % 8:
                    p = p + 1 if p % 8 < s.pos % 8 else p - 1
                elif p // 8 != s.pos // 8:
                    p = p + 8 if p // 8 < s.pos // 8 else p - 8
                b[i] = p
        if moving:
            s.marching = 1
            glide(3)
            s.marching = 0
        hit = 0
        for i in range(8):
            if b[i] == s.pos:
                b[i] = 255
                hit = 1
        if hit:
            s.hp -= 1
            impact(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
            sound(3)
            if s.hp == 0:
                lose("THE SWARM BROKE THROUGH")
                return
    if s.time % s.period == 0:
        placed = 0
        for i in range(8):
            if b[i] == 255 and not placed:
                b[i] = s.entry
                c[i] = 2 if (s.spawn + s.level) % 3 != 0 else 1
                d[i] = b[i]
                placed = 1
        s.spawn += 1
        spawn_preview()
    if s.time % 4 == 1:
        fired = 0
        for i in range(8):
            if s.mode == 1 and not fired and b[i] != 255 and distance(s.pos, b[i]) <= 2:
                sound(0)
                flight(
                    s.pos % 8 * 2,
                    3 + s.pos // 8 * 2,
                    b[i] % 8 * 2,
                    3 + b[i] // 8 * 2,
                    7,
                )
                hurt(i)
                fired = 1


def draw():
    face(2, s.facing)
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0)
        if s.pulse and distance(s.pos, i) == s.pulse:
            letter(i % 8 * 2, 3 + i // 8 * 2, 42)
    tile(s.entry % 8 * 2, 3 + s.entry // 8 * 2, 6)
    if s.cell != 255:
        tile(s.cell % 8 * 2, 3 + s.cell // 8 * 2, 3)
    for i in range(8):
        if b[i] != 255:
            if s.marching:
                mover(b[i], d[i], 1 if c[i] > 1 else 5, 0)
            else:
                tile(b[i] % 8 * 2, 3 + b[i] // 8 * 2, 1 if c[i] > 1 else 5)
    mover(s.pos, s.origin, 2, 0)
    digits(24, 6, s.hp)
    digits(23, 11, s.kills)
    letter(25, 11, 47)
    digits(26, 11, s.limit)
    digits(24, 16, s.cooldown)
    if s.cooldown == 0:
        text(19, 18, "PULSE READY")
    text(1, 20, "SALVAGE")
    digits(10, 20, s.salvage)
    effect_draw()
