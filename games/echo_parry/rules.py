# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.hp = 3
    s.enemy = 8


def act():
    if s.action == 1:
        s.stance = 0
    if s.action == 2:
        s.stance = 1
    if s.action == 5:
        if s.phase == 1 and s.stance == s.attack and not s.guarded:
            s.enemy -= 1
            s.guarded = 1
            sound(1)
            s.counter = 1
            animate(10)
            flight(7, 14 - s.stance * 3, 24, 14 - s.attack * 3, 5)
            s.counter = 0
            if s.enemy == 0:
                vanish(24, 14 - s.attack * 3)
                win()
            else:
                impact(24, 14 - s.attack * 3)
        else:
            s.hp -= 1
            sound(3)
            impact(5, 14 - s.stance * 3)
            if s.hp == 0:
                lose("WRONG GUARD OR TIMING")


def tick():
    s.age += 1
    if s.phase == 0 and s.age >= 4:
        s.phase = 1
        s.age = 0
        sound(2)
        flight(23, 14 - s.attack * 3, 7, 14 - s.attack * 3, 5)
    elif s.phase == 1 and s.age >= 2:
        if not s.guarded:
            s.hp -= 1
            sound(3)
            impact(5, 14 - s.stance * 3)
            if s.hp == 0:
                lose("MISSED THE PARRY WINDOW")
                return
        s.phase = 2
        s.age = 0
    elif s.phase == 2 and s.age >= 3:
        s.phase = 0
        s.age = 0
        s.attack = pattern[(8 - s.enemy) % 8]
        s.guarded = 0


def draw():
    for i in range(s.enemy):
        tile(8 + i * 2, 5, 5)
    tile(5, 14 - s.stance * 3, 2)
    tile(24, 14 - s.attack * 3, 6)
    if s.phase == 0:
        text(11, 10, "READ THE TELL")
    if s.phase == 1:
        text(11, 10, "PARRY NOW")
    if s.phase == 2:
        text(11, 10, "RECOVERY")
    digits(9, 19, s.hp)
    digits(25, 19, s.enemy)
    if s.counter:
        text(11, 12, "BLOCK + RIPOSTE")
    effect_draw()
