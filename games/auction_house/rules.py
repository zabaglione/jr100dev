# ruff: noqa: F821
def lot():
    offset = s.round * 5
    s.seed = (s.seed * 109 + 89) & 255
    s.market = s.seed % 3
    s.value = lots[offset] + s.market
    s.low = lots[offset + 1]
    s.high = lots[offset + 2] + 2
    s.limit = lots[offset + 3] + s.level
    s.bid = lots[offset + 4]
    s.choice = 0
    s.inspected = 0
    s.phase = 0


def init():
    s.origin = entropy()
    s.seed = s.origin ^ (s.level * 37)
    s.cash = 40
    s.goal = 58 + s.level * 2 - s.level // 2
    lot()


def settle():
    animate(36)
    s.round += 1
    if s.round == 6:
        if s.cash >= s.goal:
            win()
        else:
            lose("THE AUCTION ENDED BELOW TARGET")
    else:
        lot()


def act():
    if s.action < 5:
        s.choice = (s.choice + (3 if s.action == 1 or s.action == 3 else 1)) % 4
    if s.action == 5:
        if s.choice == 2:
            if not s.inspected and s.cash > 1:
                s.cash -= 1
                s.inspected = 1
                s.phase = 6
                sound(0)
                animate(18)
                s.low = s.value
                s.high = s.value
                sound(1)
            return
        if s.choice == 3:
            s.phase = 4
            sound(0)
            settle()
        elif s.cash >= s.bid + (6 if s.choice == 1 else 2):
            s.bid += 6 if s.choice == 1 else 2
            s.phase = 1
            sound(0)
            animate(16)
            if s.bid >= s.limit - (4 if s.choice == 1 else 0):
                s.phase = 3
                sound(1)
                for frame in range(3):
                    s.hammer = frame
                    animate(5)
                s.cash = min(99, s.cash - s.bid + s.value)
                s.won += 1
                settle()
            else:
                s.phase = 2
                s.bid += 2
                sound(2)
                animate(20)
        else:
            s.phase = 5
            sound(3)


def tick():
    pass


def draw():
    tile(4, 6, 4)
    tile(7, 4, 3)
    tile(9, 8, 4)
    if s.phase == 3:
        tile(4, 3 + s.hammer, 4)
    digits(23, 5, s.low)
    letter(25, 5, 45)
    digits(26, 5, s.high)
    digits(26, 9, s.bid)
    digits(26, 13, s.cash)
    digits(26, 17, s.won)
    text(1, 19, "BID +2  BID +6  INSPECT PASS")
    letter(1 + s.choice * 8, 20, 94)
    if s.phase == 1:
        text(1, 15, "YOUR BID")
    elif s.phase == 2:
        text(1, 15, "RIVAL +2")
    elif s.phase == 3:
        text(1, 15, "SOLD! VALUE")
        digits(5, 17, s.value)
    elif s.phase == 4:
        text(1, 15, "LOT PASSED")
    elif s.phase == 5:
        text(1, 15, "NO CASH")
    if s.phase == 6:
        text(1, 15, "APPRAISED")
    text(1, 22, "LOT  /6    CASH GOAL")
    digits(21, 22, s.goal)
    letter(5, 22, 48 + min(6, s.round + 1))
