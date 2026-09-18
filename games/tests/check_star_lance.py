"""Flight controls, heat risk, telegraphs and nonblocking destruction."""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "native")]
from checks import (
    KEYS,
    Machine,
    Model,
    assert_state,
    begin,
    controls,
    lib,
    render_bounds,
)
from star_lance.ai import choose


def constraints():
    r = Model("star_lance")
    r.env["strike"](0, 1)
    assert r.b[0] == 1 and r.s.left == 18 and r.b[32] == 6
    r.s.target, r.s.heat, r.s.jam = 0, 10, 20
    r.env["strike"](0, 1)
    assert r.b[0] == 0 and r.s.left == 17
    assert (r.s.target, r.s.heat, r.s.jam, r.s.notice) == (255, 6, 0, 16)
    r.env["strike"](1, 2)
    assert r.b[1] == 0 and r.s.left == 16

    r.init()
    r.s.wait = 255
    r.buttons = 16
    for _ in range(100):
        r.tick()
        if r.s.jam:
            break
    assert r.s.jam == 28 and r.s.heat == 12
    time, ship = r.s.time, r.s.ship
    for _ in range(10):
        heat, cool = r.s.heat, r.s.cool
        r.buttons = 17
        r.tick()
        assert r.s.heat <= heat and r.s.cool == max(0, cool - 1)
    assert r.s.time == time + 10 and r.s.ship == ship + 10
    r.buttons = 0
    for _ in range(30):
        r.tick()
    assert r.s.jam == r.s.heat == 0

    # A shallow diagonal reaches its fixed aim without jumping either axis.
    for x, y, aim in ((1, 15, 30), (30, 15, 1), (5, 5, 5), (15, 10, 18)):
        r.init()
        r.env["launch"](x, y, aim)
        previous = x, y
        while r.c[0]:
            r.env["bolts"]()
            current = r.c[8], r.c[0] or 20
            assert abs(current[0] - previous[0]) <= 1
            assert 0 <= current[1] - previous[1] <= 1
            previous = current
        assert r.c[8] == aim

    for level in range(6):
        r.init(level)
        r.buttons = 16
        for _ in range(1440):
            r.tick()
            if r.s.mode != 1:
                break
        assert r.s.mode == 3 and r.s.hp == 0 and r.s.left > 0, level
    print(
        "PASS: armour, interrupted attack/refund, overheat lock, aimed bolts, stationary fire loses six fleets"
    )


def continuous(rom=None):
    for pad in (False, True):
        m, r = begin("star_lance", rom)
        start = lib.clocks(m.p)
        positions = []
        for _ in range(10):
            controls(m, r, 17, pad)
            positions.append(r.s.ship)
        seconds = (lib.clocks(m.p) - start) / 894000
        assert positions == list(range(15, 25)) and seconds < 1.3
        assert r.s.time == 10 and any(r.d[:3])
        for _ in range(3):
            controls(m, r, 0, pad)
            assert r.s.ship == 24
        for _ in range(8):
            controls(m, r, 2, pad)
        assert r.s.ship == 16
        controls(m, r, 3, pad)
        assert r.s.ship == 16  # Opposed directions cancel.
        previous = r.s.shift
        for _ in range(12):
            controls(m, r, 0, pad)
            assert abs(r.s.shift - previous) <= 1
            previous = r.s.shift
        render_bounds(r)
        print(
            f"PASS: {'pad' if pad else 'keyboard'} hold, release, reverse, simultaneous shot, ten frames {seconds:.3f}s"
        )

    m = Machine("star_lance", rom)
    lib.key(m.p, *KEYS[5], 1)
    m.until("DISPATCH")
    m.until("FRAME_READY")
    r = Model("star_lance")
    r.s.action = 5
    assert_state(m, r)
    for _ in range(8):
        controls(m, r, 16, False)
        assert not any(r.d[:3]) and r.s.heat == 0
    controls(m, r, 0, False)
    controls(m, r, 16, False)
    assert any(r.d[:3])
    print("PASS: holding start does not fire until the button is released")


def defeat_animation(rom=None, capture=None):
    m, r = begin("star_lance", rom)
    bank = m.read(0xC000, 256)
    for _ in range(40):
        controls(m, r, choose(r))
        dead = next((i for i in range(24) if not r.b[i] and r.b[i + 32]), None)
        if dead is not None:
            break
    assert dead is not None
    x, y = r.b[dead + 64], r.b[dead + 96]
    cells = [0xC100 + y * 32 + x + offset for offset in (0, 1, 32, 33)]
    frames = []
    start, ship = r.s.time, r.s.ship
    for phase in range(7):
        if phase % 2 == 0:
            frames.append(bytes(m.get(address) for address in cells))
            if capture:
                m.capture(capture / f"vanish-{phase // 2}.png")
        assert m.read(0xC000, 256) == bank
        if phase < 6:
            controls(m, r, 1)
    assert len(set(frames)) == 4 and r.s.ship == ship + 6 and r.s.time == start + 6
    assert lib.audio_peak(m.p) > 0 and lib.min_sp(m.p) >= 0x3E00
    if rom:
        assert lib.host_mutations(m.p) == 0
    print(
        "PASS: four destruction phases while moving, fixed explosion position, PCM and unchanged shared PCG"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--capture", type=Path)
    args = parser.parse_args()
    rom = args.rom.read_bytes() if args.rom else None
    if args.capture:
        assert rom, "Published frames require the owned ROM"
        args.capture.mkdir(parents=True, exist_ok=True)
    continuous(rom)
    defeat_animation(rom, args.capture)
