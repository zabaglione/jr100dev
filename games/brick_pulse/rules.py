# ruff: noqa: F821
# Twelve authored arenas; ball, drops and drone advance on the same clock.
def init():
    for i in range(24):
        b[i] = d[i]
        if b[i]:
            s.left += 1
    s.paddle = 12
    s.width = 6
    s.hp = 3
    s.ex = 6
    s.ed = 1
    if s.level >= 2:
        s.enemy = 2 + s.level // 4
    serve()


def serve():
    s.x = s.paddle + s.width // 2
    s.y = 14
    s.dy = 0
    s.dx = 1
    s.steep = 0


def move_paddle(direction):
    if direction == 3:
        s.paddle = s.paddle - 2 if s.paddle >= 2 else 0
    if direction == 4:
        s.paddle = min(30 - s.width, s.paddle + 2)


def act():
    if s.action == 3 or s.action == 4:
        move_paddle(s.action)
        s.repeat = 1


def drop(kind, x, y):
    if not s.item:
        s.item = kind
        s.ix = x
        s.iy = y


def hazards():
    if s.enemy:
        if s.clock % 2 == 0:
            if s.ex == 2:
                s.ed = 1
            if s.ex == 27:
                s.ed = 0
            s.ex = s.ex + 1 if s.ed else s.ex - 1
        if s.level >= 5 and s.clock % 32 == 0 and not s.bomb:
            s.bomb = 10
            s.bx = s.ex
    if s.bomb and s.clock % 2 == 0:
        s.bomb += 1
        if s.bomb == 17:
            if s.bx >= s.paddle and s.bx < s.paddle + s.width:
                if s.guard:
                    s.guard = 0
                else:
                    s.jam = 48
                    s.wide = 0
                    s.width = 4
                sound(3)
            s.bomb = 0
    if s.item and s.clock % 2 == 0:
        s.iy += 1
        if s.iy == 17:
            if s.ix >= s.paddle and s.ix < s.paddle + s.width:
                if s.item == 1:
                    s.jam = 0
                    s.wide = 96
                    s.width = 10
                    s.paddle = min(20, s.paddle)
                if s.item == 2:
                    s.slow = 96
                if s.item == 3:
                    s.guard = 1
                s.caught += 1
                sound(2)
            s.item = 0


def ball():
    if s.x == 0:
        s.dx = 1
    if s.x == 29:
        s.dx = 0
    if not s.steep or s.steps % 2 == 0:
        s.x = s.x + 1 if s.dx else s.x - 1
    if s.y == 0:
        s.dy = 1
    s.y = s.y + 1 if s.dy else s.y - 1
    if s.y < 8:
        i = s.x // 5 + (s.y // 2) * 6
        if b[i]:
            b[i] -= 1
            s.dy ^= 1
            if not b[i]:
                s.left -= 1
                s.broken += 1
                if s.broken % 3 == 0:
                    drop((s.broken // 3 + s.level) % 3 + 1, s.x, s.y)
            sound(1)
    if s.enemy and s.y == 10 and s.x + 1 >= s.ex and s.x <= s.ex + 1:
        s.enemy -= 1
        s.dy ^= 1
        sound(1)
        if not s.enemy:
            drop(3, s.ex, 10)
    if s.y == 16:
        if s.x >= s.paddle and s.x < s.paddle + s.width:
            s.dy = 0
            s.bounces += 1
            middle = s.paddle + s.width // 2
            s.steep = 1 if s.x == middle or s.x + 1 == middle else 0
            s.dx = 0 if s.x < middle else 1
            sound(0)
        elif s.guard:
            s.guard = 0
            s.dy = 0
            sound(1)
        else:
            s.hp -= 1
            serve()
            sound(3)


def tick():
    direction = held()
    if direction == 3 or direction == 4:
        if s.repeat:
            s.repeat -= 1
        else:
            move_paddle(direction)
    else:
        s.repeat = 0
    s.clock += 1
    if s.jam:
        s.jam -= 1
        if not s.jam:
            s.width = 6
            s.paddle = min(24, s.paddle)
    if s.wide:
        s.wide -= 1
        if not s.wide:
            s.width = 6
    if s.slow:
        s.slow -= 1
    hazards()
    if s.hp:  # noqa: SIM102 - Explicit branches in the native DSL.
        if not s.slow or s.clock % 2 == 0:
            s.steps += 1
            ball()
    if s.hp == 0:
        lose()
    elif s.left == 0 and not s.enemy:
        win()


def draw():
    for i in range(24):
        if b[i]:
            x = 1 + i % 6 * 5
            y = 2 + i // 6 * 2
            letter(x, y, 160)
            letter(x + 1, y, 161 + b[i])
            letter(x + 2, y, 161 + b[i])
            letter(x + 3, y, 161)
    if s.enemy:
        letter(s.ex, 12, 169)
        letter(s.ex + 1, 12, 170)
        letter(s.ex + 2, 12, 171)
    if s.bomb:
        letter(s.bx + 1, s.bomb + 2, 172)
    if s.item:
        letter(s.ix + 1, s.iy + 2, 87 if s.item == 1 else 83 if s.item == 2 else 71)
    letter(s.x + 1, s.y + 2, 165)
    letter(s.paddle + 1, 19, 166)
    for i in range(s.width - 2):
        letter(s.paddle + 2 + i, 19, 167)
    letter(s.paddle + s.width, 19, 168)
    if s.guard:
        text(1, 20, "------------------------------")
    number(6, 21, s.hp)
    number(16, 21, s.left)
    number(28, 21, s.enemy)
    if s.wide:
        text(1, 22, "WIDE")
    if s.jam:
        text(1, 22, "JAM")
    if s.slow:
        text(10, 22, "SLOW")
    if s.guard:
        text(20, 22, "GUARD")
