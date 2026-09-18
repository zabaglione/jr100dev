# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def deal():
    for i in range(4):
        low = s.rng_lo & 1
        s.rng_lo = (s.rng_lo >> 1) | ((s.rng_hi & 1) << 7)
        s.rng_hi >>= 1
        if low:
            s.rng_hi ^= 180
    return (s.rng_lo ^ s.rng_hi) % 5


def init():
    s.level = 0
    s.origin = entropy()
    s.rng_lo = s.origin | 1
    s.rng_hi = s.origin ^ 165
    s.spins = 2
    s.target = 12
    for i in range(16):
        b[i] = 255
    first = deal()
    for i in range(4):
        b[12 + i] = (first + i) % 5
    for i in range(5):
        d[16 + i] = deal()
    d[16] = (first + 4) % 5
    d[17] = (first + d[17] % 4) % 5
    s.card = d[16]


def advance():
    s.mode = 1
    s.level = min(s.level + 1, 254)
    s.target = min(s.target + 6, 60)
    s.progress = 0


def evaluate():
    s.lines = 0
    for i in range(16):
        c[i] = 0
    for i in range(24):
        a = paths[i * 3]
        middle = paths[i * 3 + 1]
        end = paths[i * 3 + 2]
        if b[a] != 255 and b[a] == b[middle] and b[a] == b[end]:
            s.lines += 1
            c[a] = 1
            c[middle] = 1
            c[end] = 1


def settle():
    for step in range(3):
        changed = 0
        for i in range(16):
            d[i] = 0
        for i in range(12):
            source = 11 - i
            if b[source] != 255 and b[source + 4] == 255:
                d[source] = 1
                changed = 1
        if not changed:
            return
        s.falling = 1
        for frame in range(3):
            s.slide = frame * 2
            animate(3)
        for i in range(12):
            source = 11 - i
            if d[source]:
                b[source + 4] = b[source]
                b[source] = 255
        s.falling = 0
        sound(0)


def credit():
    s.progress = min(s.progress + s.points, 99)
    s.score_lo += s.points
    if s.score_lo >= 100:
        if s.score_hi == 99:
            s.score_lo = 99
        else:
            s.score_lo -= 100
            s.score_hi += 1


def resolve():
    s.chain = 0
    s.points = 0
    for wave in range(5):
        evaluate()
        if not s.lines:
            settle()
            evaluate()
        if not s.lines:
            return
        s.chain += 1
        sound(1 if s.chain == 1 else 2)
        for frame in range(3):
            s.glow = frame + 1
            animate(5)
        count = 0
        for i in range(16):
            if c[i]:
                b[i] = 255
                count += 1
            c[i] = 0
        s.glow = 0
        s.points = count * 2 * s.chain + (s.lines - 1) * 2
        credit()
        s.spins = min(s.spins + 1, 4)
        animate(10)
        settle()


def finish():
    if s.progress >= s.target:
        win()
    else:
        full = 1
        for i in range(16):
            if b[i] == 255:
                full = 0
        if full:
            if not s.spins:
                lose("FULL BOARD - NO SPINS")
            else:
                if not s.tool:
                    s.phase = 1
                    s.cursor = 17
                s.notice = 2


def place():
    target = 255
    for row in range(4):
        pos = row * 4 + s.cursor % 4
        if b[pos] == 255:
            target = pos
    if target == 255:
        s.notice = 3
        sound(0)
        return
    s.flying = 1
    s.fx = 2 + target % 4 * 5
    bottom = 4 + target // 4 * 4
    sound(0)
    for frame in range(5):
        s.fy = 3 + (bottom - 3) * frame // 4
        animate(3)
    s.flying = 0
    b[target] = s.card
    resolve()
    d[16 + s.offer] = d[18]
    d[18] = d[19]
    d[19] = d[20]
    d[20] = deal()
    s.card = d[16 + s.offer]
    s.phase = 0
    finish()


