# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def lot():
    s.value = 18 + (s.round * 7) % 15
    s.limit = s.value - 4 + (s.round % 3)
    s.bid = 4
    s.choice = 0


def init():
    s.cash = 40
    lot()


def settle():
    s.round += 1
    if s.round == 6:
        if s.cash >= 52:
            win()
        else:
            lose()
    else:
        lot()


def act():
    if s.action < 5:
        s.choice ^= 1
    if s.action == 5:
        if s.choice:
            settle()
        elif s.cash >= s.bid + 2:
            s.bid += 2
            if s.bid >= s.limit:
                s.cash = s.cash - s.bid + s.value
                s.won += 1
                sound(1)
                settle()
            else:
                s.bid += 2
                sound(0)


def tick():
    pass


def draw():
    tile(4, 6, 4)
    tile(7, 4, 3)
    tile(9, 8, 4)
    number(25, 5, s.value)
    number(25, 9, s.bid)
    number(25, 13, s.cash)
    number(25, 17, s.won)
    letter(5 + s.choice * 13, 20, 62)
