# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.fish = 3
    s.tide = 1


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 7) % 8
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 8
    if s.action == 5:
        landing = (s.fish + s.tide) % 8
        if s.cursor == landing:
            s.catch += 2
            sound(1)
        else:
            sound(3)
        s.casts += 1
        s.fish = (s.fish * 3 + 5) % 8
        s.tide = 1 if s.casts % 3 == 0 else 7
        if s.catch >= 16:
            win()
        elif s.casts == 12:
            lose()


def tick():
    pass


def draw():
    for x in range(8):
        tile(x * 4, 10, 0)
        letter(x * 4, 17, 48 + x)
    tile(s.fish * 4, 7, 3)
    tile(s.cursor * 4, 14, 4)
    text(1, 4, "CURRENT")
    letter(10, 4, 62 if s.tide == 1 else 60)
    number(13, 19, s.catch)
    number(27, 19, 12 - s.casts)
