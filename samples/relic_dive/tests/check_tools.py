"""Native wand/ring regressions, including persistence and one-button targeting."""

from check_game import enemy, reset_room
from machine import SYMS, Machine


def check():
    m = Machine()
    reset_room(m)
    m.set("G_BAG", 17)
    m.call("USE_ITEM")
    assert m.get("G_MODE") == 5 and m.get("G_WAND_SLOT") == 1
    assert m.get("G_BAG") == 17 and m.word("G_TURNS") == 0
    # One-button cancel on self, then SPACE cancel, cost neither charge nor turn.
    m.set("G_KEY", 5)
    m.call("INSPECT_MOVE")
    assert m.get("G_MODE") == 1 and m.get("G_WAND_SLOT") == 0
    m.call("USE_ITEM")
    m.set("G_KEY", 6)
    m.call("INSPECT_MOVE")
    assert m.get("G_BAG") == 17 and m.word("G_TURNS") == 0
    target = enemy(m, 14, 12, 2, 24)
    for charge in range(3):
        m.call("USE_ITEM")
        m.set("G_KEY", 4)
        m.call("INSPECT_MOVE")
        m.set("G_KEY", 5)
        m.call("INSPECT_MOVE")  # empty visible square: no charge spent
        if charge == 0:
            assert m.get("G_BAG") == 17 and m.word("G_TURNS") == 0
        # Enemy can advance after earlier shots; aim at actual current position.
        m.set("G_INSPECT_X", m.get(target))
        m.set("G_INSPECT_Y", m.get(target + 1))
        m.call("INSPECT_MOVE")
        assert m.get("G_BAG") == 18 + charge
        assert m.get(target + 3) == 16 - charge * 8
        assert m.word("G_TURNS") == charge + 1
    assert m.get("G_KILLS") == 1
    m.set("G_MODE", 4)
    m.call("USE_ITEM")
    assert m.get("G_MESSAGE") == 34 and m.word("G_TURNS") == 3
    assert m.get("G_BAG") == 20
    # Invisible targets cannot consume a charge or receive damage.
    reset_room(m)
    hidden = enemy(m, 35, 25, hp=10)
    m.set("G_BAG", 17)
    m.call("USE_ITEM")
    m.set("G_INSPECT_X", 35)
    m.set("G_INSPECT_Y", 25)
    m.set("G_KEY", 5)
    m.call("INSPECT_MOVE")
    assert m.get("G_BAG") == 17 and m.get(hidden + 3) == 10
    assert m.get("G_MODE") == 5 and m.word("G_TURNS") == 0
    # Wand charge is encoded in each item, surviving drop/pickup independently.
    reset_room(m)
    m.set("G_BAG", 19)
    m.set("G_MENU", 1)
    m.call("DISCARD_ITEM")
    assert m.items()[0] == [12, 12, 19] and m.get("G_BAG") == 0
    m.call("PICKUP")
    assert m.get("G_BAG") == 19
    # One equipped ring; another ring replaces it without consuming either.
    reset_room(m)
    m.set("G_BAG", 21)
    m.set(SYMS["G_BAG"] + 1, 21)
    m.call("USE_ITEM")
    assert m.read("G_BAG", 2) == bytes([22, 21]) and m.get("G_FOOD") == 240
    m.set("G_SLOT", 1)
    m.call("USE_ITEM")
    assert m.read("G_BAG", 2) == bytes([21, 22]) and m.get("G_FOOD") == 239
    m.call("USE_ITEM")
    assert m.read("G_BAG", 2) == bytes([21, 21]) and m.get("G_FOOD") == 238
    m.set("G_SLOT", 0)
    m.call("USE_ITEM")
    before = m.get("G_FOOD")
    for _ in range(10):
        m.call("COMMIT_TURN")
    assert m.get("G_FOOD") == before - 5
    # Dropping a worn ring removes the effect and normalizes its ground kind.
    m.set("G_MENU", 1)
    m.call("DISCARD_ITEM")
    assert m.items()[0] == [12, 12, 21] and 22 not in m.read("G_BAG", 6)
    # Nymph must skip the equipped ring, but can steal a carried ring.
    reset_room(m)
    thief = enemy(m, 13, 12, 15, 7)
    m.set("G_BAG", 22)
    m.call("ENEMY_STRIKE")
    assert m.get("G_BAG") == 22 and m.get(thief + 6) == 0
    m.set(SYMS["G_BAG"] + 1, 21)
    m.call("ENEMY_STRIKE")
    assert m.get("G_BAG") == 22 and m.get(SYMS["G_BAG"] + 1) == 0
    assert m.get(thief + 6) == 1
    # Both new ground sprites fit in the reserved PCG bank.
    reset_room(m)
    for i, item in enumerate((17, 21)):
        address = SYMS["FLOORS"] + SYMS["ITEM_START"] + i * 3
        for j, value in enumerate((11 + i * 2, 12, item)):
            m.set(address + j, value)
    m.call("RENDER_SCREEN")
    screen = m.read(0xC140, 640)
    assert 157 in screen and 158 in screen
    m.close()
    return "passed"


if __name__ == "__main__":
    print(check())
