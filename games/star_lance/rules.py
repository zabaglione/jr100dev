# ruff: noqa: F821
# b: hull, flash, explosion x/y. c: enemy bolts. d: player bolts.
def init():
    s.ship = 14
    s.hp = 3
    s.left = 18
    s.shift = 4
    s.direction = 1
    s.target = 255
    s.wait = 24
    for i in range(24):
        b[i] = (2 if i < 8 or s.level >= 3 and i < 16 else 1) if i % 8 < 6 else 0


def act():
    # Preserve taps until physics, and read held directions and fire together.
    if s.action == 3:
        s.tap |= 2
    if s.action == 4:
        s.tap |= 1
    if s.action == 5:
        s.tap |= 16
    if s.action == 1:
        s.tap |= 4


def fire(power):
    placed = 0
    for i in range(3):
        if not d[i] and not placed:
            d[i] = 19
            d[i + 8] = s.ship + 1
            d[i + 16] = power
            placed = 1
    if placed:
        s.cool = 4 if power == 1 else 7
        s.heat += 3 if power == 1 else 5
        sound(0 if power == 1 else 2)
        if s.heat >= 12:
            s.heat = 12
            s.jam = 28
            sound(3)


def strike(i, power):
    b[i] = b[i] - power if b[i] > power else 0
    b[i + 32] = 6
    b[i + 64] = s.shift + i % 8 * 4
    b[i + 96] = 3 + i // 8 * 3 + s.drop
    sound(1)
    if not b[i]:
        s.left -= 1
        if s.target == i:
            s.target = 255
            s.wait = 12
            s.heat = s.heat - 4 if s.heat > 4 else 0
            s.jam = 0
            s.notice = 16
            sound(4)


def shots():
    for i in range(3):
        if d[i]:
            d[i] -= 1
            if d[i + 8] >= s.shift and d[i] >= 3 + s.drop:
                x = d[i + 8] - s.shift
                y = d[i] - 3 - s.drop
                if x < 24 and x % 4 < 2 and y < 9 and y % 3 < 2:
                    enemy = y // 3 * 8 + x // 4
                    if b[enemy]:
                        strike(enemy, d[i + 16])
                        d[i] = 0


def launch(x, y, aim):
    placed = 0
    for i in range(6):
        if not c[i] and not placed:
            c[i] = y
            c[i + 8] = x
            c[i + 24] = aim - x if aim >= x else x - aim
            c[i + 16] = max(20 - y, c[i + 24])
            c[i + 32] = 1 if aim >= x else 255
            c[i + 40] = 0
            c[i + 48] = 20 - y
            c[i + 56] = 0
            placed = 1


def attack():
    if s.target == 255:
        if s.wait:
            s.wait -= 1
        else:
            best = 255
            for k in range(24):
                i = 23 - k
                x = s.shift + i % 8 * 4
                distance = x - s.ship if x >= s.ship else s.ship - x
                if b[i] and distance < best:
                    best = distance
                    s.target = i
            s.charge = 18 - s.level
            sound(5)
    else:
        s.charge -= 1
        if not s.charge:
            x = s.shift + s.target % 8 * 4 + 1
            y = 5 + s.target // 8 * 3 + s.drop
            launch(x, y, s.ship + 1)
            if s.level >= 2:
                launch(x, y, max(s.ship, 4) - 3)
                launch(x, y, min(s.ship + 5, 30))
            s.target = 255
            s.wait = 24 - s.level * 3
            sound(2)


def bolts():
    hit = 0
    for i in range(6):
        if c[i]:
            c[i + 56] += c[i + 48]
            if c[i + 56] >= c[i + 16]:
                c[i + 56] -= c[i + 16]
                c[i] += 1
            c[i + 40] += c[i + 24]
            # Bresenham steps: both axes advance by at most one character.
            if c[i + 40] >= c[i + 16]:
                c[i + 40] -= c[i + 16]
                c[i + 8] = (c[i + 8] + c[i + 32]) & 255
            if c[i + 8] > 30:
                c[i] = 0
            elif c[i] >= 20:
                if c[i + 8] >= s.ship and c[i + 8] <= s.ship + 1:
                    hit = 1
                c[i] = 0
    if hit and not s.shield:
        s.hp -= 1
        s.shield = 24
        sound(3)
        impact(s.ship, 20)


def tick():
    keys = buttons() | s.tap
    s.tap = 0
    s.time += 1
    s.age += 1
    if s.age == 240:
        s.age = 0
        s.drop += 1
    if s.cool:
        s.cool -= 1
    if s.jam:
        s.jam -= 1
    if s.heat and s.time % (2 if s.jam else 4) == 0:
        s.heat -= 1
    if s.notice:
        s.notice -= 1
    if s.shield:
        s.shield -= 1
    for i in range(24):
        if b[i + 32]:
            b[i + 32] -= 1
    if keys & 3 == 2 and s.ship > 1:
        s.ship -= 1
    if keys & 3 == 1 and s.ship < 29:
        s.ship += 1
    if not s.cool and not s.jam:
        if keys & 4:
            fire(2)
        elif keys & 16:
            fire(1)
    s.march += 1
    if s.march == 6:
        s.march = 0
        s.shift += 1 if s.direction else 255
        if s.shift == 1 or s.shift == 9:
            s.direction ^= 1
    shots()
    if s.left:
        attack()
        if s.time % 2 == 0:
            bolts()
        if not s.hp:
            lose("HIT BY ENEMY SHOT")
        elif s.drop == 6:
            lose("THE FLEET BROKE THROUGH")
    else:
        # Finish the final explosion before the clear jingle.
        s.finish += 1
        if s.finish == 7:
            win()


def draw():
    for i in range(24):
        x = s.shift + i % 8 * 4
        y = 3 + i // 8 * 3 + s.drop
        if b[i]:
            kind = 1 if b[i] > 1 else 0
            if b[i + 32] % 2 or s.target == i and s.charge % 4 < 2:
                kind = 3
            tile(x, y, kind)
        elif b[i + 32]:
            tile(b[i + 64], b[i + 96], 6 - (b[i + 32] - 1) // 2)
    if not s.shield or s.shield % 2 == 0:
        tile(s.ship, 20, 2)
    for i in range(3):
        if d[i]:
            letter(d[i + 8], d[i], 188 if d[i + 16] == 1 else 189)
    for i in range(6):
        if c[i]:
            letter(c[i + 8], c[i], 190 + s.time % 2)
    for i in range(s.hp):
        letter(6 + i, 22, 42)
    letter(18, 22, 48 + s.left // 10)
    letter(19, 22, 48 + s.left % 10)
    for i in range(s.heat):
        letter(7 + i, 23, 42)
    if s.jam:
        text(22, 23, "COOLING")
    elif s.notice:
        text(22, 23, "COOL +4")
    elif s.shield:
        text(22, 23, "HIT")
