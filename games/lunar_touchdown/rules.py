# ruff: noqa: F821
def init():
    s.x = 3
    s.target = 7 + s.level * 3
    s.narrow = 24 if s.target < 18 else 5
    s.width = 3 if s.level < 3 else 2
    s.fuel = 22
    s.wind = 1 if s.level % 2 else 0


def act():
    old = s.x
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
    if old != s.x:
        sound(0)


def tick():
    s.time += 1
    if s.flame:
        s.flame -= 1
    if s.time % 3 == 0:
        s.speed = min(5, s.speed + 1)
    if s.level and s.time % 4 == 0:
        if s.wind and s.x < 28:
            s.x += 1
        elif not s.wind and s.x > 0:
            s.x -= 1
    if s.time % (16 if s.level < 3 else 12) == 0:
        s.wind ^= 1
    old = s.height
    s.height = min(30, s.height + s.speed)
    s.middle = (old + s.height) // 2
    s.descending = 1
    glide(2)
    s.descending = 0
    if s.height >= 30:
        s.height = 30
        regular = s.x >= s.target and s.x <= s.target + s.width
        precision = s.x == s.narrow
        if (regular or precision) and s.speed <= 2:
            s.landed = 1
            s.score = s.fuel + (10 if precision else 0) + (4 if s.speed <= 1 else 0)
            sound(1)
            sparkle(s.x, 18)
            animate(24)
            win()
        else:
            impact(s.x, 18)
            if s.speed > 2:
                lose("DESCENT SPEED TOO HIGH")
            else:
                lose("MISSED BOTH LANDING PADS")


def draw():
    height = s.middle if s.descending else s.height
    tile(s.x, 4 + height // 2, 2)
    if s.flame:
        letter(s.x, 6 + height // 2, 86 if s.flame == 1 else 42)
    for i in range(s.width + 2):
        letter(s.target + i, 21, 61)
    text(s.narrow, 21, "==")
    letter(s.narrow, 22, 42)
    text(0, 2, "FUEL    FALL    ALT    WIND")
    digits(5, 2, s.fuel)
    digits(13, 2, s.speed)
    digits(20, 2, 30 - s.height)
    if s.level:
        letter(29, 2, 62 if s.wind else 60)
    else:
        letter(29, 2, 45)
    if s.landed:
        text(4, 15, "TOUCHDOWN! SCORE")
        digits(21, 15, s.score)
    effect_draw()
