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
        if total > best:
            best = total
    return best


def init():
    s.cursor = 27


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 8, 8)
    if s.action == 5 and b[s.cursor] == 0:
        b[s.cursor] = 1
        s.stones += 1
        if line(s.cursor, 1) >= 5:
            win()
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
            b[chosen] = 2
            s.last = chosen
            s.stones += 1
            if line(chosen, 2) >= 5:
                lose()
        elif s.stones >= 64:
            lose()
        sound(1)


def tick():
    pass


def draw():
    for i in range(64):
        tile(i % 8 * 2, 3 + i // 8 * 2, 0 if b[i] == 0 else (2 if b[i] == 1 else 5))
    letter(s.cursor % 8 * 2, 3 + s.cursor // 8 * 2, 62)
    number(24, 8, s.stones)
    text(20, 13, "YOU: O")
    text(20, 16, "RIVAL: X")
