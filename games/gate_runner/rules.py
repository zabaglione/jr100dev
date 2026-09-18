# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.lane = 1
    s.obstacle = 1
    s.hp = 3


def act():
    old = s.lane
    if s.action == 3 and s.lane > 0:
        s.lane -= 1
    if s.action == 4 and s.lane < 2:
        s.lane += 1
    if s.action == 5 or s.action == 1:
        s.jump = 3
        sound(0)
        animate(3)
    if old != s.lane:
        s.travel = 1
        flight(6 + old * 8, 17 - s.jump, 6 + s.lane * 8, 17 - s.jump, 2)
        s.travel = 0


def tick():
    if s.jump:
        s.jump -= 1
    s.age += 1
    if s.age == 6:
        if (
            s.lane == s.obstacle or (s.gates >= 6 and s.lane == (s.obstacle + 1) % 3)
        ) and (s.kind == 0 or s.jump == 0):
            s.hp -= 1
            sound(3)
            impact(6 + s.lane * 8, 17 - s.jump)
            if s.hp == 0:
                if s.kind == 0:
                    lose("HIT THE BARRIER")
                else:
                    lose("FELL INTO THE GAP")
                return
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
    if s.gates >= 6:
        other = (s.obstacle + 1) % 3
        x = 14 - spread if other == 0 else (14 + spread if other == 2 else 14)
        if s.age < 2:
            letter(x, 4 + s.age * 2, 35 if s.kind == 0 else 79)
        else:
            tile(x, 4 + s.age * 2 + (2 if s.age > 3 else 0), 1 if s.kind == 0 else 6)
    if not s.travel:
        tile(6 + s.lane * 8, 17 - s.jump, 2)
    digits(8, 21, s.hp)
    digits(26, 21, s.gates)
    effect_draw()
