"""Input-only demonstration: line up a shot, release to cool, and dodge bolts."""


def formation(s, frames):
    x, direction, phase = s.shift, s.direction, s.march
    for _ in range(frames):
        phase += 1
        if phase == 6:
            phase = 0
            x += 1 if direction else -1
            if x in (1, 9):
                direction ^= 1
    return x


def landing_zones(r):
    danger = set()
    for i in range(6):
        if not r.c[i]:
            continue
        y, x = r.c[i], r.c[i + 8]
        ex, ey = r.c[i + 40], r.c[i + 56]
        for _ in range(5):
            ex += r.c[i + 24]
            ey += r.c[i + 48]
            if ex >= r.c[i + 16]:
                ex -= r.c[i + 16]
                x += 1 if r.c[i + 32] == 1 else -1
            if ey >= r.c[i + 16]:
                ey -= r.c[i + 16]
                y += 1
            if y >= 20:
                danger.update((x - 1, x))
                break
    return danger


def choose(r):
    s = r.s
    danger = landing_zones(r)
    targets = []
    for col in range(6):
        enemy = next((row * 8 + col for row in (2, 1, 0) if r.b[row * 8 + col]), None)
        if enemy is None:
            continue
        flight = 18 - (4 + enemy // 8 * 3 + s.drop)
        x = formation(s, flight + 1) + col * 4
        # The cannon is the right half of the two-character interceptor.
        goal = min((x - 1, x), key=lambda v: abs(v - s.ship))
        goal = max(1, min(29, goal))
        priority = abs(goal - s.ship) - (5 if enemy == s.target else 0)
        targets.append((priority, enemy, goal, x))
    if not targets:
        return 0
    _, enemy, goal, aim = min(targets)
    if s.ship in danger or goal in danger and abs(goal - s.ship) < 2:
        safe = [x for x in range(1, 30) if x not in danger]
        goal = min(safe, key=lambda x: abs(x - s.ship) * 3 + abs(x - goal))
    move = 1 if s.ship < goal else 2 if s.ship > goal else 0
    next_x = s.ship + (1 if move == 1 else -1 if move == 2 else 0)
    shot = 0
    if (
        not any(r.d[:3])
        and not s.jam
        and not s.cool
        and next_x not in danger
        and aim <= next_x + 1 <= aim + 1
    ):
        power = 2 if r.b[enemy] > 1 else 1
        if s.heat + (5 if power == 2 else 3) < 12:
            shot = 4 if power == 2 else 16
    return move | shot
