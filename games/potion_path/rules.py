# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.x = 3
    s.y = 3
    s.tx = 1 + (s.level * 3 + 2) % 6
    s.ty = 1 + (s.level * 5 + 1) % 6


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
        s.x = nx
        s.y = ny
        s.doses += 1
        sound(1)
        if s.x == s.tx and s.y == s.ty:
            win()
        elif s.doses >= 12:
            lose()


def tick():
    pass


def draw():
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0)
    tile(s.tx * 2, 3 + s.ty * 2, 3)
    tile(s.x * 2, 3 + s.y * 2, 4)
    letter(18, 5 + s.ingredient * 3, 62)
    number(26, 19, s.doses)
