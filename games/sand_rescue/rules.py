# ruff: noqa: F821
# Three routes: b = needs, sand loss, near/far positions; c = crop growth.
# d[120:122] is a checkpoint outside the stage-clear range, owned by this game.
def init():
    s.water = 108 if s.level == 0 else d[120]
    s.total = 0 if s.level == 0 else d[121]
    s.quota = quotas[s.level]
    s.interval = 5 - s.level // 2
    s.fill = s.interval
    for i in range(3):
        k = s.level * 3 + i
        b[i] = near_need[k]
        b[3 + i] = far_need[k]
        b[6 + i] = soak[k]
        b[9 + i] = near_step[k]
        b[12 + i] = far_step[k]


def checkpoint():
    d[120] = s.water + s.tank
    d[121] = s.total


def act():
    if s.action == 3 or s.action == 4:
        s.gate = (s.gate + (2 if s.action == 3 else 1)) % 3
        sound(0)
    elif s.action == 1 and s.score >= s.quota and s.flow == 0:
        s.total += s.score
        win()
    elif s.action == 5 and s.flow == 0 and s.tank:
        s.route = s.gate
        s.flow = s.tank
        s.tank = 0
        s.step = 0
        s.notice = 0
        s.opening = 1
        sound(2)
        animate(5)
        s.opening = 2
        animate(5)
        s.opening = 0


def irrigate(i):
    s.growing = i + 1
    for drop in range(5):
        if s.flow and c[i] < b[i]:
            s.flow -= 1
            c[i] += 1
            sound(0)
            animate(5)
            if c[i] == b[i]:
                s.reward = 3 if i < 3 else b[i] * 2
                s.score += s.reward
                s.notice = 1
                s.notice_time = 12
                sound(1)
                sparkle(5 + i % 3 * 10, crop_y(i))
    s.growing = 0


def crop_y(i):
    return 6 + b[9 + i] if i < 3 else 5 + b[9 + i]


def tick():
    s.age += 1
    if s.notice_time:
        s.notice_time -= 1
    if s.flow:
        s.step += 1
        if s.step == b[9 + s.route]:
            irrigate(s.route)
        elif s.step == b[9 + s.route] + 3:
            loss = min(s.flow, b[6 + s.route])
            s.flow -= loss
            s.waste += loss
            s.notice = 2
            s.notice_time = 8
            sound(3)
            s.drying = 1
            animate(5)
            s.drying = 2
            animate(5)
            s.drying = 0
        elif s.step == b[12 + s.route]:
            irrigate(3 + s.route)
        elif s.step > b[12 + s.route] + 2:
            s.waste += s.flow
            s.flow = 0
    if s.water:
        s.fill -= 1
        if s.fill == 0:
            s.fill = s.interval
            s.water -= 1
            if s.tank < 9:
                s.tank += 1
            else:
                s.waste += 1
                s.notice = 3
                s.notice_time = 8
                sound(3)
                impact(19, 3)
    if s.water == 0 and s.tank == 0 and s.flow == 0 and s.score < s.quota:
        lose("NO WATER LEFT FOR THE HARVEST")


def channel(i, step, wet):
    bend = b[9 + i] + 2
    x = 2 + i * 10
    y = 6 + step
    shape = 0
    if step == bend:
        shape = 1
    elif step > bend:
        x += 1
        y -= 1
        shape = 2 if step == bend + 1 else 0
    letter(x, y, 164 + s.age % 2 if wet else 160 + shape)


def draw():
    number(6, 1, s.water + s.tank)
    digits(19, 1, s.score)
    digits(22, 1, s.quota)
    letter(21, 3, 48 + s.tank)
    for j in range(9):
        letter(10 + j, 3, 164 + s.age % 2 if j < s.tank else 32)
    for i in range(3):
        x = 2 + i * 10
        letter(x, 5, 166 if s.flow and s.route == i else 163)
        if s.opening and s.route == i:
            letter(x, 5, 45 if s.opening == 1 else 166)
        letter(x - 1, 5, 62 if s.gate == i else 32)
        for step in range(b[12 + i] + 3):
            channel(i, step, 0)
        for far in range(2):
            plant = i + far * 3
            y = crop_y(plant)
            tile(
                x + 3,
                y,
                (5 if far else 3) if c[plant] == b[plant] else (4 if c[plant] else 2),
            )
            letter(x + 6, y, 43)
            digits(x + 7, y, b[plant] * 2 if far else 3)
            letter(x + 3, y + 2, 48 + c[plant])
            letter(x + 4, y + 2, 47)
            letter(x + 5, y + 2, 48 + b[plant])
            letter(x + 1, y + 1, 189 if s.growing == plant + 1 else 188)
            letter(x + 2, y + 1, 189 if s.growing == plant + 1 else 188)
        letter(x + 1, 8 + b[9 + i], 167)
        letter(x + 2, 9 + b[9 + i], 48 + b[6 + i])
    if s.flow:
        for tail in range(min(3, s.flow)):
            if s.step >= tail:
                channel(s.route, s.step - tail, 1)
    letter(30, 3, 48 + s.flow)
    if s.drying:
        letter(3 + s.route * 10, 8 + b[9 + s.route], 150 if s.drying == 1 else 152)
    if s.mode == 2 or s.mode == 4:
        text(1, 20, "BANKED")
        digits(8, 20, s.score)
        text(13, 20, "WATER SAVED")
        number(25, 20, s.water + s.tank)
    elif s.notice_time:
        if s.notice == 1:
            text(1, 20, "HARVEST +")
            digits(10, 20, s.reward)
        elif s.notice == 2:
            text(1, 20, "WATER SOAKED INTO SAND")
        elif s.notice == 3:
            text(1, 20, "TANK OVERFLOW!")
    text(1, 22, "TOTAL")
    number(7, 22, s.total if s.mode != 1 else s.total + s.score)
    if s.level < 5:
        text(13, 22, "NEXT")
        digits(18, 22, quotas[s.level + 1])
    if s.score >= s.quota and s.mode == 1:
        text(24, 22, "READY")
    if s.level == 5 and (s.mode == 2 or s.mode == 4):
        if s.total >= 140:
            text(1, 2, "GOLD HARVEST")
        elif s.total >= 130:
            text(1, 2, "SILVER HARVEST")
        else:
            text(1, 2, "BRONZE HARVEST")
    effect_draw()
