# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.x = 3
    s.target = 8 + s.level * 3
    s.fuel = 24


def act():
    if s.action == 3 and s.x > 0:
        s.x -= 1
    if s.action == 4 and s.x < 28:
        s.x += 1
    if (s.action == 1 or s.action == 5) and s.fuel:
        s.speed = s.speed - 2 if s.speed >= 2 else 0
        s.fuel -= 1
        s.flame = 2
        sound(0)


def tick():
    s.time += 1
    if s.flame:
        s.flame -= 1
    if s.time % 3 == 0:
        s.speed = min(5, s.speed + 1)
    s.height += s.speed
    if s.height >= 30:
        s.height = 30
        if s.x >= s.target and s.x <= s.target + 3 and s.speed <= 2:
            win()
        else:
            lose()


def draw():
    tile(s.x, 3 + s.height // 2, 2)
    if s.flame:
        letter(s.x, 5 + s.height // 2, 86)
    text(s.target, 20, "=====")
    number(26, 4, s.fuel)
    number(26, 8, s.speed)
    number(26, 12, 30 - s.height)
