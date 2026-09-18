# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(9):
        b[i] = starts[s.level * 9 + i]
    d[16] = decks[s.level * 7]
    d[17] = decks[s.level * 7 + 1]
    s.drawn = 2
    s.placed = 3
    s.spins = 2
    s.target = 3 if s.level == 1 else 2
    s.card = d[16]
    evaluate()


def line(a, middle, end):
    if b[a] != 255 and b[a] == b[middle] and b[a] == b[end]:
        c[a] = 1
        c[middle] = 1
        c[end] = 1
        s.types |= 1 << b[a]
        return 1
    return 0


def evaluate():
    old_lines = s.lines
    old_progress = s.progress
    s.lines = 0
    s.types = 0
    for i in range(9):
        c[i] = 0
    for i in range(3):
        s.lines += line(i * 3, i * 3 + 1, i * 3 + 2)
        s.lines += line(i, i + 3, i + 6)
    diagonals = line(0, 4, 8) + line(2, 4, 6)
    s.lines += diagonals
    s.progress = s.lines
    if s.level == 1:
        s.progress = (s.types & 1) + ((s.types >> 1) & 1) + ((s.types >> 2) & 1)
    if s.level == 2:
        s.progress = diagonals if b[4] == 0 else 0
    s.gain = 1 if s.progress > old_progress or s.lines > old_lines else 0
    for i in range(9):
        d[i] = c[i] if s.gain else 0


def resonate():
    sound(1)
    animate(8)
    if s.gain:
        for glow in range(3):
            s.glow = glow + 1
            animate(6)
        s.glow = 0
        animate(18)


def finish():
    if s.placed == 9:
        if s.progress >= s.target:
            win()
        elif s.spins == 0:
            failure()
        else:
            s.phase = 1
            s.cursor = 10
            s.notice = 2


def failure():
    if s.level == 0:
        lose("NEED TWO MATCHING LINES")
    elif s.level == 1:
        lose("NEED A, B AND C LINES")
    else:
        lose("NEED BOTH A DIAGONALS")


def place():
    s.flying = 1
    start_x = 23 + s.offer * 4
    target_x = 3 + s.cursor % 3 * 6
    target_y = 6 + s.cursor // 3 * 5
    sound(0)
    for step in range(5):
        s.fx = start_x - (start_x - target_x) * step // 4
        s.fy = 5 + (target_y - 5) * step // 4
        animate(4)
    s.flying = 0
    b[s.cursor] = s.card
    s.placed += 1
    evaluate()
    resonate()
    if s.placed < 9:
        d[16 + s.offer] = decks[s.level * 7 + s.drawn]
        s.drawn += 1
        s.card = d[16 + s.offer]
    s.phase = 0
    finish()


def rotate():
    first = s.orbit * 3 if s.axis == 0 else s.orbit
    stride = 1 if s.axis == 0 else 3
    middle = first + stride
    last = middle + stride
    if b[first] == b[middle] and b[first] == b[last]:
        s.notice = 3
        sound(0)
        return
    s.rotating = 1
    sound(0)
    for step in range(4):
        s.slide = min(step * 2, 6 if s.axis == 0 else 5)
        animate(6)
    saved = b[last]
    b[last] = b[middle]
    b[middle] = b[first]
    b[first] = saved
    s.rotating = 0
    s.spins -= 1
    evaluate()
    resonate()
    s.phase = 1
    s.cursor = s.cell
    finish()


def act():
    s.notice = 0
    s.gain = 0
    if s.phase == 0:
        if s.action == 3 or s.action == 4:
            s.offer = 1 - s.offer
            s.card = d[16 + s.offer]
            sound(0)
        if s.action == 5:
            s.phase = 1
            s.cursor = s.cell
        if s.action == 2:
            s.phase = 1
            s.cursor = 9
        return
    if s.phase == 2:
        if s.axis == 0:
            if s.action == 1:
                s.orbit = (s.orbit + 2) % 3
            if s.action == 2:
                s.orbit = (s.orbit + 1) % 3
            if s.action == 3 or s.action == 4:
                s.phase = 1
                s.cursor = 10
        else:
            if s.action == 3:
                s.orbit = (s.orbit + 2) % 3
            if s.action == 4:
                s.orbit = (s.orbit + 1) % 3
            if s.action == 1 or s.action == 2:
                s.phase = 1
                s.cursor = 11
        if s.action == 5:
            rotate()
        return
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 3, 4)
        if s.cursor < 9:
            s.cell = s.cursor
    if s.action == 5:
        if s.cursor < 9:
            if b[s.cursor] == 255:
                place()
        elif s.cursor == 9:
            if s.placed == 9:
                failure()
            else:
                s.phase = 0
        elif s.spins:
            s.axis = s.cursor - 10
            s.orbit = s.cell // 3 if s.axis == 0 else s.cell % 3
            s.phase = 2
        else:
            s.notice = 1
            sound(0)


