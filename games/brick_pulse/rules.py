# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(18):
        b[i] = 1
    s.x = 14
    s.y = 10
    s.dx = 1
    s.dy = 0
    s.paddle = 12
    s.hp = 3
    s.left = 18


def act():
    if s.action == 3:
        s.paddle = max(0, s.paddle - 2) if s.paddle >= 2 else 0
    if s.action == 4:
        s.paddle = min(24, s.paddle + 2)


def tick():
    if s.x == 0:
        s.dx = 1
    if s.x == 29:
        s.dx = 0
    s.clock += 1
    if not s.steep or s.clock % 2 == 0:
        s.x = s.x + 1 if s.dx else s.x - 1
    if s.y == 0:
        s.dy = 1
    s.y = s.y + 1 if s.dy else s.y - 1
    if s.y < 6:
        i = s.x // 5 + (s.y // 2) * 6
        if b[i]:
            b[i] = 0
            s.left -= 1
            s.dy ^= 1
            sound(1)
    if s.y == 16:
        if s.x >= s.paddle and s.x <= s.paddle + 5:
            s.dy = 0
            s.bounces += 1
            s.steep = 1 if s.x == s.paddle + 2 or s.x == s.paddle + 3 else 0
            s.dx = 0 if s.x < s.paddle + 3 else 1
            sound(0)
        else:
            s.hp -= 1
            s.x = 14
            s.y = 10
            s.dy = 0
            sound(3)
    if s.hp == 0:
        lose()
    elif s.left == 0:
        win()


def draw():
    for i in range(18):
        if b[i]:
            text(i % 6 * 5, 2 + i // 6 * 2, "[##]")
    letter(1 + s.x, 2 + s.y, 79)
    text(1 + s.paddle, 19, "======")
    number(8, 21, s.hp)
    number(25, 21, s.left)
