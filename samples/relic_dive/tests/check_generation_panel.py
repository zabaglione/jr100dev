"""Observe actual new-game generation stages and removal of the central panel."""

from machine import Machine, lib


def check():
    m = Machine()
    m.resume()
    lib.pad(m.p, 16)
    for n, label in enumerate(
        ("BUILD_ROOMS", "ITEM_COUNT_READY", "POPULATION_READY", "GEN_EXTRAS_READY"), 1
    ):
        m.until(label)
        expected = bytes(
            0x40 if c == 32 else c - 32 for c in f"[ BUILDING {n}/4 ]".encode()
        )
        assert m.read(0xC268, 16) == expected
        assert m.read(0xC248, 16) == bytes([0x40]) * 16
        assert m.read(0xC288, 16) == bytes([0x40]) * 16
    m.until("FRAME_READY")
    assert m.get("G_MODE") == 1
    assert m.read(0xC268, 16) != expected
    m.close()
    return {"status": "passed", "stages": 4}


if __name__ == "__main__":
    print(check())
