# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.hp = 3
    departure()


def departure():
    # The current train and its forecast change together, after arrival finishes.
    s.dest = timetable[s.service]
    s.next1 = timetable[(s.service + 1) % 12]
    s.next2 = timetable[(s.service + 2) % 12]
    s.next3 = timetable[(s.service + 3) % 12]
    s.age = 0
    s.x = 2
    s.y = 5
    s.route = 0
    s.j1 = 0
    s.j2 = 0
    s.slope = 0
    s.arrival = 0
    s.wrong = 0
    s.ready = 6
    reschedule()


def act():
    if s.action == 1 or s.action == 2:
        s.cursor ^= 1
    if s.action == 3 or s.action == 4 or s.action == 5:
        c[s.cursor] ^= 1
        sound(0)


def tick():
    if s.ready:
        s.ready -= 1
        if s.ready == 0:
            sound(0)
        return
    oldx = s.x
    oldy = s.y
    s.age += 1
    # Each point is read only when the train reaches that physical junction.
    if s.x == 8 and s.y == 5:
        s.j1 = 1
        if c[0]:
            s.route = 1
        sound(0)
    if s.x == 17 and s.y == 10:
        s.j2 = 1
        if c[1]:
            s.route = 2
        sound(0)
    targety = 5 + s.route * 5
    if s.y < targety:
        s.x += 1
        s.y += 1
    else:
        s.x += 2 if s.x < 25 else 1
    s.slope = 1 if s.y > oldy and s.y < targety else 0
    s.travel = 1
    cruise(oldx, oldy, s.x, s.y, 2)
    s.travel = 0
    if s.x == 26:
        s.arrival = 1
        if s.route == s.dest:
            s.delivered += 1
            sound(1)
            sparkle(26, 5 + s.route * 5)
            animate(18)
        else:
            s.hp -= 1
            s.wrong = 1
            sound(3)
            impact(26, 5 + s.route * 5)
            animate(30)
        if s.hp == 0:
            lose("THREE TRAINS REACHED WRONG PLATFORMS")
        elif s.delivered == 12:
            win()
        else:
            s.service = (s.service + 1) % 12
            departure()


def draw():
    face(2, 1 + s.slope)
    face(3, 2 if s.dest == 0 else 1)
    face(4, 2 if s.dest == 1 else 1)
    face(5, 2 if s.dest == 2 else 1)
    # Bold rails are the connected route; the other tracks remain thin.
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
    letter(9, 6, 184 + c[0])
    letter(18, 11, 184 + c[1])
    letter(6 + s.cursor * 9, 3 + s.cursor * 5, 105)
    letter(9, 4, 105 if c[0] == 0 else 103)
    letter(18, 9, 105 if c[1] == 0 else 103)
    if c[0]:
        text(11, 3, "DOWN")
    else:
        text(11, 3, "A")
    letter(20, 8, 66 + c[1])
    for i in range(3):
        tile(29, 5 + i * 5, 3 + i)
    y = 5 + s.dest * 5
    text(24, y - 2, "GOAL")
    for x in range(4):
        letter(28 + x, y - 1, 110 if (s.age + s.ready) % 2 or s.arrival else 142)
        letter(28 + x, y + 2, 110 if (s.age + s.ready) % 2 or s.arrival else 116)
    for row in range(2):
        letter(28, y + row, 136)
        letter(31, y + row, 146)
    if not s.travel:
        tile(s.x, s.y, 2)
    letter(7, 19, 48 + s.hp)
    digits(24, 19, s.delivered)
    letter(6, 21, 65 + s.next1)
    letter(10, 21, 65 + s.next2)
    letter(14, 21, 65 + s.next3)
    text(18, 21, "ROUTE")
    letter(24, 21, 65 if c[0] == 0 else 66 + c[1])
    if s.wrong:
        text(1, 2, "WRONG PLATFORM! CHECK DEST")
    elif s.arrival:
        text(1, 2, "DELIVERED - TRAIN AT PLATFORM")
    elif s.ready:
        text(1, 2, "SET ROUTE - TRAIN READY")
    elif s.j1 and s.route == 0:
        text(1, 2, "TO A - JUNCTION 1 PASSED")
    elif s.j2:
        text(1, 2, "TO")
        letter(4, 2, 65 + s.route)
        text(6, 2, "- JUNCTION 2 PASSED")
    elif s.j1:
        text(1, 2, "NEXT TURN: JUNCTION 2")
    else:
        text(1, 2, "SET 1:A/DOWN   2:B/C")
    effect_draw()
