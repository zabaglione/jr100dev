# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def evaluate():
    pairs = 0
    largest = 0
    same = 1
    for i in range(5):
        count = 0
        for j in range(5):
            if b[i] == b[j]:
                count += 1
                if i < j:
                    pairs += 1
        d[i] = 1 if count > 1 else 0
        largest = max(largest, count)
        if c[i] != c[0]:
            same = 0
    s.points = 3
    s.hand = 0
    if pairs == 1:
        s.points = 8
        s.hand = 1
    if pairs >= 2:
        s.points = 16
        s.hand = 2
        if largest == 3:
            s.hand = 4 if pairs == 4 else 3
        if largest == 4:
            s.hand = 5
        if largest == 5:
            s.hand = 6
    if same:
        s.points = 25
        s.hand = 7
        for i in range(5):
            d[i] = 1


def deal():
    for i in range(5):
        b[i] = 1 + ((s.round * 3 + i * 5 + s.draws * 7) % 13)
        c[i] = (i + s.round + s.draws) % 4
    s.discards = 2
    s.scoring = 0
    evaluate()


def init():
    s.target = 25
    deal()


def act():
    if s.action == 3:
        s.cursor = (s.cursor + 4) % 5
    if s.action == 4:
        s.cursor = (s.cursor + 1) % 5
    if s.action == 1 and s.discards:
        s.flipping = 1
        sound(0)
        animate(6)
        s.flipping = 2
        animate(6)
        s.draws += 1
        b[s.cursor] = 1 + ((s.draws * 7 + s.cursor * 3 + s.round) % 13)
        c[s.cursor] = (s.draws + s.cursor) % 4
        s.discards -= 1
        s.flipping = 1
        animate(6)
        s.flipping = 0
        evaluate()
        animate(8)
    if s.action == 5:
        s.scoring = 1
        s.score += s.points
        sound(1)
        for flash in range(2):
            s.blink = 1
            animate(12)
            s.blink = 0
            animate(12)
        animate(60)
        s.round += 1
        if s.round == 3:
            if s.score >= s.target:
                win()
            else:
                lose("TOTAL BELOW 25")
        else:
            deal()


def tick():
    pass


def small_number(x, y, value):
    if value >= 10:
        letter(x, y, 48 + value // 10)
    letter(x + 1, y, 48 + value % 10)


def card(x, i):
    left = x
    right = x + 4
    if s.flipping and i == s.cursor:
        left += 1
        right -= 1
    if s.flipping == 2 and i == s.cursor:
        for y in range(7):
            letter(x + 2, 5 + y, 181)
    else:
        letter(left, 5, 176)
        letter(right, 5, 177)
        letter(left, 11, 178)
        letter(right, 11, 179)
        for dx in range(3):
            if left + dx + 1 < right:
                letter(left + dx + 1, 5, 180)
                letter(left + dx + 1, 11, 180)
        for dy in range(5):
            letter(left, 6 + dy, 181)
            letter(right, 6 + dy, 181)
        if s.flipping == 0 or i != s.cursor:
            small_number(x + 1, 6, b[i])
            tile(x + 1, 8, c[i])


def draw():
    for i in range(5):
        card(1 + i * 6, i)
        if d[i] and s.blink == 0:
            letter(3 + i * 6, 12, 42)
    if s.scoring == 0:
        letter(3 + s.cursor * 6, 4, 86)
    text(1, 2, "HAND")
    letter(6, 2, 48 + min(s.round + 1, 3))
    text(7, 2, "/3  * = MATCHING CARDS")
    if s.hand == 0:
        text(1, 14, "NO PAIR")
    elif s.hand == 1:
        text(1, 14, "ONE PAIR")
    elif s.hand == 2:
        text(1, 14, "TWO PAIRS")
    elif s.hand == 3:
        text(1, 14, "THREE OF A KIND")
    elif s.hand == 4:
        text(1, 14, "FULL HOUSE")
    elif s.hand == 5:
        text(1, 14, "FOUR OF A KIND")
    elif s.hand == 6:
        text(1, 14, "FIVE OF A KIND")
    else:
        text(1, 14, "FLUSH / SAME SUIT")
    text(24, 14, "+")
    small_number(25, 14, s.points)
    text(28, 14, "PTS")
    if s.scoring:
        text(1, 15, "HAND SCORED!")
    else:
        text(1, 15, "HAND READY")
    small_number(6, 18, s.score)
    small_number(16, 18, s.target)
    small_number(27, 18, s.discards)
