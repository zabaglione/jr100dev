# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.x = 3
    s.y = 3
    s.tx = orders[s.level * 2]
    s.ty = orders[s.level * 2 + 1]


def act():
    if s.action == 3 or s.action == 1:
        s.ingredient = (s.ingredient + 3) % 4
    if s.action == 4 or s.action == 2:
        s.ingredient = (s.ingredient + 1) % 4
    if s.action == 5:
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
        tile(i % 8 * 2, 3 + i // 8 * 2, 0)
    tile(s.tx * 2, 3 + s.ty * 2, 3)
    if not s.pouring:
        tile(s.x * 2, 3 + s.y * 2, 4)
    letter(18, 5 + s.ingredient * 3, 62)
    digits(26, 19, s.doses)
    effect_draw()
