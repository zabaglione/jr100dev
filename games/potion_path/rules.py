# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.x = 3
    s.y = 3
    s.tx = orders[s.level * 2]
    s.ty = orders[s.level * 2 + 1]
    for i in range(7):
        if hazards[s.level * 7 + i] != 255:
            b[hazards[s.level * 7 + i]] = 1
    for i in range(4):
        c[i] = 4


def act():
    if s.action == 3 or s.action == 1:
        s.ingredient = (s.ingredient + 3) % 4
    if s.action == 4 or s.action == 2:
        s.ingredient = (s.ingredient + 1) % 4
    if s.action == 5:
        if not c[s.ingredient]:
            s.notice = 1
            sound(3)
            return
        s.notice = 0
        nx = s.x
        ny = s.y
        if s.ingredient == 0:
            if nx < 2:
                return
            nx -= 2
        if s.ingredient == 1:
            if nx >= 7 or ny >= 6:
                return
            nx += 1
            ny += 2
        if s.ingredient == 2:
            if ny == 0:
                return
            ny -= 1
        if s.ingredient == 3:
            if nx >= 5 or ny >= 7:
                return
            nx += 3
            ny += 1
        if b[ny * 8 + nx]:
            s.notice = 2
            sound(3)
            return
        c[s.ingredient] -= 1
        s.pouring = 1
        sound(0)
        flight(21, 5 + s.ingredient * 3, s.x * 2, 3 + s.y * 2, 4)
        flight(s.x * 2, 3 + s.y * 2, nx * 2, 3 + ny * 2, 4)
        s.pouring = 0
        s.x = nx
        s.y = ny
        s.doses += 1
        sound(1)
        if s.x == s.tx and s.y == s.ty:
            sparkle(s.tx * 2, 3 + s.ty * 2)
            win()
        elif s.doses >= 12:
            lose("TWELVE DOSES MISSED THE RECIPE")


def tick():
    pass


def draw():
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 1 if b[i] else 0)
    tile(s.tx * 2, 3 + s.ty * 2, 3)
    if not s.pouring:
        tile(s.x * 2, 3 + s.y * 2, 4)
    letter(18, 5 + s.ingredient * 3, 62)
    digits(26, 19, s.doses)
    for i in range(4):
        letter(29, 6 + i * 3, 48 + c[i])
    text(1, 20, "PAR")
    digits(5, 20, pars[s.level])
    if s.notice == 1:
        text(9, 20, "INGREDIENT EMPTY")
    elif s.notice == 2:
        text(9, 20, "POISON LANDING")
    effect_draw()
