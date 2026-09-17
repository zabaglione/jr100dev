# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.hp = 3
    s.target = 3


def act():
    if s.action == 3 or s.action == 1:
        s.pos = (s.pos + 7) % 8
    if s.action == 4 or s.action == 2:
        s.pos = (s.pos + 1) % 8


def tick():
    s.age += 1
    if s.age == 4:
        if s.pos == s.target:
            s.hp -= 1
            sound(3)
            impact(ringx(s.pos), ringy(s.pos))
            if s.hp == 0:
                lose()
                return
        else:
            s.waves += 1
            sound(0)
        s.target = (s.target * 5 + 3) % 8
        s.age = 0
        if s.hp == 0:
            lose()
        elif s.waves >= 20:
            win()


def draw():
    for i in range(8):
        tile(ringx(i), ringy(i), 7)
    tile(ringx(s.pos), ringy(s.pos), 2)
    tile(ringx(s.target), ringy(s.target), 5 if s.age == 3 else 3)
    number(14, 8, s.hp)
    number(14, 12, s.waves)
    number(14, 16, 4 - s.age)
