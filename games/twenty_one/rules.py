# ruff: noqa: F821
def card():
    s.seed = (s.seed * 5 + 1) & 255
    return 2 + s.seed % 9


def deal(who):
    value = card()
    count = s.np if who == 0 else s.nd
    if s.ready:
        sound(0)
        flight(14, 18, (1 if who == 0 else 17) + count % 3 * 5, 4 + count // 3 * 3, 7)
    if who == 0:
        b[count] = value
        s.np += 1
        s.player += value
    else:
        c[count] = value
        s.nd += 1
        s.dealer += value
    if s.ready:
        animate(12)


def hand():
    s.np = 0
    s.nd = 0
    s.player = 0
    s.dealer = 0
    s.result = 0
    s.choice = 0
    deal(0)
    deal(1)
    deal(0)


def init():
    s.seed = 17
    s.coins = 6
    hand()
    s.ready = 1


def finish():
    if s.player <= 21 and (s.dealer > 21 or s.player > s.dealer):
        s.coins += 2
        s.result = 1
        sound(1)
    elif s.player > 21 or s.player < s.dealer:
        s.coins -= 2
        s.result = 2 if s.player > 21 else 3
        sound(3)
    else:
        s.result = 4
        sound(0)
    animate(45)
    s.round += 1
    if s.coins == 0:
        lose("NO COINS LEFT AT THE TABLE")
    elif s.round == 5:
        if s.coins >= 8:
            win()
        else:
            lose("FIVE HANDS ENDED BELOW 8 COINS")
    else:
        hand()


def act():
    if s.action < 5:
        s.choice ^= 1
    if s.action == 5:
        if s.choice == 0:
            deal(0)
            if s.player > 21:
                finish()
        else:
            s.choice = 2
            for i in range(8):
                if s.dealer < 17:
                    deal(1)
            finish()


def tick():
    pass


def draw_card(x, y, value):
    text(x, y, "----")
    letter(x, y + 1, 91)
    if value == 10:
        digits(x + 1, y + 1, value)
    else:
        letter(x + 1, y + 1, 32)
        letter(x + 2, y + 1, 48 + value)
    letter(x + 3, y + 1, 93)
    text(x, y + 2, "____")


def draw():
    for i in range(s.np):
        draw_card(0 + i % 3 * 5, 3 + i // 3 * 3, b[i])
    for i in range(s.nd):
        draw_card(17 + i % 3 * 5, 3 + i // 3 * 3, c[i])
    digits(6, 16, s.player)
    digits(25, 16, s.dealer)
    digits(7, 18, s.coins)
    letter(27, 18, 49 + s.round)
    if s.result == 1:
        text(6, 20, "YOU WIN! +2 COINS")
    elif s.result == 2:
        text(6, 20, "BUST!    -2 COINS")
    elif s.result == 3:
        text(6, 20, "DEALER WINS   -2")
    elif s.result == 4:
        text(6, 20, "PUSH - COINS STAY")
    elif s.choice == 2:
        text(6, 20, "DEALER DRAWS TO 17")
    else:
        text(6, 20, "HIT          STAND")
        letter(4 + s.choice * 13, 20, 62)
    effect_draw()
