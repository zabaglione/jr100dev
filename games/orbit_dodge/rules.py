# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.hp = 3
    s.target = 3


def act():
    old = s.pos
    if s.action == 3 or s.action == 1:
        s.pos = (s.pos + 7) % 8
    if s.action == 4 or s.action == 2:
        s.pos = (s.pos + 1) % 8
    if s.pos != old:
        s.travel = 1
        sound(0)
        flight(ringx(old), ringy(old), ringx(s.pos), ringy(s.pos), 2)
        s.travel = 0


def tick():
    s.age += 1
    if s.age == 4:
        s.firing = 1
        sound(2)
        for frame in range(3):
            s.beam = 5 + frame * 5
            animate(4)
        s.firing = 0
        if s.pos == s.target or (
            s.waves >= 6 and s.pos == (s.target + 3 + s.waves % 3) % 8
        ):
            s.hp -= 1
            sound(3)
            impact(ringx(s.pos), ringy(s.pos))
            if s.hp == 0:
                lose("STRUCK BY AN ORBITAL BEAM")
                return
        else:
            s.waves += 1
            sound(0)
        s.target = (s.target * 5 + 3) % 8
        s.age = 0
        if s.hp == 0:
            lose()
        elif s.waves >= 20:
            win()


def draw():
    for i in range(8):
        tile(ringx(i), ringy(i), 7)
    if not s.travel:
        tile(ringx(s.pos), ringy(s.pos), 2)
    tile(ringx(s.target), ringy(s.target), 5 if s.age == 3 else 3)
    digits(14, 8, s.hp)
    digits(14, 12, s.waves)
    digits(14, 16, 4 - min(s.age, 4))
    if s.waves >= 6:
        other = (s.target + 3 + s.waves % 3) % 8
        tile(ringx(other), ringy(other), 5 if s.age == 3 else 3)
        if s.firing:
            beam(other)
    if s.firing:
        beam(s.target)
    effect_draw()


def beam(target):
    tx = ringx(target)
    ty = ringy(target)
    for i in range(s.beam):
        x = 15 + (tx - 15) * i // 14 if tx >= 15 else 15 - (15 - tx) * i // 14
        y = 10 + (ty - 10) * i // 14 if ty >= 10 else 10 - (10 - ty) * i // 14
        letter(
            x,
            y,
            145
            if target == 0 or target == 4
            else (
                45
                if target == 2 or target == 6
                else (127 if target == 1 or target == 5 else 159)
            ),
        )
