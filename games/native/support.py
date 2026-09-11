# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
"""Small reusable geometry helpers; game rules and screens stay in each title."""


def move(pos, action, width, height):
    if action == 1 and pos >= width:
        return pos - width
    if action == 2 and pos < width * (height - 1):
        return pos + width
    if action == 3 and pos % width > 0:
        return pos - 1
    if action == 4 and pos % width < width - 1:
        return pos + 1
    return pos


def grid(width, height, left, top):
    for i in range(width * height):
        tile(left + i % width * 2, top + i // width * 2, b[i])


def pointer(pos, width, left, top):
    letter(left + pos % width * 2, top + pos // width * 2, 62)


def box():
    for i in range(64):
        b[i] = 1 if i < 8 or i >= 56 or i % 8 == 0 or i % 8 == 7 else 0


def rand():
    s.seed = (s.seed * 5 + 1) & 255
    return s.seed


def distance(a, b):
    dx = a % 8 - b % 8 if a % 8 >= b % 8 else b % 8 - a % 8
    dy = a // 8 - b // 8 if a // 8 >= b // 8 else b // 8 - a // 8
    return dx + dy


def move8(pos, action):
    if action == 9:
        return move(move(pos, 1, 8, 8), 3, 8, 8)
    if action == 10:
        return move(move(pos, 1, 8, 8), 4, 8, 8)
    if action == 11:
        return move(move(pos, 2, 8, 8), 3, 8, 8)
    if action == 12:
        return move(move(pos, 2, 8, 8), 4, 8, 8)
    return move(pos, action, 8, 8)


def ringx(i):
    if i == 0 or i == 4:
        return 15
    if i == 1 or i == 3:
        return 24
    if i == 2:
        return 28
    if i == 5 or i == 7:
        return 6
    return 2


def ringy(i):
    if i == 0:
        return 3
    if i == 1 or i == 7:
        return 5
    if i == 2 or i == 6:
        return 10
    if i == 3 or i == 5:
        return 15
    return 17


def ray(pos, direction):
    x = pos % 8
    y = pos // 8
    if direction == 0:
        return pos + 1 if x < 7 else 255
    if direction == 1:
        return pos - 1 if x > 0 else 255
    if direction == 2:
        return pos + 8 if y < 7 else 255
    if direction == 3:
        return pos - 8 if y > 0 else 255
    if direction == 4:
        return pos + 9 if x < 7 and y < 7 else 255
    if direction == 5:
        return pos - 9 if x > 0 and y > 0 else 255
    if direction == 6:
        return pos + 7 if x > 0 and y < 7 else 255
    return pos - 7 if x < 7 and y > 0 else 255


def spend_move():
    if s.moves < 255:
        s.moves += 1
    else:
        s.overflow = 1


def take_rune(pos):
    before = s.runes
    if pos == d[67]:
        s.runes |= 1
    if pos == d[68]:
        s.runes |= 2
    if before != s.runes:
        sound(1)


def ranked_clear():
    s.stars = 1
    if s.moves <= s.par and not s.overflow:
        s.stars = 3 if s.runes == 3 else 2
    win()


def draw_runes(left):
    for rune in range(2):
        if not (s.runes & (1 << rune)):
            pos = d[67 + rune]
            tile(left + pos % 8 * 2, 3 + pos // 8 * 2, 6)


def ranked_hud():
    text(1, 20, "MOV 000  PAR 000  RUNES 0/2")
    number(5, 20, s.moves)
    if s.overflow:
        letter(8, 20, 43)
    number(14, 20, s.par)
    letter(25, 20, 48 + (s.runes & 1) + (s.runes >> 1))
