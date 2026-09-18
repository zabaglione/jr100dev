# ruff: noqa: F821
# The road spans character columns 2..29. The runner is two characters wide.
def init():
    s.x = 15
    s.hp = 3
    s.limit = 9 if s.level == 0 else 12
    s.speed = 1
    s.rate = 6 - s.level // 2
    load_gate(0, 0)
    load_gate(1, 16)


def load_gate(event, slot):
    k = (event + s.level * 2) % 12
    b[slot] = kinds[k]
    b[slot + 1] = lefts[k]
    b[slot + 2] = rights[k]
    b[slot + 3] = other_kinds[k]
    b[slot + 4] = other_lefts[k]
    b[slot + 5] = other_rights[k]
    b[slot + 6] = prizes[k]
    b[slot + 7] = prize_air[k]
    if s.level % 2:
        old = b[slot + 1]
        b[slot + 1] = 32 - b[slot + 2]
        b[slot + 2] = 32 - old
        old = b[slot + 4]
        b[slot + 4] = 32 - b[slot + 5]
        b[slot + 5] = 32 - old
        b[slot + 6] = 30 - b[slot + 6]


def shift(action):
    if action == 3 and s.x > 2:
        s.x -= 1
    elif action == 4 and s.x < 28:
        s.x += 1


def act():
    shift(s.action)
    if (s.action == 1 or s.action == 5) and s.air == 0:
        s.air = 8
        sound(0)


def collides(slot):
    if s.x + 2 <= b[slot + 1] or s.x >= b[slot + 2]:
        return 0
    kind = b[slot]
    if (
        kind == 1
        or (kind == 2 and heights[s.air] < 2)
        or (kind == 3 and heights[s.air] >= 2)
    ):
        return kind
    return 0


def tick():
    s.clock += 1
    if s.notice_time:
        s.notice_time -= 1
    shift(held())
    if s.air:
        s.air -= 1
    s.pace += 1
    if s.pace < s.speed:
        return
    s.pace = 0
    s.age += 1
    if s.age == 20:
        s.age = 0
        load_gate(s.gates, 0)
        load_gate(s.gates + 1, 16)
        return
    if s.age == 18:
        s.hit = max(collides(0), collides(3))
        if s.hit:
            s.hp -= 1
            s.notice = s.hit
            s.notice_time = 18
            sound(3)
            impact(s.x, 18 - heights[s.air])
            animate(15)
            if s.hp == 0:
                if s.hit == 1:
                    lose("HIT THE WALL")
                elif s.hit == 2:
                    lose("FELL INTO THE PIT")
                else:
                    lose("JUMPED INTO THE LOW BEAM")
                return
        else:
            delta = s.x - b[6] if s.x >= b[6] else b[6] - s.x
            if delta <= 1 and (heights[s.air] >= 2) == b[7]:
                s.coins += 1
                s.notice = 4
                s.notice_time = 12
                sound(1)
                sparkle(s.x, 18 - heights[s.air])
            else:
                sound(0)
        s.gates += 1
        if s.gates == s.limit:
            win()
            return


def project(x, depth):
    half = widths[depth]
    return 16 - (16 - x) * half // 14 if x < 16 else 16 + (x - 16) * half // 14


def draw():
    for x in range(2):
        letter(s.x + x, 20, 167)
    face(2, 3 if s.air else 1 + s.clock % 2)
    tile(s.x, 18 - heights[s.air], 2)
    for i in range(3):
        letter(5 + i * 2, 1, 42 if i < s.hp else 45)
    digits(7, 22, s.gates)
    digits(10, 22, s.limit)
    digits(23, 22, s.coins)
    digits(26, 22, s.limit)
    if s.mode == 2 or s.mode == 4:
        if s.coins >= s.limit - 2:
            text(1, 2, "GOLD RUN")
        elif s.coins >= (s.limit + 1) // 2:
            text(1, 2, "SILVER RUN")
        else:
            text(1, 2, "BRONZE RUN")
    elif s.notice_time:
        if s.notice == 1:
            text(1, 2, "HIT THE WALL!")
        elif s.notice == 2:
            text(1, 2, "FELL INTO THE PIT!")
        elif s.notice == 3:
            text(1, 2, "HIT THE LOW BEAM!")
        else:
            text(1, 2, "CRYSTAL +1")
    effect_draw()
