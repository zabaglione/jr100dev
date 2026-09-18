# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def trace():
    for i in range(49):
        c[i] = 0
        d[i] = 0
    p = 21
    direction = 4
    for i in range(64):
        incoming = (
            2
            if direction == 1
            else (1 if direction == 2 else (8 if direction == 3 else 4))
        )
        if d[p] & incoming:
            return
        d[p] = d[p] | incoming
        if p == 6:
            c[p] = incoming
            if s.turns:
                animate(4)
            win()
            return
        if b[p] == 1:
            direction = (
                4
                if direction == 1
                else (3 if direction == 2 else (2 if direction == 3 else 1))
            )
        elif b[p] == 2:
            direction = (
                3
                if direction == 1
                else (4 if direction == 2 else (1 if direction == 3 else 2))
            )
        outgoing = 1 << (direction - 1)
        c[p] = c[p] | incoming | outgoing
        if s.turns:
            if b[p]:
                sound(0)
                animate(4)
            else:
                animate(1)
        n = move(p, direction, 7, 7)
        if n == p:
            return
        p = n


def init():
    b[23] = 1
    b[37] = 1
    b[40] = 2
    b[12] = 1
    b[8] = 2
    b[1] = 2
    trace()


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 7, 7)
    if s.action == 5 and b[s.cursor]:
        b[s.cursor] = 3 - b[s.cursor]
        s.turns += 1
        sound(1)
        trace()


def tick():
    pass


def draw():
    x = 2
    y = 4
    for i in range(49):
        shape = b[i] * 4
        if c[i] == 15:
            shape += 3
        elif c[i] == 3 or c[i] == 5 or c[i] == 6:
            shape += 1
        elif c[i]:
            shape += 2
        if i == 6:
            shape = 13 if c[i] else 12
        stamp(x, y, shape)
        x += 2
        if x == 16:
            x = 2
            y += 2
    stamp(0, 10, 2)
    text(0, 9, "IN")
    # Keep the cursor outside the optical cells so it never cuts the beam.
    letter(2 + s.cursor % 7 * 2, 2, 86)
    letter(17, 4 + s.cursor // 7 * 2, 60)
    number(24, 9, s.turns)
