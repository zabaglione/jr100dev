# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.facing = 2
    box()
    s.pos = 9
    s.origin = s.pos
    s.guard = 49 + s.level
    s.guard_origin = s.guard
    s.guard_facing = 4
    s.direction = 4
    s.battery = 42 - s.level * 2
    s.cache = 33 + s.level % 6
    for i in range(6):
        b[24 + i + 1] = 1 if i != (1 + s.level * 2) % 6 else 0
    for i in range(6):
        b[40 + i + 1] = 1 if i != (4 + s.level) % 6 else 0
    b[14] = 3
    b[54] = 6


def act():
    if s.action < 5:
        s.facing = s.action
    if s.action == 5:
        s.quiet ^= 1
        return
    if s.action < 5:
        n = move(s.pos, s.action, 8, 8)
        if b[n] == 1:
            return
        s.origin = s.pos
        s.pos = n
        cost = 2 if s.quiet else 1
        if s.battery <= cost:
            s.origin = s.pos
            lose("BATTERY EXHAUSTED")
            return
        s.battery -= cost
        if s.pos == 14 and not s.key:
            s.key = 1
            sound(1)
            sparkle(12, 5)
            sparkle(12, 15)
        if s.pos == s.cache:
            s.cache = 255
            s.intel = 1
            s.battery = min(50, s.battery + 6)
            sound(1)
            sparkle(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
        if s.pos == 54 and s.key:
            s.origin = s.pos
            win()
            return
        s.alert = distance(s.pos, s.guard) < (2 if s.quiet else 5)
        sound(0)
        animate(2)
        s.origin = s.pos
        if s.alert:
            a = (
                1
                if s.guard // 8 > s.pos // 8
                else (
                    2
                    if s.guard // 8 < s.pos // 8
                    else (3 if s.guard % 8 > s.pos % 8 else 4)
                )
            )
            s.guard_facing = a
            n = move(s.guard, a, 8, 8)
        else:
            if s.guard == 49:
                s.direction = 4
            if s.guard == 54:
                s.direction = 3
            s.guard_facing = s.direction
            n = move(s.guard, s.direction, 8, 8)
        if b[n] != 1:
            s.guard_origin = s.guard
            s.guard = n
            sound(0)
            animate(2)
            s.guard_origin = s.guard
        if s.pos == s.guard:
            impact(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
            lose("CAUGHT BY THE GUARD")
        sound(0)


def tick():
    pass


def draw():
    face(2, s.facing)
    face(5, s.guard_facing)
    x = 0
    y = 3
    for i in range(64):
        kind = 0 if i == 14 and s.key else b[i]
        tile(x, y, kind)
        x += 2
        if x == 16:
            x = 0
            y += 2
    if s.cache != 255:
        tile(s.cache % 8 * 2, 3 + s.cache // 8 * 2, 4)
    mover(s.guard, s.guard_origin, 5, 0)
    mover(s.pos, s.origin, 2, 0)
    digits(24, 5, s.battery)
    if s.quiet:
        text(20, 10, "SILENT")
    else:
        text(20, 10, "NORMAL")
    if s.key:
        text(20, 15, "TAKEN")
    else:
        text(20, 15, "GET FILE")
    if s.mode == 2:
        if s.intel:
            text(19, 18, "ALL INTEL")
        else:
            text(19, 18, "ESCAPED")
    elif s.alert:
        text(19, 18, "DETECTED")
        letter(s.guard % 8 * 2 + 1, 3 + s.guard // 8 * 2, 33)
    if s.action < 5 and s.action > 0 and s.mode == 1:
        radius = 1 if s.quiet else 4
        for pos in range(64):
            if b[pos] == 0 and pos != s.pos and distance(pos, s.pos) == radius:
                letter(pos % 8 * 2, 3 + pos // 8 * 2, 46)
    text(1, 20, "NOISE REACH")
    letter(13, 20, 50 if s.quiet else 53)
    text(18, 20, "INTEL")
    letter(25, 20, 48 + s.intel)
    effect_draw()
