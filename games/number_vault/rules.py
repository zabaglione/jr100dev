# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.origin = entropy()
    s.secret = s.origin ^ (s.level * 23 + 17)
    for i in range(4):
        b[i] = 1
        d[i] = 1 + (s.secret >> (i * 2)) % 4


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 3) % 4
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 4
    s.spin = 0
    if s.action == 1:
        s.spin = 1
        sound(0)
        animate(4)
        b[s.cursor] = b[s.cursor] % 4 + 1
        s.spin = 0
    if s.action == 2:
        s.spin = 1
        sound(0)
        animate(4)
        b[s.cursor] = (b[s.cursor] + 2) % 4 + 1
        s.spin = 0
    if s.action == 5:
        s.exact = 0
        s.near = 0
        for i in range(4):
            c[i] = 0
            c[i + 4] = 0
            if b[i] == d[i]:
                s.exact += 1
                c[i] = 1
                c[i + 4] = 1
        for i in range(4):
            if not c[i]:
                for j in range(4):
                    if not c[i] and not c[j + 4] and b[i] == d[j]:
                        c[i] = 1
                        c[j + 4] = 1
                        s.near += 1
        for i in range(30):
            c[32 + i] = c[38 + i]
        for i in range(4):
            c[62 + i] = b[i]
            s.scan = i + 1
            sound(0)
            animate(5)
        c[66] = s.exact
        c[67] = s.near
        s.scan = 0
        s.tries += 1
        sound(1)
        if s.exact == 4:
            sound(1)
            for frame in range(3):
                s.opening = frame + 1
                animate(10)
            sparkle(14, 3)
            win()
        elif s.tries >= 10:
            lose("TEN CODES DID NOT OPEN THE VAULT")


def tick():
    pass


def draw():
    for i in range(4):
        x = 3 + i * 7
        text(x, 4, "___")
        letter(x, 5, 91)
        letter(x + 2, 5, 93)
        letter(x + 1, 5, 45 if s.spin and i == s.cursor else 48 + b[i])
        if s.scan == i + 1:
            letter(x, 6, 42)
    letter(3 + s.cursor * 7, 3, 86)
    text(2, 8, "LAST SIX CODES    EXACT NEAR")
    for row in range(6):
        if c[32 + row * 6]:
            for i in range(4):
                letter(3 + i * 3, 10 + row * 2, 48 + c[32 + row * 6 + i])
            letter(21, 10 + row * 2, 48 + c[36 + row * 6])
            letter(27, 10 + row * 2, 48 + c[37 + row * 6])
    text(2, 22, "TRIES LEFT")
    digits(14, 22, 10 - s.tries)
    if s.opening:
        face(6, s.opening)
        tile(14, 4, 6)
        text(11, 6, "VAULT OPEN")
    effect_draw()