def tick():
    pass


def moving(pos):
    left = pos % 3 * 6
    top = pos // 3 * 5
    for quad in range(4):
        x = left + quad % 2
        y = top + quad // 2
        if s.axis == 0:
            x = (x + s.slide) % 18
        else:
            y = (y + s.slide) % 15
        letter(3 + x, 6 + y, 160 + b[pos] * 4 + quad)


def card(x, y, i):
    if s.level == 2 and i % 2 == 0:
        letter(x + 2, y, 65)
    shifted = i // 3 == s.orbit if s.axis == 0 else i % 3 == s.orbit
    if s.rotating and shifted:
        if b[i] != 255:
            moving(i)
    elif b[i] == 255:
        letter(x + 2, y + 2, 43)
    else:
        letter(x + 1, y + 1, 65 + b[i])
        tile(x + 2, y + 2, 3 if s.glow and d[i] else b[i])
    if c[i] and s.rotating == 0:
        letter(x + 3, y, 42)


def draw():
    if s.glow:
        face(3, s.glow)
    for i in range(9):
        card(1 + i % 3 * 6, 4 + i // 3 * 5, i)
    if s.phase == 1 and s.cursor < 9 and s.flying == 0:
        letter(s.cursor % 3 * 6, 6 + s.cursor // 3 * 5, 62)
        letter(6 + s.cursor % 3 * 6, 6 + s.cursor // 3 * 5, 60)
    if s.phase == 2:
        if s.axis == 0:
            letter(0, 6 + s.orbit * 5, 62)
            letter(18, 6 + s.orbit * 5, 60)
        else:
            letter(3 + s.orbit * 6, 3, 86)
            letter(3 + s.orbit * 6, 19, 94)
    if s.placed < 9:
        for i in range(2):
            if s.flying == 0 or i != s.offer:
                tile(23 + i * 4, 5, d[16 + i])
                letter(23 + i * 4, 7, 65 + d[16 + i])
        letter(23 + s.offer * 4, 8, 94)
    else:
        text(22, 5, "DECK END")
    if s.flying:
        tile(s.fx, s.fy, s.card)
    if s.level == 0:
        text(1, 1, "MAKE TWO MATCHING LINES")
        text(22, 11, "LINES")
    elif s.level == 1:
        text(1, 1, "MAKE A, B AND C LINES")
        text(22, 11, "ABC LINES")
    else:
        text(1, 1, "A ON BOTH DIAGONALS")
        text(22, 11, "A DIAGS")
    letter(24, 13, 48 + s.progress)
    letter(27, 13, 48 + s.target)
    for kind in range(3):
        letter(23 + kind * 3, 14, 65 + kind)
        if s.types & (1 << kind):
            letter(24 + kind * 3, 14, 42)
    letter(28, 17, 48 + s.placed)
    letter(28, 19, 48 + s.spins)
    if s.mode == 1:
        text(1, 21, "CARDS ROW>  COLV")
        if s.placed == 9:
            text(1, 21, "END  ")
        if s.phase == 1 and s.cursor >= 9:
            letter((s.cursor - 9) * 6, 21, 62)
        if s.notice == 1:
            text(0, 22, "NO SPINS LEFT")
        elif s.notice == 2:
            text(0, 22, "FULL: ROW/COL OR END")
        elif s.notice == 3:
            text(0, 22, "SAME CARDS: NO SPIN USED")
        elif s.gain:
            text(0, 22, "RESONANCE!")
        elif s.phase == 0:
            text(0, 22, "A/D PICK  RET SELECT  S BACK")
        elif s.phase == 1:
            text(0, 22, "WASD CELL/MENU  RET USE")
        elif s.axis == 0:
            text(0, 22, "W/S ROW  RET SHIFT  A/D BACK")
        else:
            text(0, 22, "A/D COL  RET SHIFT  W/S BACK")
