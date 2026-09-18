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
    s.route = 0
    s.arrival = 0
    s.wrong = 0
    s.ready = 3
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
    oldx = 8 + s.age * 2
    oldy = 5 + s.route * 5
    s.age += 1
    if s.age == 3:
        s.route = 0 if c[0] == 0 else (1 if c[1] == 0 else 2)
    s.travel = 1
    cruise(oldx, oldy, 8 + s.age * 2, 5 + s.route * 5, 2)
    s.travel = 0
    if s.age == 9:
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
            c[s.service % 2] ^= 1
            s.service = (s.service + 1) % 12
            departure()


def draw():
    face(3, 2 if s.dest == 0 else 1)
    face(4, 2 if s.dest == 1 else 1)
    face(5, 2 if s.dest == 2 else 1)
    for i in range(3):
        text(9, 5 + i * 5, "-------------------")
        tile(29, 5 + i * 5, 3 + i)
    y = 5 + s.dest * 5
    text(20, y - 1, "DELIVER")
    for x in range(4):
        letter(28 + x, y - 1, 110 if (s.age + s.ready) % 2 or s.arrival else 142)
        letter(28 + x, y + 2, 110 if (s.age + s.ready) % 2 or s.arrival else 116)
    for row in range(2):
        letter(28, y + row, 136)
        letter(31, y + row, 146)
    tile(6, 5, 6)
    tile(6, 10, 6)
    letter(4, 5 + s.cursor * 5, 105)
    letter(3, 5, 65 if c[0] == 0 else 103)
    letter(3, 10, 66 if c[1] == 0 else 67)
    if not s.travel:
        tile(8 + s.age * 2, 5 + s.route * 5, 2)
    letter(7, 19, 48 + s.hp)
    digits(24, 19, s.delivered)
    letter(6, 21, 65 + s.next1)
    letter(10, 21, 65 + s.next2)
    letter(14, 21, 65 + s.next3)
    if s.wrong:
        text(1, 2, "WRONG PLATFORM! CHECK DEST")
    elif s.arrival:
        text(1, 2, "DELIVERED - TRAIN AT PLATFORM")
    elif s.ready:
        text(1, 2, "SET ROUTE - TRAIN READY")
    effect_draw()
