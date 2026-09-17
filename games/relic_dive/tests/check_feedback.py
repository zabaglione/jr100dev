"""Isolated victory sound fixture: timer mode, duration, input and VIA restore."""

from machine import KEYS, Machine, lib


def check():
    m = Machine()
    try:
        for mode in (0, 1):
            m.set("G_MODE", mode)
            assert m.call("END_FEEDBACK")[3] < 1000
        m.set("G_MODE", 9)
        m.call("RENDER_SCREEN")
        screen = m.read(0xC100, 768)
        # Nondefault T2 pulse mode must not stall the sound's timed hold.
        m.set(0xC80B, 0x20)
        m.set(0xC802, 0x20)
        lib.key(m.p, *KEYS[5], 1)
        lib.audio_peak(m.p)
        cycles = m.call("END_FEEDBACK")[3]
        seconds = cycles / 894886.25
        assert 1.85 < seconds < 2.05, seconds
        assert m.get(0xC80B) == 0x20 and m.get(0xC802) == 0x20
        assert m.get("G_MODE") == 9 and m.get("G_CLEAR_SUNG") == 1
        assert m.get("G_PENDING") == 0 and m.get("G_PREVIOUS") == 5
        assert m.read(0xC100, 768) == screen
        assert lib.audio_peak(m.p) > 0
        assert m.call("END_FEEDBACK")[3] < 1000, "Victory phrase repeated"
        m.set("G_MODE", 8)
        m.set("G_CLEAR_SUNG", 0)
        m.call("RENDER_SCREEN")
        screen = m.read(0xC100, 768)
        cycles = m.call("END_FEEDBACK")[3]
        assert 1.4 < cycles / 894886.25 < 1.6
        assert m.read(0xC100, 768) == screen
        assert m.get("G_PENDING") == 0 and m.get(0xC80B) == 0x20
        assert m.call("END_FEEDBACK")[3] < 1000, "Failure phrase repeated"
        return {"status": "passed", "seconds": round(seconds, 3), "via_restored": True}
    finally:
        m.close()


if __name__ == "__main__":
    print(check())
