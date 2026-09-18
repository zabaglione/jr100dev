# ruff: noqa: F821
def init():
    s.fish = 3
    s.deep = 1
    current()


def current():
    s.tide = 1 if s.casts % 3 == 0 else 7
    s.force = 1 + s.casts % 2


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 7) % 8
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 8
    if s.action == 5:
        s.notice = 0
        s.casting = 1
        sound(0)
        flight(s.cursor * 4, 14, s.cursor * 4, 10, 4)
        s.casting = 0
        landing = (s.fish + s.tide * s.force) % 8
        below = (s.deep + s.tide * s.force * 2) % 8
        s.swimming = 1
        flight(s.fish * 4, 7, landing * 4, 7, 3)
        s.fish = landing
        s.swimming = 2
        flight(s.deep * 4, 10, below * 4, 10, 3)
        s.deep = below
        s.swimming = 0
        gain = 0
        if s.cursor == landing or (s.cursor + 1) % 8 == landing:
            gain += 2
        if s.cursor == below or (s.cursor + 1) % 8 == below:
            gain += 3
        if gain:
            s.notice = gain
            sound(1)
            flight(s.cursor * 4, 10, 12, 19, 4)
            s.catch += gain
        else:
            sound(3)
        animate(20)
        s.casts += 1
        s.fish = (s.fish * 3 + 5) % 8
        s.deep = (s.deep * 5 + 3) % 8
        current()
        if s.catch >= 30:
            win()
        elif s.casts == 9:
            lose("NINE CASTS ENDED BELOW 30 FISH")


def tick():
    pass


def draw():
    for x in range(8):
        tile(x * 4, 12, 0)
        letter(x * 4, 17, 49 + x)
    if s.swimming != 1:
        tile(s.fish * 4, 7, 3)
    if s.swimming != 2:
        tile(s.deep * 4, 10, 3)
    if not s.casting:
        tile(s.cursor * 4, 14, 4)
    letter(((s.cursor + 1) % 8) * 4, 15, 94)
    text(1, 4, "TIDE")
    letter(6, 4, 62 if s.tide == 1 else 60)
    letter(8, 4, 48 + s.force)
    text(1, 6, "SHOAL +2")
    text(1, 9, "DEEP +3")
    digits(12, 19, s.catch)
    digits(28, 19, 9 - s.casts)
    if s.notice:
        text(19, 2, "CAUGHT +")
        letter(27, 2, 48 + s.notice)
    effect_draw()
