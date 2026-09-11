# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.food = 10
    s.wood = 8
    s.heat = 12


def act():
    if s.action == 1 or s.action == 3:
        s.choice = (s.choice + 3) % 4
    if s.action == 2 or s.action == 4:
        s.choice = (s.choice + 1) % 4
    if s.action == 5:
        if s.choice == 0:
            s.wood = min(30, s.wood + 7)
        if s.choice == 1:
            s.food = min(30, s.food + 7)
        if s.choice == 2:
            if s.wood < 3:
                return
            s.wood -= 3
            s.heat = min(24, s.heat + 9)
        if s.choice == 3:
            if s.wood < 4 or s.insulation >= 2:
                return
            s.wood -= 4
            s.insulation += 1
        s.day += 1
        cost = 4 - s.insulation + (1 if s.day % 3 == 0 else 0)
        if s.food < 2 or s.heat <= cost:
            lose()
            return
        s.food -= 2
        s.heat -= cost
        sound(1)
        if s.day == 8:
            win()


def tick():
    pass


def draw():
    for i in range(s.heat // 2):
        tile(2 + i % 4 * 2, 16 - i // 4 * 2, 3)
    text(13, 4, "FOOD")
    number(22, 4, s.food)
    text(13, 7, "WOOD")
    number(22, 7, s.wood)
    text(13, 10, "WARMTH")
    number(22, 10, s.heat)
    text(13, 13, "INSULATE")
    number(22, 13, s.insulation)
    number(25, 18, s.day)
    letter(1 + s.choice * 8, 20, 62)
