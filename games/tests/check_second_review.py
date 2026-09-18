"""Choice, resource and terminal-state regressions for individually revised games.

These model fixtures exercise outcomes that a successful input replay does not
cover. Native byte-state comparison and full campaigns run separately.
"""

import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "native"), str(ROOT)]
from checks import Model, render_bounds
from quality.strategies import lights


def auction_house():
    # The same cautious policy must work on every timer seed in all three markets.
    # It uses appraisal bounds, never the hidden final value or rival reserve.
    for seed in range(256):
        r = Model("auction_house")
        r.entropy = lambda seed=seed: seed
        for level in range(3):
            r.init(level)
            for _ in range(60):
                s = r.s
                if s.mode != 1:
                    break
                if not s.inspected and s.low - 2 <= s.bid + 2 <= s.high - 2:
                    s.choice = 2
                else:
                    s.choice = (
                        3
                        if s.bid + 2 > s.low - 2
                        else (1 if s.bid + 6 <= s.low - 2 else 0)
                    )
                r.action(5)
            assert r.s.mode == 2, (seed, level, vars(r.s))
    r = Model("auction_house")
    r.s.choice = 2
    r.action(5)
    cash = r.s.cash
    r.action(5)
    assert r.s.cash == cash == 39 and r.s.low == r.s.high == r.s.value


def twenty_one():
    decks = set()
    for seed in range(256):
        r = Model("twenty_one")
        r.entropy = lambda seed=seed: seed
        r.init()
        assert set(r.d[:52]) == set(range(52))
        assert Counter(card % 13 for card in r.d[:52]) == Counter(
            {i: 4 for i in range(13)}
        )
        decks.add(bytes(r.d[:52]))
    assert len(decks) > 200
    r = Model("twenty_one")
    for cards, expected in (
        ([0, 13, 8], 21),
        ([0, 13, 8, 12], 21),
        ([0, 13, 26, 39], 14),
    ):
        r.b[: len(cards)] = bytes(cards)
        r.s.np = len(cards)
        assert r.env["total"](0) == expected
    # Player blackjack, dealer blackjack, equal naturals, and ordinary bust.
    for player, dealer, np, nd, expected in (
        (21, 20, 2, 2, 13),
        (21, 21, 3, 2, 8),
        (21, 21, 2, 2, 10),
        (22, 25, 3, 3, 8),
    ):
        r.init()
        r.s.player, r.s.dealer, r.s.np, r.s.nd = player, dealer, np, nd
        r.env["finish"]()
        assert r.s.coins == expected
    r.init()
    r.s.coins = 3
    r.s.choice = 2
    before = (r.s.drawn, r.s.coins, r.s.round)
    r.action(5)
    assert (r.s.drawn, r.s.coins, r.s.round) == before


def star_lance():
    r = Model("star_lance")
    r.b[:] = bytes(128)
    r.b[3], r.s.left = 2, 1
    r.action(5)
    assert r.b[3] == 1 and r.s.left == 1 and r.s.heat == 2
    r.s.cool, r.s.heat = 0, 6
    r.action(1)
    assert r.b[3] == 1 and r.s.heat == 6 and r.s.notice
    r.s.heat = 4
    r.action(1)
    assert r.b[3] == 0 and r.s.mode == 2 and r.s.heat == 8
    r.init()
    r.s.ship = 0
    r.action(3)
    assert r.s.ship == 0


def orbit_dodge():
    r = Model("orbit_dodge")
    r.s.pos, r.s.orbit = r.s.target, r.s.ring
    r.s.age = r.s.window - 1
    r.tick()
    assert r.s.hp == 2
    r.init()
    r.s.pos, r.s.orbit = r.s.target, r.s.ring ^ 1
    r.s.age = r.s.window - 1
    r.tick()
    assert r.s.hp == 3
    r.init()
    for _ in range(3):
        r.s.pos, r.s.orbit = r.s.gem, r.s.gem_ring
        r.s.age = r.s.window - 1
        r.tick()
    assert r.s.score == 6 and r.s.hp == 3


def echo_parry():
    r = Model("echo_parry")
    r.action(3)
    for _ in range(6):
        r.tick()
    assert r.s.hp == 4 and r.s.enemy == 6
    r.init()
    r.s.phase, r.s.age, r.s.stance = 1, 1, r.s.attack
    r.action(5)
    assert r.s.enemy == 4 and r.s.hp == 4
    r.init()
    r.action(5)
    for _ in range(6):
        r.tick()
    assert r.s.hp == 3  # One mistimed guard cannot be charged twice.


