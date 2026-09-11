# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    s.culprit = (s.level * 5 + 2) % 6
    s.file = 0


def act():
    if s.action == 1 or s.action == 2:
        s.mode_choice ^= 1
    if s.action == 3:
        s.choice = (s.choice + 5) % 6
    if s.action == 4:
        s.choice = (s.choice + 1) % 6
    if s.action == 5:
        if s.mode_choice:
            if s.choice == s.culprit:
                win()
            else:
                lose()
        else:
            s.file = s.choice % 3
            c[s.file] = 1
            sound(1)


def tick():
    pass


def draw():
    for i in range(6):
        tile(2 + i % 3 * 5, 5 + i // 3 * 6, 2)
        letter(2 + i % 3 * 5, 8 + i // 3 * 6, 65 + i)
    letter(1 + s.choice % 3 * 5, 5 + s.choice // 3 * 6, 62)
    text(19, 4, "FILE NOTES")
    if c[0]:
        text(18, 7, "FLOOR")
        number(26, 7, 1 + s.culprit // 3)
    if c[1]:
        text(18, 11, "BADGE MOD3")
        number(25, 12, s.culprit % 3)
    if c[2]:
        text(18, 16, "BADGE MOD2")
        number(25, 17, s.culprit % 2)
    if s.mode_choice:
        text(2, 19, "ACCUSE THE SELECTED SUSPECT")
    else:
        text(2, 19, "READ THE SELECTED FILE")
