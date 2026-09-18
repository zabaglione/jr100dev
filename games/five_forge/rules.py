# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def count_ray(pos, direction, mark):
    count = 0
    p = pos
    for i in range(7):
        p = ray(p, direction)
        if p == 255:
            return count
        if b[p] != mark:
            return count
        count += 1
    return count


def line(pos, mark):
    best = 0
    for d in range(4):
        total = 1 + count_ray(pos, d * 2, mark) + count_ray(pos, d * 2 + 1, mark)
        best = max(best, total)
    return best


def init():
    s.cursor = 27


def place(pos, mark):
    b[pos] = mark
    s.stones += 1
    s.last = pos
    s.placing = mark
    sound(0)
    for frame in range(4):
        s.pose = (mark - 1) * 4 + frame + 1
        if frame == 2:
            sound(1)
        animate(8 if frame < 3 else 12)
    s.placing = 0


def mark_ray(pos, direction, mark):
    p = pos
    for step in range(7):
        p = ray(p, direction)
        if p == 255:
            return
        if b[p] != mark:
            return
        d[p] = 1


def complete(pos, mark):
    if line(pos, mark) < 5:
        return 0
    d[pos] = 1
    for axis in range(4):
        if 1 + count_ray(pos, axis * 2, mark) + count_ray(pos, axis * 2 + 1, mark) >= 5:
            for side in range(2):
                mark_ray(pos, axis * 2 + side, mark)
    s.winner = mark
    for flash in range(3):
        s.blink = 1
        sound(0)
        animate(12)
        s.blink = 0
        animate(16)
    animate(24)
    if mark == 1:
        win()
    else:
        lose("RIVAL COMPLETED FIVE")
    return 1


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 8, 8)
    if s.action == 5 and b[s.cursor] == 0:
        place(s.cursor, 1)
        if complete(s.cursor, 1):
            return
        best = 0
        chosen = 255
        for i in range(64):
            if b[i] == 0:
                attack = line(i, 2)
                defense = line(i, 1)
                value = attack * 3 + defense
                if defense >= 5:
                    value = 100
                if attack >= 5:
                    value = 120
                if value > best:
                    best = value
                    chosen = i
        if chosen != 255:
            place(chosen, 2)
            complete(chosen, 2)
        elif s.stones >= 64:
            lose("BOARD FULL - NO FIVE")


def tick():
    pass


def draw():
    if s.placing:
        face(3, s.pose)
    elif b[s.cursor]:
        face(3, b[s.cursor] * 4)
    for i in range(64):
        shape = b[i]
        if s.winner:
            if s.blink and d[i]:
                shape = 0
        elif s.placing:
            if i == s.last:
                shape = 3
        elif i == s.cursor:
            shape = 3 if b[i] else 4
        tile(1 + i % 8 * 2, 4 + i // 8 * 2, shape)
    tile(22, 5, 1)
    tile(22, 11, 2)
    own = (s.stones + 1) // 2
    rival = s.stones // 2
    small_number(27, 6, own)
    small_number(27, 12, rival)
    if s.placing == 2:
        text(21, 16, "RIVAL MOVE")
    elif s.placing == 1:
        text(21, 16, "YOUR MOVE")
    elif s.winner:
        text(21, 16, "LAST MOVE")
    else:
        text(21, 16, "YOUR TURN")
    pos = s.last if s.placing or s.winner else s.cursor
    text(21, 18, "CELL")
    letter(27, 18, 65 + pos % 8)
    letter(28, 18, 49 + pos // 8)


def small_number(x, y, value):
    if value >= 10:
        letter(x, y, 48 + value // 10)
    letter(x + 1, y, 48 + value % 10)
