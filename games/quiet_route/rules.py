# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    box()
    s.pos = 9
    s.guard = 49
    s.direction = 4
    s.battery = 50
    for i in range(6):
        b[24 + i + 1] = 1 if i != 1 else 0
    for i in range(6):
        b[40 + i + 1] = 1 if i != 4 else 0
    b[14] = 3
    b[54] = 6


def act():
    if s.action == 5:
        s.quiet ^= 1
        return
    if s.action < 5:
        n = move(s.pos, s.action, 8, 8)
        if b[n] == 1:
            return
        s.pos = n
        cost = 2 if s.quiet else 1
        if s.battery <= cost:
            lose()
            return
        s.battery -= cost
        if s.pos == 14:
            s.key = 1
        if s.pos == 54 and s.key:
            win()
            return
        s.alert = distance(s.pos, s.guard) < (2 if s.quiet else 5)
        animate(5)
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
            n = move(s.guard, a, 8, 8)
        else:
            if s.guard == 49:
                s.direction = 4
            if s.guard == 54:
                s.direction = 3
            n = move(s.guard, s.direction, 8, 8)
        if b[n] != 1:
            s.guard = n
        if s.pos == s.guard:
            lose()
        sound(0)


def tick():
    pass


def draw():
    x = 0
    y = 3
    for i in range(64):
        kind = 0 if i == 14 and s.key else b[i]
        if i == s.guard:
            kind = 5
        if i == s.pos:
            kind = 2
        tile(x, y, kind)
        x += 2
        if x == 16:
            x = 0
            y += 2
    number(24, 5, s.battery)
    number(24, 10, s.quiet)
    number(24, 15, s.key)
    if s.alert:
        text(19, 18, "DETECTED")
