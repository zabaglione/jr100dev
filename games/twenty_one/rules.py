# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def card():
    s.seed = (s.seed * 5 + 1) & 255
    return 2 + s.seed % 9


def hand():
    s.player = card()
    s.player += card()
    s.dealer = card()
    s.choice = 0


def init():
    s.seed = 17
    s.coins = 6
    hand()


def finish():
    if s.player <= 21 and (s.dealer > 21 or s.player > s.dealer):
        s.coins += 2
    elif s.player > 21 or s.player < s.dealer:
        s.coins -= 2
    s.round += 1
    if s.coins == 0:
        lose()
    elif s.round == 5:
        if s.coins >= 8:
            win()
        else:
            lose()
    else:
        hand()


def act():
    if s.action < 5:
        s.choice ^= 1
    if s.action == 5:
        if s.choice == 0:
            s.player += card()
            if s.player > 21:
                finish()
        else:
            for i in range(8):
                if s.dealer < 17:
                    s.dealer += card()
            finish()
        sound(1)


def tick():
    pass


def draw():
    tile(4, 5, 7)
    tile(7, 5, 7)
    tile(21, 5, 7)
    number(5, 9, s.player)
    number(21, 9, s.dealer)
    number(14, 14, s.coins)
    number(26, 17, s.round)
    letter(5 + s.choice * 15, 20, 62)
