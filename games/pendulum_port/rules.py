# ruff: noqa: F821
def port():
    s.target = 4 + (s.ports * 7 + s.level * 3 + 6) % 9
    s.width = 1 if s.level < 3 or s.ports % 3 else 0
    s.swing = 0
    s.direction = 1


def init():
    s.hp = 3
    s.rope = 2
    port()


def landing():
    return (
        min(15, s.swing + s.rope)
        if s.direction
        else (s.swing - s.rope if s.swing >= s.rope else 0)
    )


def act():
    if s.action == 3 and s.rope > 1:
        s.rope -= 1
        sound(0)
    if s.action == 4 and s.rope < 3:
        s.rope += 1
        sound(0)
    if s.action == 5:
        s.dest = landing()
        s.airborne = 1
        sound(0)
        flight(s.swing * 2, 13, s.swing + s.dest, 8, 2)
        flight(s.swing + s.dest, 8, s.dest * 2, 16, 2)
        s.airborne = 2
        if s.dest + s.width >= s.target and s.dest <= s.target + s.width:
            s.score += 2 if s.dest == s.target else 1
            sound(1)
            sparkle(s.dest * 2, 16)
            animate(16)
            s.ports += 1
            if s.ports == 6 + s.level:
                win()
            else:
                port()
        else:
            s.hp -= 1
            flight(s.dest * 2, 16, s.dest * 2, 20, 2)
            impact(s.dest * 2, 20)
            sound(3)
            if s.hp == 0:
                lose("THE JUMP MISSED THE PORT")
        s.airborne = 0


def tick():
    if s.swing == 15:
        s.direction = 0
    if s.swing == 0:
        s.direction = 1
    s.swing = s.swing + 1 if s.direction else s.swing - 1


def draw():
    tile(14, 3, 6)
    for i in range(8):
        x = (
            15 + (s.swing * 2 - 15) * i // 8
            if s.swing * 2 >= 15
            else 15 - (15 - s.swing * 2) * i // 8
        )
        letter(x, 5 + i, 145)
    if s.airborne == 0:
        tile(s.swing * 2, 13, 2)
    elif s.airborne == 2:
        tile(s.dest * 2, 16, 2)
    for i in range(1 + s.width * 2):
        tile((s.target - s.width + i) * 2, 18, 4)
    tile(s.target * 2, 18, 3)
    letter(landing() * 2, 17, 86)
    text(0, 2, "ROPE")
    letter(5, 2, 48 + s.rope)
    letter(8, 2, 62 if s.direction else 60)
    text(19, 2, "CENTRE")
    digits(27, 2, s.score)
    digits(9, 20, s.hp)
    digits(25, 20, s.ports)
    effect_draw()
