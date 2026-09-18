# ruff: noqa: F821
# The native compiler supplies state, arrays and drawing functions.
def init():
    s.origin = entropy()
    s.seed = s.origin ^ (s.level * 17)
    for i in range(16):
        b[i] = i // 2
    for i in range(15):
        s.seed = (s.seed * 109 + 89) & 255
        j = s.seed % (16 - i)
        saved = b[15 - i]
        b[15 - i] = b[j]
        b[j] = saved
    s.first = 255
    s.second = 255
    s.turning = 255
    s.left = 8
    s.limit = 12 - s.level // 3


def turn(pos, reveal):
    s.turning = pos
    sound(0)
    for frame in range(5):
        s.pose = frame + 1 if reveal else 5 - frame
        animate(3)
    s.turning = 255
    c[pos] = reveal


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5:
        s.notice = 0
        if s.second != 255:
            if b[s.first] != b[s.second]:
                turn(s.first, 0)
                turn(s.second, 0)
            s.first = 255
            s.second = 255
        elif not c[s.cursor]:
            turn(s.cursor, 1)
            if s.first == 255:
                s.first = s.cursor
            else:
                s.second = s.cursor
                if b[s.first] == b[s.second]:
                    s.left -= 1
                    s.chain += 1
                    s.best = max(s.best, s.chain)
                    s.notice = 1
                    sound(1)
                    sparkle(2 + s.first % 4 * 4, 4 + s.first // 4 * 4)
                    sparkle(2 + s.second % 4 * 4, 4 + s.second // 4 * 4)
                else:
                    s.errors += 1
                    s.chain = 0
                    s.notice = 2
                    sound(3)
                    animate(18)
                if not s.left:
                    win()
                elif s.errors >= s.limit:
                    lose("TOO MANY PAIRS DID NOT MATCH")


def tick():
    pass


def draw():
    if s.turning != 255:
        flip(s.pose)
    for i in range(16):
        x = 2 + i % 4 * 4
        y = 4 + i // 4 * 4
        tile(x, y, 6 if i == s.turning else (7 if c[i] else 4))
        if c[i] and i != s.turning:
            letter(x, y, 160 + b[i])
    letter(1 + s.cursor % 4 * 4, 4 + s.cursor // 4 * 4, 62)
    digits(24, 7, 8 - s.left)
    digits(23, 14, s.errors)
    letter(25, 14, 47)
    digits(26, 14, s.limit)
    text(20, 17, "CHAIN")
    letter(27, 17, 48 + s.chain)
    if s.mode == 2:
        text(1, 20, "ALL EIGHT PAIRS FOUND")
    elif s.notice == 1:
        text(1, 20, "MATCHED!")
    elif s.notice == 2:
        text(1, 20, "MISMATCH")
    effect_draw()
