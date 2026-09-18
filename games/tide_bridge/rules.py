# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(36):
        b[i] = 3 if (i // 6 + i % 6 + s.level) % 3 == 0 else 0
    s.pos = 30
    s.origin = 30
    s.facing = 2
    s.cursor = 0
    s.moves = 0


def connected():
    for i in range(36):
        c[i] = 0
        c[64 + i] = 255
        d[i] = 0
    c[30] = 1
    d[0] = 30
    tail = 1
    for head in range(36):
        if head < tail:
            p = d[head]
            for a in range(4):
                n = move(p, a + 1, 6, 6)
                if c[n] == 0 and (b[n] or n == 5):
                    c[n] = 1
                    c[64 + n] = p
                    d[tail] = n
                    tail += 1
    if c[5]:
        target = 5
        length = 0
        for i in range(36):
            if target != 30:
                d[length] = target
                length += 1
                target = c[64 + target]
        s.walking = 1
        animate(8)
        for i in range(36):
            if length:
                length -= 1
                target = d[length]
                s.facing = 1 if target < s.pos else 2
                if target // 6 == s.pos // 6:
                    s.facing = 3 if target < s.pos else 4
                s.origin = s.pos
                s.pos = target
                s.half = 1
                sound(0)
                animate(3)
                s.half = 0
                animate(3)
        s.arrived = 1
        for cheer in range(2):
            s.facing = 5
            s.hop = 1
            sound(1)
            animate(8)
            s.facing = 6
            s.hop = 0
            animate(8)
        s.facing = 5
        animate(6)
        win()


def act():
    if s.action == 1:
        s.cursor = (s.cursor + 5) % 6
    if s.action == 2:
        s.cursor = (s.cursor + 1) % 6
    if s.action == 3 or s.action == 4:
        s.axis ^= 1
    if s.action == 5:
        for i in range(6):
            n = s.cursor * 6 + i if s.axis == 0 else i * 6 + s.cursor
            b[n] = 0 if b[n] else 3
        s.moves += 1
        sound(1)
        connected()
        if s.moves >= 30 and s.mode == 1:
            lose()


def tick():
    pass


def draw():
    x = 2
    y = 5
    for i in range(36):
        kind = b[i]
        if (
            s.walking == 0
            and s.mode == 1
            and (
                (s.axis == 0 and i // 6 == s.cursor)
                or (s.axis == 1 and i % 6 == s.cursor)
            )
        ):
            kind = 4 if b[i] else 1
        tile(x, y, kind)
        x += 2
        if x == 14:
            x = 2
            y += 2
    tile(12, 5, 6)
    face(2, s.facing)
    if s.half:
        tile(2 + s.pos % 6 + s.origin % 6, 5 + s.pos // 6 + s.origin // 6, 2)
    else:
        tile(2 + s.pos % 6 * 2, 5 + s.pos // 6 * 2 - s.hop, 2)
    if s.walking == 0:
        text(20, 5, "SELECT")
        if s.axis == 0:
            text(20, 6, "ROW")
        else:
            text(20, 6, "COL")
        number(24, 6, s.cursor + 1)
        text(20, 10, "W/S SELECT")
        text(20, 11, "A/D AXIS")
        text(20, 13, "RET SWITCH")
        if s.axis == 0:
            letter(1, 5 + s.cursor * 2, 62)
            letter(14, 5 + s.cursor * 2, 60)
        else:
            letter(2 + s.cursor * 2, 4, 86)
            letter(2 + s.cursor * 2, 17, 94)
    elif s.arrived:
        text(20, 5, "ARRIVED!")
        text(20, 10, "HOORAY!")
    else:
        text(20, 5, "CROSSING")
        text(20, 10, "TO THE GATE")
    number(24, 16, s.moves)
