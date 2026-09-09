"""Native execution checks for added monsters, magic, and identification."""

from check_game import enemy, reset_room
from machine import SYMS, Machine


def check():
    m = Machine()
    appearances = [2, 3, 4, 5, 6, 14, 15, 16]
    # Every effect through every appearance slot: names, bit 7, consumption.
    for slot, item in enumerate(appearances):
        for effect in range(8):
            reset_room(m)
            m.set("G_HP", 10)
            if effect == 5:
                m.set("G_POISON", 6)
                m.set("G_POISON_TICK", 1)
            m.set("G_BAG", item)
            m.set(SYMS["G_IDENTITIES"] + slot, effect)
            m.call("ITEM_NAME", item)
            assert m.read("G_KNOWN", 1) == b"\0"
            m.call("USE_ITEM")
            assert m.get("G_BAG") == 0
            assert m.get("G_KNOWN") == 1 << slot
            _, _, ptr, _ = m.call("ITEM_NAME", item)
            table = SYMS["EFFECT_NAMES"] + effect * 2
            assert ptr == m.word(table)
            assert m.get("G_WEAPON") == m.get("G_ARMOR") == 0
            if effect == 5:
                assert m.get("G_HP") == 24
                assert m.get("G_POISON") == m.get("G_POISON_TICK") == 0
    # Real initializers keep potion/scroll identities separate and permuted.
    layouts = set()
    for seed in range(1, 65):
        m.set("G_DIFFICULTY", 0)
        m.setw("G_SEED", seed)
        m.call("NEW_GAME")
        ids = m.read("G_IDENTITIES", 8)
        assert sorted(ids) == list(range(8))
        assert sorted(ids[i] for i in (0, 1, 2, 5)) == [0, 1, 2, 5]
        assert sorted(ids[i] for i in (3, 4, 6, 7)) == [3, 4, 6, 7]
        assert m.get("G_KNOWN") == 0
        layouts.add(ids)
    assert len(layouts) > 8
    # Hold applies to visible monsters only, including the consumption turn.
    reset_room(m)
    near = enemy(m, 13, 12)
    far = enemy(m, 35, 25, index=1)
    m.set("G_BAG", 15)
    m.set(SYMS["G_IDENTITIES"] + 6, 6)
    m.call("USE_ITEM")
    assert m.get(near + 7) == 5 and m.get(far + 7) == 0
    assert m.get("G_HP") == 24
    for _ in range(5):
        m.call("COMMIT_TURN")
        assert m.get("G_HP") == 24
    m.call("COMMIT_TURN")
    assert m.get("G_HP") < 24
    # Aggravation cancels holds and sets even unseen targets to current position.
    reset_room(m)
    far = enemy(m, 35, 25)
    m.set(far + 7, 4)
    m.set("ITEM_EFFECT", 7)
    m.call("EXTENDED_MAGIC", 7)
    assert m.read(far + 4, 2) == bytes([12, 12]) and m.get(far + 7) == 0
    # Vampire drain is conditional, cannot underflow maximum health.
    drains = 0
    for seed in range(1, 33):
        reset_room(m)
        enemy(m, 13, 12, 13, 12)
        m.setw("G_RNG", seed)
        m.call("ENEMY_STRIKE")
        drains += m.get("G_MAX_HP") == 23
        assert m.get("G_HP") <= m.get("G_MAX_HP")
    assert 0 < drains < 32
    m.set("G_MAX_HP", 8)
    for seed in range(1, 33):
        m.set("G_HP", 8)
        m.setw("G_RNG", seed)
        m.call("ENEMY_STRIKE")
        assert m.get("G_MAX_HP") == 8
    # Dragon fire uses line of sight, and its dedicated sprite stays in PCG.
    reset_room(m)
    enemy(m, 12, 8, 14, 16)
    m.call("ENEMIES_TURN")
    assert m.get("G_HP") < 24 and m.get("G_MESSAGE") == 31
    m.call("RENDER_SCREEN")
    assert 128 + 27 in m.read(0xC140, 640)
    from check_game import tile

    tile(m, 12, 10, 0)
    m.call("UPDATE_VISIBILITY")
    hp = m.get("G_HP")
    m.call("ENEMIES_TURN")
    assert m.get("G_HP") == hp
    # Nymph steals one carried item once, leaves equipment intact, then flees.
    reset_room(m)
    thief = enemy(m, 13, 12, 15, 7)
    m.set(SYMS["G_BAG"] + 1, 5)
    m.set(SYMS["G_BAG"] + 3, 14)
    m.set("G_WEAPON", 9)
    m.set("G_ARMOR", 12)
    m.call("ENEMY_STRIKE")
    assert m.get(SYMS["G_BAG"] + 1) == 0
    assert m.get(SYMS["G_BAG"] + 3) == 14
    assert m.get(thief + 6) == 1 and m.get("G_MESSAGE") == 32
    assert m.get("G_WEAPON") == 9 and m.get("G_ARMOR") == 12
    m.call("ENEMY_STRIKE")
    assert m.get(SYMS["G_BAG"] + 3) == 14
    m.call("ENEMIES_TURN")
    assert abs(m.get(thief) - 12) + abs(m.get(thief + 1) - 12) > 1
    reset_room(m)
    thief = enemy(m, 13, 12, 15, 7)
    m.call("ENEMY_STRIKE")
    assert m.get(thief + 6) == 0
    m.set("G_BAG", 1)
    m.call("ENEMY_STRIKE")
    assert m.get(thief + 6) == 1 and m.get("G_BAG") == 0
    m.call("RENDER_SCREEN")
    assert 128 + 28 in m.read(0xC140, 640)
    m.close()
    return {"status": "passed", "identity_layouts": len(layouts)}


if __name__ == "__main__":
    print(check())
