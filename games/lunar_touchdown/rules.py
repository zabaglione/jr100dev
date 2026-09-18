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
        animate(3)


def tick():
    s.time += 1
    if s.flame:
        s.flame -= 1
    if s.time % 3 == 0:
        s.speed = min(5, s.speed + 1)
    old = s.height
    s.height = min(30, s.height + s.speed)
    s.middle = (old + s.height) // 2
    s.descending = 1
    glide(2)
    s.descending = 0
    if s.height >= 30:
        s.height = 30
        if s.x >= s.target and s.x <= s.target + 3 and s.speed <= 2:
            s.landed = 1
            sound(1)
            sparkle(s.x, 18)
            animate(30)
            win()
        else:
            impact(s.x, 18)
            if s.speed > 2:
                lose("DESCENT SPEED TOO HIGH")
            else:
                lose("MISSED THE LANDING PAD")


def draw():
    height = s.middle if s.descending else s.height
    tile(s.x, 3 + height // 2, 2)
    if s.flame:
        letter(s.x, 5 + height // 2, 86 if s.flame == 1 else 42)
    text(s.target, 20, "=====")
    digits(26, 4, s.fuel)
    digits(26, 8, s.speed)
    digits(26, 12, 30 - s.height)
    if s.landed:
        text(3, 15, "TOUCHDOWN! ENGINES OFF")
    effect_draw()
