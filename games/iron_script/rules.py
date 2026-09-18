# ruff: noqa: F821
# Eight byte-sized instructions; the program survives every failed run.
# Map: floor, wall, robot, goal, switch, sentry, door, laser, armored sentry.
def reset_world():
    for i in range(64):
        b[i] = d[i]
    s.pos = d[64]
    s.origin = s.pos
    s.facing = d[65]
    s.ammo = d[66]
    s.gate = 0
    s.door_pose = 1
    s.steps = 0
    s.pc = 0
    s.sub = 0
    s.notice = 0
    s.beam = 255


def init():
    reset_world()


def stop(reason):
    s.notice = reason
    s.running = 0
    s.cursor = min(s.pc, d[67] - 1)
    sound(3)
    animate(40)


def act():
    if s.running:
        if s.action == 5:
            stop(9)
        return
    if s.action == 3 and s.cursor > 0:
        s.cursor -= 1
    if s.action == 4 and s.cursor < d[67] - 1:
        s.cursor += 1
    if s.action == 1:
        c[s.cursor] = (c[s.cursor] + 1) & 7
    if s.action == 2:
        c[s.cursor] = (c[s.cursor] + 7) & 7
    if s.action < 5:
        sound(0)
    if s.action == 5:
        reset_world()
        s.running = 1
        reschedule()


def shoot():
    if s.ammo == 0:
        stop(5)
        return
    s.ammo -= 1
    target = s.pos
    sound(1)
    for ray_step in range(7):
        target = move(target, s.facing, 8, 8)
        if b[target] == 1 or (b[target] == 6 and not s.gate):
            s.beam = 255
            return
        s.beam = target
        animate(3)
        if b[target] == 5 or b[target] == 8:
            if b[target] == 8:
                b[target] = 5
                s.notice = 10
                impact(target % 8 * 2, 3 + target // 8 * 2)
            else:
                b[target] = 0
                s.notice = 11
                vanish(target % 8 * 2, 3 + target // 8 * 2)
            s.beam = 255
            return
    s.beam = 255


def tick():
    if not s.running:
        return
    s.active = s.pc
    if c[s.pc] == 7:
        if s.pc < 2 or c[s.pc - 1] == 7 or c[s.pc - 2] == 7:
            stop(7)
            return
        s.active = s.pc - 2 + s.sub
    command = c[s.active]
    s.steps += 1
    s.notice = 0
    if command > 0 and command < 5:
        s.facing = command
        target = move(s.pos, command, 8, 8)
        obstacle = b[target]
        if (
            obstacle == 1
            or obstacle == 5
            or obstacle == 8
            or (obstacle == 6 and not s.gate)
        ):
            s.notice = 1 if obstacle == 1 else (3 if obstacle == 6 else 2)
            impact(target % 8 * 2, 3 + target // 8 * 2)
            stop(s.notice)
            return
        s.origin = s.pos
        s.pos = target
        sound(0)
        animate(5)
        s.origin = s.pos
    elif command == 5:
        shoot()
    elif command == 6:
        if b[s.pos] != 4:
            stop(6)
            return
        s.gate = 1 - s.gate
        s.notice = 12
        sound(1)
        for frame in range(3):
            s.door_pose = frame + 2 if s.gate else 3 - frame
            animate(5)
    else:
        sound(0)
        animate(5)
    if not s.running:
        return
    if b[s.pos] == 7 and (s.steps + d[68]) & 1:
        s.notice = 4
        impact(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
        stop(4)
        return
    if b[s.pos] == 3:
        s.running = 0
        sparkle(s.pos % 8 * 2, 3 + s.pos // 8 * 2)
        win()
        return
    if c[s.pc] == 7 and s.sub == 0:
        s.sub = 1
    else:
        s.sub = 0
        s.pc += 1
    if s.pc >= d[67]:
        stop(8)


def draw():
    face(2, s.facing)
    face(6, s.door_pose)
    for i in range(64):
        x = i % 8 * 2
        y = 3 + i // 8 * 2
        kind = b[i]
        if kind == 8:
            kind = 5
        if kind == 7 and not ((s.steps + d[68]) & 1):
            kind = 0
        tile(x, y, kind)
        if b[i] == 8:
            letter(x + 1, y, 50)
        if b[i] == 7 and kind == 0:
            letter(x, y, 46)
            letter(x + 1, y + 1, 46)
    mover(s.pos, s.origin, 2, 0)
    if s.beam != 255:
        letter(s.beam % 8 * 2, 3 + s.beam // 8 * 2, 42)
    digits(23, 3, s.ammo)
    digits(26, 9, d[67])
    letter(29, 3, icons[s.facing])
    if s.gate:
        text(23, 5, "OPEN")
    else:
        text(23, 5, "LOCK")
    if (s.steps + d[68]) & 1:
        text(22, 7, "OFF")
    else:
        text(22, 7, "ON!")
    current = s.pc if s.running else s.cursor
    for i in range(12):
        x = 19 + i % 4 * 3
        y = 11 + i // 4 * 3
        letter(x, y, icons[c[i]] if i < d[67] else 88)
    letter(18 + current % 4 * 3, 11 + current // 4 * 3, 105)
    for i in range(8):
        letter(1 + i, 20, names[c[min(current, 11)] * 8 + i])
    digits(26, 20, s.steps)
    if s.running and not s.notice:
        if c[s.pc] == 7:
            text(1, 21, "REPLAY PAIR")
        else:
            text(1, 21, "EXECUTING")
    else:
        for i in range(16):
            letter(1 + i, 21, messages[s.notice * 16 + i])
    effect_draw()
