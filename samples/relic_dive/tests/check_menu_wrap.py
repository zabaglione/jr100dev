"""Exercise cyclic selection and BACK through real keyboard/pad input."""

from check_game import reset_room
from machine import Machine


def check():
    cases = 0
    for pad in (False, True):
        for mode, context, item, last, back_mode in (
            (2, 0, 7, 6, 1),
            (2, 1, 7, 7, 1),
            (3, 0, 7, 6, 2),
            (4, 0, 7, 2, 3),
            (4, 0, 10, 2, 3),
            (4, 0, 17, 2, 3),
            (4, 0, 21, 2, 3),
        ):
            m = Machine()
            reset_room(m)
            m.set("G_MODE", mode)
            if context:
                m.call("CELL", 12, 12)
                m.call("WRITE_CELL", 3)
            m.set("G_BAG", item)
            m.call("RENDER_SCREEN")
            m.resume()
            turns = m.word("G_TURNS")
            m.action(1, pad)
            assert m.get("G_MENU") == last
            m.action(2, pad)
            assert m.get("G_MENU") == 0
            for index in range(1, last + 1):
                m.action(2, pad)
                assert m.get("G_MENU") == index
            m.action(2, pad)
            assert m.get("G_MENU") == 0
            m.action(1, pad)
            m.action(5, pad)
            assert m.get("G_MODE") == back_mode
            assert m.word("G_TURNS") == turns
            m.close()
            cases += 1
        m = Machine()
        m.set("G_DIFFICULTY", 0)
        m.resume()
        m.action(1, pad)
        assert m.get("G_DIFFICULTY") == 2
        m.action(2, pad)
        assert m.get("G_DIFFICULTY") == 0
        m.action(2, pad)
        assert m.get("G_DIFFICULTY") == 1
        m.close()
        cases += 1
    return {"status": "passed", "cases": cases}


if __name__ == "__main__":
    print(check())
