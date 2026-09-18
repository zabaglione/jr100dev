# ruff: noqa: F821
def shuffle():
    for i in range(52):
        d[i] = i
    for i in range(51):
        s.seed = (s.seed * 109 + 89) & 255
        j = s.seed % (52 - i)
        saved = d[51 - i]
        d[51 - i] = d[j]
        d[j] = saved
    s.drawn = 0


def total(who):
    value = 0
    aces = 0
    count = s.np if who == 0 else s.nd
    for i in range(count):
        rank = (b[i] if who == 0 else c[i]) % 13 + 1
        value += min(10, rank)
        if rank == 1:
            aces += 1
    if aces and value <= 11:
        value += 10
    return value


def deal(who):
    if s.drawn == 52:
        shuffle()
    value = d[s.drawn]
    s.drawn += 1
    count = s.np if who == 0 else s.nd
    if s.ready:
        sound(0)
        flight(14, 18, (0 if who == 0 else 17) + count % 3 * 5, 4 + count // 3 * 3, 7)
    if who == 0:
        b[count] = value
        s.np += 1
        s.player = total(0)
    else:
        c[count] = value
        s.nd += 1
        s.dealer = total(1)
    if s.ready:
        animate(8)


def hand():
    s.np = 0
    s.nd = 0
    s.player = 0
    s.dealer = 0
    s.result = 0
    s.choice = 0
    s.reveal = 0
    s.wager = 2
    deal(0)
    deal(1)
    deal(0)
    deal(1)


def init():
    s.origin = entropy()
    s.seed = s.origin
    s.coins = 10
    shuffle()
    hand()
    s.ready = 1


def finish():
    s.reveal = 1
    natural = s.player == 21 and s.np == 2
    dealer_natural = s.dealer == 21 and s.nd == 2
    if s.player <= 21 and (
        s.dealer > 21 or s.player > s.dealer or natural and not dealer_natural
    ):
        s.gain = 3 if natural else s.wager
        s.coins += s.gain
        s.result = 1
        sound(1)
    elif s.player > 21 or s.player < s.dealer or dealer_natural and not natural:
        s.coins -= s.wager
        s.result = 2 if s.player > 21 else 3
        sound(3)
    else:
        s.result = 4
        sound(0)
    animate(42)
    s.round += 1
    if s.coins < 2:
        lose("NO COINS LEFT AT THE TABLE")
    elif s.round == 7:
        if s.coins >= 12:
            win()
        else:
            lose("SEVEN HANDS ENDED BELOW 12")
    else:
        hand()


def stand():
    s.reveal = 1
    s.choice = 3
    animate(12)
    for i in range(9):
        if s.dealer < 17:
            deal(1)
    finish()


def act():
    if s.action < 5:
        s.choice = (s.choice + (2 if s.action == 1 or s.action == 3 else 1)) % 3
    if s.action == 5:
        if s.choice == 0:
            deal(0)
            if s.player > 21:
                finish()
        elif s.choice == 1:
            stand()
        elif s.np == 2 and s.coins >= 4:
            s.wager = 4
            deal(0)
            if s.player > 21:
                finish()
            else:
                stand()
        else:
            sound(3)


def tick():
    pass


def draw_card(x, y, value, shown):
    text(x, y, "+---+")
    text(x, y + 1, "[   ]")
    text(x, y + 2, "+---+")
    if not shown:
        text(x + 1, y + 1, "###")
        return
    rank = value % 13 + 1
    if rank == 1:
        letter(x + 1, y + 1, 65)
    elif rank <= 10:
        digits(x + 1, y + 1, rank)
    else:
        letter(x + 1, y + 1, 74 if rank == 11 else (81 if rank == 12 else 75))
    letter(x + 3, y + 1, 160 + value // 13)


def draw():
    for i in range(s.np):
        draw_card(i % 3 * 5, 3 + i // 3 * 3, b[i], 1)
    for i in range(s.nd):
        draw_card(17 + i % 3 * 5, 3 + i // 3 * 3, c[i], s.reveal or i == 0)
    digits(6, 16, s.player)
    if s.reveal:
        digits(25, 16, s.dealer)
    else:
        text(25, 16, "??")
    digits(7, 18, s.coins)
    letter(27, 18, 49 + min(6, s.round))
    if s.result == 1:
        text(6, 20, "YOU WIN! +")
        letter(16, 20, 48 + s.gain)
    elif s.result == 2:
        text(6, 20, "BUST! -")
        letter(13, 20, 48 + s.wager)
    elif s.result == 3:
        text(6, 20, "DEALER WINS -")
        letter(19, 20, 48 + s.wager)
    elif s.result == 4:
        text(6, 20, "PUSH - COINS STAY")
    elif s.choice == 3:
        text(6, 20, "DEALER DRAWS TO 17")
    else:
        text(2, 20, "HIT      STAND     DOUBLE")
        letter(1 + s.choice * 9, 20, 62)
    effect_draw()
