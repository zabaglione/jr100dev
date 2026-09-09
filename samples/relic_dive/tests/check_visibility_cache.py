"""Check cached native visibility against the original geometric line rule."""

import random

from check_game import reset_room, tile
from machine import SYMS, Machine


def visible(grid, px, py, tx, ty):
    x, y = px, py
    dx, dy = abs(tx - px), abs(ty - py)
    error = dx - dy
    while (x, y) != (tx, ty):
        if grid[y * 64 + x] in (0, 5):
            return False
        twice = error * 2
        if twice > -dy:
            error -= dy
            x += 1 if tx >= px else -1
        if twice < dx:
            error += dx
            y += 1 if ty >= py else -1
    return True


def check():
    m = Machine()
    rng = random.Random(6301)
    worst = 0
    for case in range(200):
        reset_room(m)
        grid = [rng.choice((0, 1, 1, 1, 5, 6, 7, 8, 9)) for _ in range(2048)]
        points = (
            (1, 1),
            (62, 1),
            (1, 30),
            (62, 30),
            (32, 16),
            (rng.randrange(1, 63), rng.randrange(1, 31)),
        )
        px, py = points[case % len(points)]
        grid[py * 64 + px] = 1
        for i in range(1024):
            m.set(SYMS["FLOORS"] + i, grid[2 * i] | grid[2 * i + 1] << 4)
        old = bytes(rng.randrange(256) for _ in range(256))
        for i, value in enumerate(old):
            m.set(SYMS["SEEN"] + i, value)
        m.set("G_X", px)
        m.set("G_Y", py)
        *_, cycles = m.call("UPDATE_VISIBILITY")
        worst = max(worst, cycles)
        expected = bytearray(256)
        for ty in range(max(0, py - 5), min(32, py + 6)):
            for tx in range(max(0, px - 5), min(64, px + 6)):
                if abs(tx - px) + abs(ty - py) <= 5 and visible(grid, px, py, tx, ty):
                    n = ty * 64 + tx
                    expected[n // 8] |= 1 << (n % 8)
        assert m.read("VISIBLE", 256) == expected, case
        assert m.read("SEEN", 256) == bytes(a | b for a, b in zip(old, expected)), case
        assert m.get("NEW_SIGHT") == sum(
            bin(b & ~a).count("1") for a, b in zip(old, expected)
        )
        frame = m.read("FRAMEBUFFER", 768)
        assert m.call("ENSURE_VISIBILITY")[3] < 200
        assert m.get("NEW_SIGHT") == 0
        assert m.read("FRAMEBUFFER", 768) == frame
        assert m.read("VISIBLE", 256) == expected
    reset_room(m)
    tile(m, 13, 12, 5)
    m.call("UPDATE_VISIBILITY")
    assert m.call("VISIBLE_CELL", 14, 12)[0] == 0
    tile(m, 13, 12, 1)
    assert m.get("VIS_DIRTY") == 1
    m.call("ENSURE_VISIBILITY")
    assert m.call("VISIBLE_CELL", 14, 12)[0] != 0
    m.set("G_X", 14)
    m.call("ENSURE_VISIBILITY")
    assert m.get("LAST_VIS_X") == 14
    m.close()
    return {"status": "passed", "cases": 200, "max_cycles": worst}


if __name__ == "__main__":
    print(check())
