# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    for i in range(25):
        b[i] = 4 if i % 5 > 0 and i % 5 < 4 or i // 5 > 0 and i // 5 < 4 else 1
    b[12] = 0
    s.cursor = 12
    s.selected = 255
    s.left = 20


def act():
    if s.action < 5:
        s.cursor = move(s.cursor, s.action, 5, 5)
    if s.action == 5:
        if s.selected == 255:
            if b[s.cursor] == 4:
                s.selected = s.cursor
        else:
            for a in range(4):
                mid = move(s.selected, a + 1, 5, 5)
                end = move(mid, a + 1, 5, 5)
                if (
                    mid != s.selected
                    and end != mid
                    and end == s.cursor
                    and b[mid] == 4
                    and b[end] == 0
                ):
                    b[mid] = 0
                    b[s.selected] = 0
                    s.jumping = 1
                    s.jump = s.selected
                    animate(3)
                    s.jump = mid
                    animate(6)
                    s.jump = end
                    animate(3)
                    b[end] = 4
                    s.jumping = 0
                    s.left -= 1
                    sound(1)
            s.selected = 255
            if s.left <= 5:
                win()


def tick():
    pass


def draw():
    for i in range(25):
        tile(2 + i % 5 * 3, 4 + i // 5 * 3, b[i])
    letter(1 + s.cursor % 5 * 3, 4 + s.cursor // 5 * 3, 62)
    number(24, 7, s.left)
    number(24, 13, 5)
    if s.selected != 255:
        letter(2 + s.selected % 5 * 3, 4 + s.selected // 5 * 3, 83)
    if s.jumping:
        tile(2 + s.jump % 5 * 3, 3 + s.jump // 5 * 3, 4)
