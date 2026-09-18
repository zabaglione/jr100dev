# ruff: noqa: F821
# Native byte arrays: x/y/route/destination/deadline/express, three slots each.
def init():
    s.hp = 3
    s.origin = entropy()
    s.seed = s.origin ^ (37 + s.level * 17)
    s.capacity = min(3, 2 + s.level)
    s.interval = 24 - s.level * 8
    s.quota = 24 + s.level * 6
    for i in range(3):
        c[16 + i] = rand() % 3
    dispatch(0)


def dispatch(express):
    if s.issued == 8 or s.active == s.capacity:
        return
    for i in range(3):
        if b[i] and b[i] < 5:
            return
    for i in range(3):
        if b[i] == 0:
            b[i] = 2
            b[3 + i] = 5
            b[6 + i] = 0
            b[9 + i] = c[16]
            b[12 + i] = 32
            b[15 + i] = express
            c[16] = c[17]
            c[17] = c[18]
            c[18] = rand() % 3
            s.issued += 1
            s.active += 1
            s.cool = s.interval
            s.notice = 4 if express else 0
            s.notice_time = 8
            sound(2 if express else 0)
            return


def act():
    if s.action == 1 or s.action == 2:
        s.cursor ^= 1
    elif s.action == 3:
        c[2 + s.cursor] ^= 1
        sound(0)
    elif s.action == 4:
        c[s.cursor] ^= 1
        sound(0)
    elif s.action == 5:
        dispatch(1)


def arrive(i):
    s.arrival = i + 1
    c[8 + b[6 + i]] = 12
    s.done += 1
    s.active -= 1
    s.reward = 0
    if b[6 + i] != b[9 + i]:
        s.notice = 2
    elif b[15 + i] == 2:
        s.notice = 3
    else:
        s.notice = 1
        s.chain = min(3, s.chain + 1)
        s.reward = (4 if b[15 + i] else 2) * s.chain
        s.score += s.reward
    s.notice_time = 10
    if s.reward:
        sound(1)
        sparkle(26, b[3 + i])
        animate(12)
    else:
        s.hp -= 1
        s.chain = 0
        sound(3)
        impact(26, b[3 + i])
        animate(30)
    if s.hp == 0:
        if s.notice == 3:
            lose("EXPRESS LATE")
        else:
            lose("WRONG PLATFORM")
        return
    if s.done == 8:
        if s.score < s.quota:
            lose("NOT ENOUGH POINTS THIS SHIFT")
        else:
            s.medal = 3 if s.score >= 60 else (2 if s.score >= 44 else 1)
            win()
        return
    b[i] = 0


def advance_train(i):
    if b[15 + i] == 1:
        if b[12 + i]:
            b[12 + i] -= 1
        else:
            b[15 + i] = 2
    if b[i] == 8 and b[3 + i] == 5:
        if c[2]:
            return
        b[6 + i] = c[0]
    if b[i] == 17 and b[3 + i] == 10:
        if c[3]:
            return
        b[6 + i] = 1 + c[1]
    if b[i] == 25 and c[8 + b[6 + i]]:
        return
    nx = b[i] + 1
    ny = b[3 + i] + (1 if b[3 + i] < 5 + b[6 + i] * 5 else 0)
    # Automatic braking keeps the two-character cars visibly separated.
    for j in range(3):
        if j != i and b[j]:
            dx = nx - b[j] if nx >= b[j] else b[j] - nx
            dy = ny - b[3 + j] if ny >= b[3 + j] else b[3 + j] - ny
            if dx < 3 and dy < 2:
                return
    b[i] = nx
    b[3 + i] = ny
    if nx == 26:
        arrive(i)


def tick():
    s.arrival = 0
    s.age += 1
    if s.notice_time:
        s.notice_time -= 1
    if s.cool:
        s.cool -= 1
    for i in range(3):
        if c[8 + i]:
            c[8 + i] -= 1
    for i in range(3):
        if b[i]:
            advance_train(i)
            if s.mode != 1:
                return
    if s.cool == 0:
        dispatch(0)


def draw():
    goals = 0
    for i in range(3):
        if b[i]:
            goals |= 1 << b[9 + i]
    face(3, 2 if goals & 1 else 1)
    face(4, 2 if goals & 2 else 1)
    face(5, 2 if goals & 4 else 1)
    for x in range(25 if c[0] == 0 else 6):
        letter(3 + x, 6, 186)
    if c[0]:
        for i in range(4):
            letter(10 + i, 7 + i, 187)
        letter(14, 11, 190)
        for x in range(13 if c[1] == 0 else 3):
            letter(15 + x, 11, 186)
        if c[1]:
            for i in range(4):
                letter(19 + i, 12 + i, 187)
            letter(23, 16, 190)
            for x in range(4):
                letter(24 + x, 16, 186)
    for i in range(2):
        x = 9 + i * 9
        y = 4 + i * 5
        letter(x, y + 2, 184 + c[i])
        letter(x, y, 105 if c[i] == 0 else 103)
        if c[2 + i]:
            text(x + 2, y - 1, "STOP")
        else:
            text(x + 2, y - 1, "GO  ")
    letter(6 + s.cursor * 9, 3 + s.cursor * 5, 105)
    for i in range(3):
        y = 5 + i * 5
        tile(29, y, 3 + i)
        if c[8 + i]:
            text(24, y - 2, "BUSY")
        if goals & (1 << i):
            letter(28, y, 62)
            for x in range(4):
                letter(28 + x, y - 1, 110 if s.age % 2 else 142)
                letter(28 + x, y + 2, 110 if s.age % 2 else 116)
        if b[i]:
            tile(b[i], b[3 + i], 2)
            letter(b[i], b[3 + i] - 1, 49 + i)
            letter(b[i] + 1, b[3 + i] - 1, 65 + b[9 + i])
            letter(1, 10 + i * 2, 49 + i)
            letter(3, 10 + i * 2, 65 + b[9 + i])
            if b[15 + i]:
                margin = b[12 + i] - (26 - b[i]) if b[12 + i] >= 26 - b[i] else 0
                letter(5, 10 + i * 2, 43 if b[15 + i] == 1 else 33)
                digits(6, 10 + i * 2, margin)
            else:
                text(5, 10 + i * 2, "REG")
    letter(4, 19, 48 + s.hp)
    letter(11, 19, 48 + s.done)
    letter(24, 19, 48 + max(1, s.chain))
    number(5, 20, s.score)
    number(11, 20, s.quota)
    for i in range(3):
        letter(6 + i * 2, 21, 65 + c[16 + i] if s.issued + i < 8 else 45)
    digits(18, 21, s.cool)
    if s.mode == 2 or s.mode == 4:
        if s.medal == 3:
            text(1, 2, "GOLD DISPATCHER!")
        elif s.medal == 2:
            text(1, 2, "SILVER DISPATCHER!")
        else:
            text(1, 2, "BRONZE DISPATCHER!")
    elif s.notice_time and s.notice == 1:
        text(1, 2, "DELIVERED +")
        digits(12, 2, s.reward)
        text(16, 2, "CHAIN BONUS!")
    elif s.notice_time and s.notice == 2:
        text(1, 2, "WRONG STATION! CHAIN LOST")
    elif s.notice_time and s.notice == 3:
        text(1, 2, "EXPRESS LATE! CHAIN LOST")
    elif s.notice_time and s.notice == 4:
        text(1, 2, "EXPRESS DEPARTED")
    effect_draw()
