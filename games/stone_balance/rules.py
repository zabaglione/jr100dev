# ruff: noqa: F821
# s, b, c, d and drawing functions are supplied by the native compiler.
def init():
    b[0] = 2 + s.level % 5
    b[1] = 3 + (s.level // 5) * 2
    b[2] = 7
    if ((b[0] % 4) ^ (b[1] % 4) ^ (b[2] % 4)) == 0:
        b[2] = 6
    s.take = 1


def remove(pile, count):
    for n in range(count):
        b[pile] -= 1
        sound(0)
        flight(2 + b[pile] * 3, 4 + pile * 5, 27, 18, 4)
    animate(12)


def act():
    if s.action == 1:
        s.pile = (s.pile + 2) % 3
    if s.action == 2:
        s.pile = (s.pile + 1) % 3
    if s.action == 3:
        s.take = 1 if s.take == 3 else s.take + 1
    if s.action == 4:
        s.take = 3 if s.take == 1 else s.take - 1
    if s.action == 5 and b[s.pile] >= s.take:
        s.turn = 1
        remove(s.pile, s.take)
        if b[0] + b[1] + b[2] == 0:
            win()
            return
        found = 0
        for i in range(3):
            for j in range(3):
                if not found and b[i] >= j + 1:
                    value = b[i]
                    b[i] -= j + 1
                    nim = (b[0] % 4) ^ (b[1] % 4) ^ (b[2] % 4)
                    b[i] = value
                    if nim == 0:
                        s.enemy_pile = i
                        s.enemy_take = j + 1
                        found = 1
        if not found:
            for i in range(3):
                if b[i]:
                    s.enemy_pile = i
            s.enemy_take = 1
        s.turn = 2
        remove(s.enemy_pile, s.enemy_take)
        sound(1)
        if b[0] + b[1] + b[2] == 0:
            lose("THE RIVAL TOOK THE LAST STONE")


def tick():
    pass


def draw():
    for i in range(3):
        for j in range(b[i]):
            tile(2 + j * 3, 4 + i * 5, 4)
        if i == s.pile:
            letter(0, 4 + i * 5, 62)
    text(2, 19, "TAKE")
    digits(8, 19, s.take)
    text(15, 19, "RIVAL TOOK")
    digits(26, 19, s.enemy_take)

    if s.turn == 1:
        text(2, 21, "YOU TAKE")
    elif s.turn == 2:
        text(2, 21, "RIVAL TOOK - YOUR TURN")
    effect_draw()
