# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.target = 10
    s.hp = 3
    s.direction = 1


def act():
    if s.action == 5:
        if s.swing + 1 >= s.target and s.swing <= s.target + 1:
            s.ports += 1
            s.target = 5 + (s.ports * 7) % 10
            s.swing = 0
            s.direction = 1
            sound(1)
            if s.ports == 8:
                win()
        else:
            s.hp -= 1
            sound(3)
            impact(s.swing * 2, 13)
            if s.hp == 0:
                lose()


def tick():
    if s.swing == 15:
        s.direction = 0
    if s.swing == 0:
        s.direction = 1
    s.swing = s.swing + 1 if s.direction else s.swing - 1


def draw():
    tile(14, 3, 6)
    for i in range(8):
        x = (
            15 + ((s.swing * 2 - 15) * i) // 8
            if s.swing * 2 >= 15
            else 15 - ((15 - s.swing * 2) * i) // 8
        )
        letter(x, 5 + i, 46)
    tile(s.swing * 2, 13, 2)
    tile(s.target * 2, 17, 3)
    number(9, 20, s.hp)
    number(25, 20, s.ports)
