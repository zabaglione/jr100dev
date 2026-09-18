# ruff: noqa: F821
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
        s.notice = 0
        if s.choice == 2 and s.wood < 3:
            s.notice = 1
            sound(3)
            return
        if s.choice == 3 and (s.wood < 4 or s.insulation >= 2):
            s.notice = 2
            sound(3)
            return
        s.phase = 1
        sound(0)
        flight(
            2 + s.choice * 8,
            19,
            5,
            12,
            4
            if s.choice == 0
            else (1 if s.choice == 1 else (3 if s.choice == 2 else 6)),
        )
        if s.choice == 0:
            s.wood = min(30, s.wood + 7)
        elif s.choice == 1:
            s.food = min(30, s.food + 7)
        elif s.choice == 2:
            s.wood -= 3
            s.heat = min(24, s.heat + 9)
        else:
            s.wood -= 4
            s.insulation += 1
        sound(1)
        animate(18)
        s.phase = 2
        cost = weather[s.level * 12 + s.day] - s.insulation
        for frame in range(3):
            s.fire_frame = frame % 2
            animate(5)
        if s.food < 2:
            lose("NO FOOD LEFT FOR THE NIGHT")
            return
        s.food -= 2
        sound(0)
        animate(12)
        if s.heat <= cost:
            s.heat = 0
            lose("THE NIGHT EXTINGUISHED THE HEARTH")
            return
        s.heat -= cost
        sound(0)
        animate(12)
        s.day += 1
        s.phase = 0
        if s.day == 12:
            win()


def tick():
    pass


def draw():
    face(3, 1 + s.fire_frame)
    for i in range(s.heat // 2):
        tile(3 + i % 4 * 2, 16 - i // 4 * 2, 3)
    text(14, 4, "FOOD")
    digits(26, 4, s.food)
    text(14, 7, "WOOD")
    digits(26, 7, s.wood)
    text(14, 10, "HEAT")
    digits(26, 10, s.heat)
    text(14, 13, "WALL")
    digits(26, 13, s.insulation)
    for i in range(3):
        if s.day + i < 12:
            letter(18 + i * 4, 16, 48 + weather[s.level * 12 + s.day + i])
    digits(26, 18, s.day)
    letter(1 + s.choice * 8, 20, 62)
    if s.notice == 1:
        text(1, 21, "FIRE NEEDS THREE WOOD")
    elif s.notice == 2:
        text(1, 21, "WALL: FOUR WOOD, MAX TWO")
    elif s.phase == 1:
        text(1, 21, "WORK COMPLETE")
    elif s.phase == 2:
        text(1, 21, "NIGHTFALL")
        for x in range(5):
            letter(3 + x * 2, 6 + (x + s.fire_frame) % 3, 42)
    effect_draw()