def rotate():
    if not s.spins:
        s.notice = 1
        sound(0)
        return
    s.axis = s.tool - 1
    s.orbit = s.cursor // 4 if not s.axis else s.cursor % 4
    first = s.orbit * 4 if not s.axis else s.orbit
    stride = 1 if not s.axis else 4
    same = 1
    for i in range(4):
        if b[first + i * stride] != b[first]:
            same = 0
    if same:
        s.notice = 4
        sound(0)
        return
    s.rotating = 1
    sound(0)
    for frame in range(4):
        s.slide = frame * (5 if not s.axis else 4) // 3
        animate(4)
    last = first + 3 * stride
    saved = b[last]
    for i in range(3):
        b[last - i * stride] = b[last - (i + 1) * stride]
    b[first] = saved
    s.rotating = 0
    s.spins -= 1
    resolve()
    finish()


def act():
    s.notice = 0
    if not s.phase:
        if s.action == 3 or s.action == 4:
            s.offer = 1 - s.offer
            s.card = d[16 + s.offer]
            sound(0)
        if s.action == 5:
            s.phase = 1
            s.cursor = s.cell
        if s.action == 2:
            s.phase = 1
            s.cursor = 16
        return
    if s.action < 5:
        s.cursor = min(move(s.cursor, s.action, 4, 5), 18)
        if s.cursor < 16:
            s.cell = s.cursor
    if s.action == 5:
        if s.cursor >= 16:
            s.tool = s.cursor - 16
            s.cursor = s.cell
            if not s.tool:
                s.phase = 0
        elif not s.tool:
            place()
        else:
            rotate()


def tick():
    pass


def moving(pos):
    for quad in range(4):
        x = pos % 4 * 5 + quad % 2
        y = pos // 4 * 4 + quad // 2
        if s.falling or s.axis:
            y = (y + s.slide) % 16
        else:
            x = (x + s.slide) % 20
        letter(2 + x, 4 + y, 160 + b[pos] * 4 + quad)


def card(i):
    x = 1 + i % 4 * 5
    y = 3 + i // 4 * 4
    shifted = i // 4 == s.orbit if not s.axis else i % 4 == s.orbit
    if b[i] != 255:
        if (s.rotating and shifted) or (s.falling and d[i]):
            moving(i)
        else:
            letter(x + 1, y, 65 + b[i])
            if s.glow and c[i]:
                for quad in range(4):
                    letter(
                        x + 1 + quad % 2,
                        y + 1 + quad // 2,
                        bursts[(s.glow - 1) * 4 + quad],
                    )
            else:
                tile(x + 1, y + 1, b[i])


def pair(x, y, value):
    letter(x, y, 48 + value // 10)
    letter(x + 1, y, 48 + value % 10)


def draw():
    for i in range(16):
        card(i)
    if s.flying:
        tile(s.fx, s.fy, s.card)
    if s.phase == 1 and s.cursor < 16:
        col = s.cursor % 4
        row = s.cursor // 4
        if not s.tool:
            for i in range(4):
                if b[i * 4 + col] == 255:
                    row = i
        if s.tool == 2:
            letter(2 + col * 5, 2, 86)
            letter(2 + col * 5, 19, 94)
        else:
            letter(0 if s.tool == 1 else col * 5, 4 + row * 4, 62)
            letter(20 if s.tool == 1 else 5 + col * 5, 4 + row * 4, 60)
    for i in range(2):
        tile(23 + i * 4, 5, d[16 + i])
        letter(23 + i * 4, 7, 65 + d[16 + i])
    letter(23 + s.offer * 4, 4, 86)
    for i in range(3):
        letter(27 + i, 8, 65 + d[18 + i])
    pair(24, 13, s.score_hi)
    pair(26, 13, s.score_lo)
    letter(29, 14, 48 + s.chain)
    pair(26, 17, s.progress)
    pair(29, 17, s.target)
    letter(27, 19, 48 + s.spins)
    if s.mode == 1:
        text(1, 21, "CARD  ROW   COL")
        letter(s.tool * 6, 21, 91)
        letter(s.tool * 6 + 5, 21, 93)
        if s.phase == 1 and s.cursor >= 16:
            letter((s.cursor - 16) * 6, 21, 62)
        if s.notice == 1:
            text(0, 22, "NO SPINS: CLEAR A LINE TO EARN")
        elif s.notice == 2:
            text(0, 22, "FULL BOARD: USE ROW / COL")
        elif s.notice == 3:
            text(0, 22, "COLUMN FULL: PICK ANOTHER")
        elif s.notice == 4:
            text(0, 22, "SAME CARDS: NO SPIN USED")
