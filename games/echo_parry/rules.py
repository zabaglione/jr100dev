# ruff: noqa: F821
def init():
    s.hp = 4
    s.enemy = 6 + s.level
    s.attack = pattern[s.level % 8]


def act():
    if s.action == 1:
        s.stance = 0
    if s.action == 2:
        s.stance = 1
    if s.action == 3 and s.phase < 2 and not s.guarded:
        s.evade = 1
        s.guarded = 1
        s.combo = 0
        sound(0)
        flight(5, 14 - s.stance * 3, 1, 14 - s.stance * 3, 2)
    if s.action == 5:
        if s.phase == 1 and s.stance == s.attack and not s.guarded:
            s.combo = min(3, s.combo + 1)
            damage = 2 if s.age == 1 or s.combo == 3 else 1
            s.enemy = s.enemy - damage if s.enemy >= damage else 0
            s.guarded = 1
            s.counter = damage
            sound(1)
            animate(8)
            flight(7, 14 - s.stance * 3, 24, 14 - s.attack * 3, 5)
            if s.enemy == 0:
                vanish(24, 14 - s.attack * 3)
                win()
            else:
                impact(24, 14 - s.attack * 3)
            s.counter = 0
        elif not s.guarded:
            s.hp -= 1
            s.combo = 0
            s.guarded = 1
            sound(3)
            impact(5, 14 - s.stance * 3)
            if s.hp == 0:
                lose("WRONG GUARD OR EARLY PARRY")


def tick():
    s.age += 1
    if s.phase == 0 and s.age == 2 and s.level >= 2 and s.turn % 3 == 1:
        s.attack ^= 1
        s.feint = 1
        sound(2)
        animate(12)
    if s.phase == 0 and s.age >= (4 if s.level < 4 else 3):
        s.phase = 1
        s.age = 0
        sound(2)
        flight(23, 14 - s.attack * 3, 7, 14 - s.attack * 3, 5)
    elif s.phase == 1 and s.age >= 2:
        if not s.guarded:
            s.hp -= 1
            s.combo = 0
            sound(3)
            impact(5, 14 - s.stance * 3)
            if s.hp == 0:
                lose("MISSED THE PARRY WINDOW")
                return
        s.phase = 2
        s.age = 0
    elif s.phase == 2 and s.age >= 3:
        s.phase = 0
        s.age = 0
        s.turn += 1
        s.attack = pattern[(s.turn + s.level * 3) % 8]
        s.guarded = 0
        s.evade = 0
        s.feint = 0


def draw():
    for i in range(s.enemy):
        letter(10 + i, 5, 42)
    if not s.evade:
        tile(5, 14 - s.stance * 3, 2)
    else:
        tile(1, 14 - s.stance * 3, 2)
    tile(24, 14 - s.attack * 3, 6)
    if s.phase == 0:
        if s.feint:
            text(11, 9, "FEINT")
        else:
            text(11, 9, "READY")
    if s.phase == 1:
        text(11, 9, "ATTACK")
        if s.age == 1:
            text(11, 11, "COUNTER!")
    if s.phase == 2:
        text(11, 9, "RECOVERY")
    digits(9, 19, s.hp)
    digits(25, 19, s.enemy)
    text(3, 2, "DUEL")
    text(3, 7, "CHAIN")
    letter(9, 7, 48 + s.combo)
    if s.counter:
        text(10, 13, "RIPOSTE +")
        letter(19, 13, 48 + s.counter)
    if s.evade:
        text(11, 13, "EVADED")
    effect_draw()
