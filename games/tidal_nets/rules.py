# ruff: noqa: F821
def current():
    s.tide = 1 if (s.casts + s.level) % 3 == 0 else 7
    s.force = 1 + (s.casts + s.level) % 2


def init():
    s.fish = (3 + s.level * 2) % 8
    s.deep = (1 + s.level * 3) % 8
    s.rope = 12
    s.quota = 30 + s.level * 3
    current()


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 7) % 8
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 8
    if s.action == 1 or s.action == 2:
        s.wide ^= 1
        sound(0)
    if s.action == 5:
        cost = 2 if s.wide else 1
        if s.rope < cost:
            s.notice = 7
            sound(3)
            return
        s.rope -= cost
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
        if s.cursor == landing or s.wide and (s.cursor + 1) % 8 == landing:
            gain += 2
        if s.cursor == below or s.wide and (s.cursor + 1) % 8 == below:
            gain += 4
        if gain:
            s.notice = gain
            sound(1)
            flight(s.cursor * 4, 10, 12, 19, 4)
            s.catch += gain
        else:
            sound(3)
        animate(16)
        s.casts += 1
        s.fish = (s.fish * 3 + 5 + s.level) % 8
        s.deep = (s.deep * 5 + 3 + s.level) % 8
        current()
        if s.catch >= s.quota:
            win()
        elif s.casts == 9 or s.rope == 0:
            lose("THE FISHING TRIP MISSED QUOTA")


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
        if s.wide:
            tile(((s.cursor + 1) % 8) * 4, 14, 4)
    text(1, 2, "QUOTA")
    digits(7, 2, s.quota)
    text(18, 2, "ROPE")
    digits(24, 2, s.rope)
    text(1, 4, "TIDE")
    letter(6, 4, 62 if s.tide == 1 else 60)
    letter(8, 4, 48 + s.force)
    if s.wide:
        text(19, 4, "WIDE NET")
    else:
        text(19, 4, "FINE NET")
    text(1, 6, "SHOAL +2")
    text(1, 9, "DEEP +4")
    digits(12, 19, s.catch)
    digits(28, 19, 9 - s.casts)
    if s.notice == 7:
        text(1, 20, "NOT ENOUGH ROPE")
    elif s.notice:
        text(1, 20, "CAUGHT +")
        letter(9, 20, 48 + s.notice)
    effect_draw()
