# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.lane = 1
    s.obstacle = 1
    s.hp = 3


def act():
    if s.action == 3 and s.lane > 0:
        s.lane -= 1
    if s.action == 4 and s.lane < 2:
        s.lane += 1
    if s.action == 5 or s.action == 1:
        s.jump = 3


def tick():
    if s.jump:
        s.jump -= 1
    s.age += 1
    if s.age == 6:
        if s.lane == s.obstacle and (s.kind == 0 or s.jump == 0):
            s.hp -= 1
            sound(3)
        else:
            s.gates += 1
            sound(0)
        s.obstacle = (s.obstacle + s.gates + 1) % 3
        s.kind ^= 1
        s.age = 0
        if s.hp == 0:
            lose()
        elif s.gates >= 18:
            win()


def draw():
    # Perspective changes the picture only: lane and collision timing stay exact.
    spread = 2 + s.age * 6 // 5
    x = 14 - spread if s.obstacle == 0 else (14 + spread if s.obstacle == 2 else 14)
    if s.age < 2:
        letter(x, 4 + s.age * 2, 35 if s.kind == 0 else 79)
    else:
        tile(x, 4 + s.age * 2 + (2 if s.age > 3 else 0), 1 if s.kind == 0 else 6)
    tile(6 + s.lane * 8, 17 - s.jump, 2)
    number(8, 21, s.hp)
    number(26, 21, s.gates)
