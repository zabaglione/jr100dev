"""Compare streamed terrain against scalar packed-map decoding at camera edges."""

from check_game import reset_room
from machine import SYMS, Machine


def check():
    m = Machine()
    reset_room(m)
    terrain = (0, 1, 3, 4, 5, 6, 7, 8, 9)
    cells = [
        terrain[(x * 7 + y * 3) % len(terrain)] for y in range(32) for x in range(64)
    ]
    seen = bytes((0x55, 0x80, 0x01, 0, 255)[i % 5] for i in range(256))
    for i in range(1024):
        m.set(SYMS["FLOORS"] + i, cells[2 * i] | (cells[2 * i + 1] << 4))
    for i, value in enumerate(seen):
        m.set(SYMS["SEEN"] + i, value)
    glyphs = {0: 1, 1: 2, 3: 4, 4: 5, 5: 1, 6: 2, 7: 2, 8: 25, 9: 25}
    worst = 0
    cases = 0
    for vy in (0, 7, 12):
        for vx in range(33):
            m.set("G_X", vx + 16)
            m.set("G_Y", vy + 10)
            *_, cycles = m.call("RENDER_MAP")
            expected = bytearray()
            for y in range(vy, vy + 20):
                for x in range(vx, vx + 32):
                    n = y * 64 + x
                    tile = glyphs[cells[n]] if seen[n // 8] & (1 << (n % 8)) else 0
                    if (x, y) == (vx + 16, vy + 10):
                        tile = 6
                    expected.append(tile | 128)
            assert m.read(SYMS["FRAMEBUFFER"] + 64, 640) == expected, (vx, vy)
            worst = max(worst, cycles)
            cases += 1
    m.close()
    assert worst < 160000, worst
    return {"status": "passed", "cases": cases, "max_map_cycles": worst}


if __name__ == "__main__":
    print(check())
