# ruff: noqa: F821
# The native compiler supplies state, arrays and drawing functions.
def gate(a, b, kind):
    if kind == 0:
        return a & b
    if kind == 1:
        return a | b
    return a ^ b


def output(a, b, c, p, q, r):
    first = gate(a, b, p)
    second = gate(first, c, q)
    return gate(second, a, r)


def init():
    for i in range(8):
        d[i] = output(
            i // 4,
            i // 2 % 2,
            i % 2,
            targets[s.level * 3],
            targets[s.level * 3 + 1],
            targets[s.level * 3 + 2],
        )
    s.probe = 255
    s.running = 255


def act():
    if s.action == 1:
        s.cursor = (s.cursor + 2) % 3
    if s.action == 2:
        s.cursor = (s.cursor + 1) % 3
    if s.action == 3:
        c[s.cursor] = (c[s.cursor] + 2) % 3
    if s.action == 4:
        c[s.cursor] = (c[s.cursor] + 1) % 3
    if s.action == 5:
        s.correct = 0
        s.tested = 0
        for i in range(8):
            s.probe = i
            s.signal = i // 4
            for stage in range(3):
                s.running = stage
                operand = (
                    i // 2 % 2 if stage == 0 else (i % 2 if stage == 1 else i // 4)
                )
                s.signal = gate(s.signal, operand, c[stage])
                sound(0)
                for pulse in range(3):
                    s.pulse = pulse
                    animate(2)
            b[i] = s.signal
            s.tested += 1
            if b[i] == d[i]:
                s.correct += 1
            animate(4)
        s.running = 255
        s.probe = 255
        s.tests = min(s.tests + 1, 99)
        sound(1 if s.correct == 8 else 3)
        animate(12)
        if s.correct == 8:
            win()


def tick():
    pass


def draw():
    for i in range(3):
        tile(4, 5 + i * 4, 6)
        if c[i] == 0:
            text(8, 5 + i * 4, "AND")
        elif c[i] == 1:
            text(8, 5 + i * 4, "OR ")
        else:
            text(8, 5 + i * 4, "XOR")
        letter(7, 6 + i * 4, 66 if i == 0 else (67 if i == 1 else 65))
        for wire in range(3):
            letter(5, 7 + i * 4 + wire, 145)
        letter(7, 5 + i * 4, 62)
        if s.running == i:
            letter(12, 5 + i * 4, 48 + s.signal)
            letter(3, 5 + i * 4, 42)
            letter(5, 7 + i * 4 + s.pulse, 48 + s.signal)
    letter(1, 5 + s.cursor * 4, 62)
    for i in range(8):
        letter(17, 4 + i * 2, 48 + i // 4)
        letter(19, 4 + i * 2, 48 + i // 2 % 2)
        letter(21, 4 + i * 2, 48 + i % 2)
        letter(25, 4 + i * 2, 48 + d[i])
        if i < s.tested:
            letter(29, 4 + i * 2, 48 + b[i])
            letter(31, 4 + i * 2, 42 if b[i] == d[i] else 88)
        if s.probe == i:
            letter(16, 4 + i * 2, 62)
    digits(9, 20, s.tests)
    digits(25, 20, s.correct)
