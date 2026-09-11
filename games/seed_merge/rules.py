# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def index(line, offset, action):
    if action == 1:
        return offset * 4 + line
    if action == 2:
        return (3 - offset) * 4 + line
    if action == 3:
        return line * 4 + offset
    return line * 4 + 3 - offset


def spawn():
    s.seed = (s.seed * 5 + 1) & 255
    for i in range(16):
        p = (s.seed + i) % 16
        if b[p] == 0:
            b[p] = 1
            return


def init():
    s.seed = 7
    spawn()
    spawn()
    s.best = 1


def settle():
    changed = 0
    for step in range(3):
        moved = 0
        for line in range(4):
            for i in range(3):
                p = index(line, i, s.action)
                n = index(line, i + 1, s.action)
                if not b[p] and b[n]:
                    b[p] = b[n]
                    b[n] = 0
                    moved = 1
                    changed = 1
        if moved:
            animate(3)
    return changed


def act():
    if s.action >= 5:
        return
    changed = settle()
    merged = 0
    for line in range(4):
        for i in range(3):
            p = index(line, i, s.action)
            n = index(line, i + 1, s.action)
            if b[p] and b[p] == b[n]:
                b[p] += 1
                b[n] = 0
                merged = 1
                changed = 1
                if b[p] > s.best:  # noqa: PLR1730 - native DSL has no max()
                    s.best = b[p]
    if merged:
        sound(1)
        animate(8)
    changed |= settle()
    if changed:
        spawn()
        s.moves += 1
        sound(1)
        animate(4)
    possible = 0
    for i in range(16):
        if b[i] == 0:
            possible = 1
        for a in range(4):
            n = move(i, a + 1, 4, 4)
            if n != i and b[i] == b[n]:
                possible = 1
    if s.best >= 6:
        win()
    elif not possible:
        lose()


def tick():
    pass


def draw():
    for i in range(16):
        if b[i]:
            number(1 + i % 4 * 5, 5 + i // 4 * 4, 1 << b[i])
    number(26, 7, 1 << s.best)
    number(26, 14, s.moves)