def night_swarm():
    r = Model("night_swarm")
    entries = set()
    for count in range(28):
        r.s.spawn = count
        r.env["spawn_preview"]()
        entries.add(r.s.entry)
    assert len(entries) == 28
    assert all(p % 8 in (0, 7) or p // 8 in (0, 7) for p in entries)
    r.b[0], r.c[0] = 26, 2
    r.env["hurt"](0)
    assert r.b[0] == 26 and r.c[0] == 1 and r.s.kills == 0
    r.s.kills = 3
    r.env["hurt"](0)
    assert r.b[0] == 255 and r.s.cell == 26 and r.s.kills == 4
    r.s.hp, r.s.cooldown = 2, 6
    r.action(3)
    assert r.s.hp == 3 and r.s.cooldown == 0 and r.s.salvage == 1


def ribbon_snake():
    r = Model("ribbon_snake")
    r.action(5)
    assert r.s.brakes == 2
    r.action(5)
    assert r.s.brakes == 2
    r.tick()
    pos = r.b[0]
    r.tick()
    assert r.b[0] == pos
    r.init()
    r.d[16] = 1
    r.tick()
    assert r.s.mode == 3


def lunar_touchdown():
    scores = []
    for precise in (False, True):
        r = Model("lunar_touchdown")
        r.s.x = r.s.narrow if precise else r.s.target
        r.s.height, r.s.speed = 29, 1
        r.tick()
        assert r.s.mode == 2
        scores.append(r.s.score)
    assert scores[1] == scores[0] + 10 and scores[0] == 26
    r = Model("lunar_touchdown")
    r.s.x, r.s.height, r.s.speed = r.s.target, 29, 3
    r.tick()
    assert r.s.mode == 3


def orchard_days():
    for crop, growth, reward in ((0, 3, 3), (1, 5, 7)):
        r = Model("orchard_days")
        r.s.crop = crop
        r.action(5)
        for _ in range(growth - 1):
            r.action(5)
        assert r.b[0] == growth and r.s.seeds == 7
        r.action(5)
        assert r.s.fruit == reward and r.s.seeds == 8 and r.b[0] == 0
    r.init()
    r.s.water, r.s.cursor = 0, 19
    r.action(5)
    assert r.s.water == 3 and r.s.day == 1
    r.s.cursor, r.s.seeds = 0, 0
    r.action(5)
    assert r.s.day == 1 and r.b[0] == 0


def tidal_nets():
    for wide, cost, expected in ((0, 1, 2), (1, 2, 6)):
        r = Model("tidal_nets")
        r.s.fish, r.s.deep, r.s.tide, r.s.force = 1, 1, 1, 1
        r.s.cursor, r.s.wide = 2, wide
        r.action(5)
        assert r.s.catch == expected and r.s.rope == 12 - cost
    r.s.rope, r.s.wide = 1, 1
    before = r.s.casts
    r.action(5)
    assert r.s.casts == before and r.s.rope == 1


def cargo_balance():
    for column, torque, fare in ((0, 9, 6), (1, 3, 3)):
        r = Model("cargo_balance")
        r.s.cursor, r.s.weight = column, 3
        r.action(5)
        assert r.s.left == torque and r.s.fare == fare and r.s.mode == 1
    r = Model("cargo_balance")
    r.s.weight = 4
    r.action(5)
    assert r.s.mode == 3
    r.init()
    r.c[0] = 4
    r.action(5)
    assert r.s.loads == 0 and r.s.fare == 0


def potion_path():
    r = Model("potion_path")
    r.b[25] = 1  # Ash would land at (1, 3).
    r.action(5)
    assert r.s.doses == 0 and r.c[0] == 4 and (r.s.x, r.s.y) == (3, 3)
    r.b[25] = 0
    r.action(5)
    assert r.s.doses == 1 and r.c[0] == 3 and (r.s.x, r.s.y) == (1, 3)
    r.c[0] = 0
    r.action(5)
    assert r.s.doses == 1


def compass_rose():
    r = Model("compass_rose")
    reading = (r.s.north, r.s.east, r.s.band, r.s.survey_pos)
    r.action(4)
    assert r.s.pos != reading[3]
    assert reading == (r.s.north, r.s.east, r.s.band, r.s.survey_pos)
    fuel = r.s.fuel
    r.action(7)
    assert r.s.fuel == fuel - 2 and r.s.surveys == 3 and r.s.survey_pos == r.s.pos


def stone_balance():
    @lru_cache(None)
    def winning(piles, misere):
        if not sum(piles):
            return misere
        return any(
            not winning(piles[:i] + (count - take,) + piles[i + 1 :], misere)
            for i, count in enumerate(piles)
            for take in range(1, min(3, count) + 1)
        )

    r = Model("stone_balance")
    for level in range(10):
        r.init(level)
        assert winning(tuple(r.b[:3]), bool(r.s.misere))
    for misere in (0, 1):
        r.init()
        r.s.misere = misere
        r.b[:3] = bytes((1, 0, 0))
        r.action(5)
        assert r.s.mode == (3 if misere else 2)


def lumen_cross():
    r = Model("lumen_cross")
    for level in range(18):
        r.init(level)
        solution = lights(r.b)
        assert len(solution) == r.env["pars"][level]
        for pos in solution:
            r.s.cursor = pos
            r.action(5)
        assert r.s.mode == 2 and not any(r.b[:25])


def word_foundry():
    from replay import Player

    p = Player("word_foundry")
    for target in (1, 2):
        p.go(target, 4)
        p.press(5)
    # Inspect the native logical framebuffer, before font mapping. Subtracting
    # eight from a short history used to wrap and display CAT repeatedly.
    history = p.m.read("FRAMEBUFFER", 768)[19 * 32 : 20 * 32]
    for column, word in enumerate(("CAT", "COT", "COG")):
        assert history[column * 4 : column * 4 + 3] == bytes(ord(c) - 32 for c in word)


def check(name):
    r = Model(name)
    assert r.metadata["secondReview"]
    if name in globals():
        globals()[name]()
    # Draw every effect pose reached by a mixed sequence, including failures.
    import random

    rng = random.Random(name)
    frames = []

    def frame(*args):
        render_bounds(r)
        frames.append(1)

    for hook in ("animate", "hold", "glide"):
        r.env[hook] = frame
    for event in range(100):
        if r.s.mode != 1:
            r.init(event % r.metadata["levels"])
        if r.metadata.get("rate", 255) < 255 and event % 2:
            r.tick()
        else:
            r.action(rng.choice((1, 2, 3, 4, 5, 7)))
        render_bounds(r)
    print(
        f"PASS: {name}, choices/resources/endings and {len(frames)} intermediate frames"
    )


if __name__ == "__main__":
    names = sys.argv[1:] or [
        p.parent.name
        for p in ROOT.glob("*/game.json")
        if json.loads(p.read_text()).get("secondReview")
    ]
    for name in names:
        check(name)
