# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.dest = 2
    s.hp = 3


def act():
    if s.action == 1 or s.action == 2:
        s.cursor ^= 1
    if s.action == 3 or s.action == 4 or s.action == 5:
        c[s.cursor] ^= 1
        sound(0)


def tick():
    s.age += 1
    if s.age == 3:
        s.route = 0 if c[0] == 0 else (1 if c[1] == 0 else 2)
    if s.age == 9:
        if s.route == s.dest:
            s.delivered += 1
            sound(1)
        else:
            s.hp -= 1
            sound(3)
        s.dest = (s.dest + s.delivered + 1) % 3
        c[s.delivered % 2] ^= 1
        s.age = 0
        if s.hp == 0:
            lose()
        elif s.delivered == 12:
            win()


def draw():
    for i in range(3):
        text(9, 5 + i * 5, "--------------------")
        letter(29, 5 + i * 5, 65 + i)
    tile(6, 5, 6)
    tile(6, 10, 6)
    letter(4, 5 + s.cursor * 5, 62)
    number(2, 5, c[0])
    number(2, 10, c[1])
    tile(8 + s.age * 2, 5 + s.route * 5, 2)
    letter(15, 19, 65 + s.dest)
    number(26, 19, s.delivered)
