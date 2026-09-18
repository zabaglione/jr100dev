# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.word = starts[s.level]
    s.goal = goals[s.level]
    d[0] = s.word


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5:
        diff = 0
        for i in range(3):
            if words[s.word * 3 + i] != words[s.cursor * 3 + i]:
                diff += 1
        if diff == 1:
            s.old = s.word
            s.changing = 1
            for frame in range(3):
                s.lift = frame
                sound(0)
                animate(4)
            s.word = s.cursor
            s.changing = 0
            s.steps += 1
            d[s.steps] = s.word
            sound(1)
            if s.word == s.goal:
                win()
            elif s.steps == 8:
                lose("EIGHT WORD CHANGES USED")
        else:
            sound(3)


def draw():
    for i in range(3):
        letter(12 + i, 3, words[s.word * 3 + i])
        letter(26 + i, 3, words[s.goal * 3 + i])
    for i in range(16):
        diff = 0
        for j in range(3):
            if words[s.word * 3 + j] != words[i * 3 + j]:
                diff += 1
        if diff == 1:
            letter(6 + i % 4 * 8, 8 + i // 4 * 3, 42)
        for j in range(3):
            letter(2 + i % 4 * 8 + j, 8 + i // 4 * 3, words[i * 3 + j])
    letter(1 + s.cursor % 4 * 8, 8 + s.cursor // 4 * 3, 62)
    digits(25, 20, s.steps)
    text(1, 6, "* = ONE LETTER CAN CHANGE")
    for i in range(min(s.steps + 1, 8)):
        for j in range(3):
            letter(i * 4 + j, 19, words[d[i] * 3 + j])
    if s.changing:
        for i in range(3):
            if words[s.old * 3 + i] != words[s.cursor * 3 + i]:
                letter(12 + i, 4 + s.lift, words[s.cursor * 3 + i])


def tick():
    pass
