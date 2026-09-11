# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.word = starts[s.level]
    s.goal = goals[s.level]


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 4, 4)
    if s.action == 5:
        diff = 0
        for i in range(3):
            if words[s.word * 3 + i] != words[s.cursor * 3 + i]:
                diff += 1
        if diff == 1:
            s.word = s.cursor
            s.steps += 1
            sound(1)
            if s.word == s.goal:
                win()
            elif s.steps == 8:
                lose()
        else:
            sound(3)


def draw():
    for i in range(3):
        letter(12 + i, 3, words[s.word * 3 + i])
        letter(26 + i, 3, words[s.goal * 3 + i])
    for i in range(16):
        for j in range(3):
            letter(2 + i % 4 * 8 + j, 8 + i // 4 * 3, words[i * 3 + j])
    letter(1 + s.cursor % 4 * 8, 8 + s.cursor // 4 * 3, 62)
    number(25, 20, s.steps)


def tick():
    pass
