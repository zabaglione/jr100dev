# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
"""Toggle a five-cell cross; extinguish every light on the five by five panel."""


def toggle(pos):
    b[pos] ^= 1
    if s.ready:
        s.flash = pos + 1
        sound(0)
        for frame in range(5):
            s.pose = frame + 1 if b[pos] else 5 - frame
            animate(2)
        s.flash = 0


def cross(pos):
    toggle(pos)
    if pos >= 5:
        toggle(pos - 5)
    if pos < 20:
        toggle(pos + 5)
    if pos % 5 > 0:
        toggle(pos - 1)
    if pos % 5 < 4:
        toggle(pos + 1)


def init():
    for i in range(4 + s.level // 3):
        cross((s.level * 7 + i * 11 + 3) % 25)

    s.ready = 1


def act():
    if s.action == 1 and s.cursor >= 5:
        s.cursor -= 5
    if s.action == 2 and s.cursor < 20:
        s.cursor += 5
    if s.action == 3 and s.cursor % 5 > 0:
        s.cursor -= 1
    if s.action == 4 and s.cursor % 5 < 4:
        s.cursor += 1
    if s.action == 5:
        cross(s.cursor)
        s.moves += 1
        sound(1)
        count = 0
        for i in range(25):
            count += b[i]
        if count == 0:
            win()
        elif s.moves >= 60:
            lose("SIXTY SWITCHES WERE NOT ENOUGH")


def tick():
    pass


def draw():
    if s.flash:
        flip(s.pose)
    for i in range(25):
        tile(
            1 + i % 5 * 3, 4 + i // 5 * 3, 6 if s.flash == i + 1 else (3 if b[i] else 0)
        )
    letter(s.cursor % 5 * 3, 4 + s.cursor // 5 * 3, 62)
    digits(23, 7, s.moves)
    digits(23, 13, 60 - s.moves)

    text(19, 16, "PAR")
    digits(24, 17, pars[s.level])
    if s.mode == 1:
        for pos in range(25):
            dx = (
                pos % 5 - s.cursor % 5
                if pos % 5 >= s.cursor % 5
                else s.cursor % 5 - pos % 5
            )
            dy = (
                pos // 5 - s.cursor // 5
                if pos // 5 >= s.cursor // 5
                else s.cursor // 5 - pos // 5
            )
            if dx + dy <= 1:
                letter(2 + pos % 5 * 3, 6 + pos // 5 * 3, 94)
    elif s.mode == 2 and s.moves <= pars[s.level]:
        text(2, 20, "PERFECT CIRCUIT")
