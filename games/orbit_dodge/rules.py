# ruff: noqa: F821
def rx(i, ring):
    x = ringx(i)
    return x if ring == 0 else (15 + (x - 15) // 2 if x >= 15 else 15 - (15 - x) // 2)


def ry(i, ring):
    y = ringy(i)
    return y if ring == 0 else (10 + (y - 10) // 2 if y >= 10 else 10 - (10 - y) // 2)


def next_wave():
    s.target = (s.target * 5 + 3 + s.level * 2) % 8
    s.ring = (s.waves + s.level) % 2
    s.other = (s.target + 3 + s.waves % 3) % 8
    s.dual = s.waves >= 4 or s.level >= 2
    s.gem = (s.target + 1 + s.waves % 2) % 8
    s.gem_ring = s.ring
    s.age = 0


def init():
    s.hp = 3
    s.target = 3
    s.limit = 12 + s.level * 2
    s.window = 5 if s.level < 3 else 4
    next_wave()


def act():
    old = s.pos
    before = s.orbit
    if s.action == 3 or s.action == 1:
        s.pos = (s.pos + 7) % 8
    if s.action == 4 or s.action == 2:
        s.pos = (s.pos + 1) % 8
    if s.action == 5:
        s.orbit ^= 1
    if s.pos != old or before != s.orbit:
        s.travel = 1
        sound(0)
        flight(
            rx(old, before), ry(old, before), rx(s.pos, s.orbit), ry(s.pos, s.orbit), 2
        )
        s.travel = 0


def tick():
    s.age += 1
    if s.age >= s.window:
        s.firing = 1
        sound(2)
        for frame in range(3):
            s.beam = 5 + frame * 5
            animate(3)
        hit = s.orbit == s.ring and s.pos == s.target
        if s.dual and s.orbit != s.ring and s.pos == s.other:
            hit = 1
        if hit:
            s.hp -= 1
            s.chain = 0
            impact(rx(s.pos, s.orbit), ry(s.pos, s.orbit))
            sound(3)
        elif s.orbit == s.gem_ring and s.pos == s.gem:
            s.chain = min(3, s.chain + 1)
            s.score += s.chain
            sparkle(rx(s.pos, s.orbit), ry(s.pos, s.orbit))
            sound(1)
        else:
            s.chain = 0
        s.firing = 0
        s.waves += 1
        if s.hp == 0:
            lose("STRUCK BY AN ORBITAL BEAM")
        elif s.waves >= s.limit:
            win()
        else:
            next_wave()


def beam(target, ring):
    tx = rx(target, ring)
    ty = ry(target, ring)
    for i in range(s.beam):
        x = 15 + (tx - 15) * i // 14 if tx >= 15 else 15 - (15 - tx) * i // 14
        y = 10 + (ty - 10) * i // 14 if ty >= 10 else 10 - (10 - ty) * i // 14
        stroke = (
            145
            if tx == 15
            else (45 if ty == 10 else (127 if (tx >= 15) == (ty >= 10) else 159))
        )
        letter(x, y, 42 if i == s.beam - 1 else stroke)


def draw():
    for i in range(8):
        tile(rx(i, 0), ry(i, 0), 7)
        tile(rx(i, 1), ry(i, 1), 7)
    tile(rx(s.gem, s.gem_ring), ry(s.gem, s.gem_ring), 3)
    tile(rx(s.target, s.ring), ry(s.target, s.ring), 5 if s.age + 1 >= s.window else 1)
    if s.dual:
        tile(
            rx(s.other, s.ring ^ 1),
            ry(s.other, s.ring ^ 1),
            5 if s.age + 1 >= s.window else 1,
        )
    if s.firing:
        beam(s.target, s.ring)
        if s.dual:
            beam(s.other, s.ring ^ 1)
    if not s.travel:
        tile(rx(s.pos, s.orbit), ry(s.pos, s.orbit), 2)
    text(0, 2, "HULL")
    letter(5, 2, 48 + s.hp)
    text(21, 2, "IMPACT")
    letter(29, 2, 48 + s.window - min(s.age, s.window))
    text(1, 20, "WAVE   /    ENERGY")
    digits(6, 20, s.waves)
    digits(9, 20, s.limit)
    digits(19, 20, s.score)
    if s.mode == 2:
        if s.score >= s.limit:
            text(1, 22, "GOLD ORBIT")
        else:
            text(1, 22, "ORBIT SECURED")
    effect_draw()
