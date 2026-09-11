# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def deal():
    for i in range(5):
        b[i] = 1 + ((s.round * 3 + i * 5 + s.draws * 7) % 13)
        c[i] = (i + s.round + s.draws) % 4
    s.discards = 2


def init():
    s.target = 25
    deal()


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 4) % 5
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 5
    if s.action == 1 and s.discards:
        s.draws += 1
        b[s.cursor] = 1 + ((s.draws * 7 + s.cursor * 3 + s.round) % 13)
        c[s.cursor] = (s.draws + s.cursor) % 4
        s.discards -= 1
        sound(0)
    if s.action == 5:
        points = 3
        pairs = 0
        for i in range(5):
            for j in range(5):
                if i < j and b[i] == b[j]:
                    pairs += 1
        if pairs == 1:
            points = 8
        if pairs >= 2:
            points = 16
        same = 1
        for i in range(5):
            if c[i] != c[0]:
                same = 0
        if same:
            points = 25
        s.score += points
        s.round += 1
        sound(1)
        if s.round == 3:
            if s.score >= s.target:
                win()
            else:
                lose()
        else:
            deal()


def tick():
    pass


def draw():
    for i in range(5):
        tile(1 + i * 6, 6, 7)
        number(1 + i * 6, 8, b[i])
        letter(1 + i * 6, 11, 65 + c[i])
    letter(1 + s.cursor * 6, 4, 86)
    number(6, 16, s.score)
    number(16, 16, s.target)
    number(27, 16, s.discards)
