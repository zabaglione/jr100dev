"""Verify staged combat and input isolation against the independent rules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tests"))
from machine import KEYS, Machine, lib
from model import State
from replay import FIELDS, compare, settle


def check(state, die, choice, expected):
    machine = Machine("dice_relic")
    machine.action(5)
    settle(machine)
    for field, name in FIELDS.items():
        lib.poke(machine.p, machine.sym[name], getattr(state, field))
    for i, value in enumerate(state.dice):
        lib.poke(machine.p, machine.sym["DICE"] + i, value)
    lib.poke(machine.p, machine.sym["SELECTED"], die)
    lib.poke(machine.p, machine.sym["CHOICE"], choice)
    initial_dice = bytes(state.dice)
    turn = state.turn
    hp, enemy_hp, shield = state.hp, state.enemy_hp, state.shield
    state.use(die, choice)
    scenes = []
    images = {}
    bank = machine.read(0xC000, 256)
    lib.key(machine.p, *KEYS[5], 1)
    machine.until("DISPATCH")
    while True:
        event = lib.until_either(
            machine.p,
            machine.sym["EFFECT_VISIBLE"],
            machine.sym["FRAME_READY"],
            12_000_000,
        )
        assert event
        if event == 2:
            break
        kind, phase = machine.get("EVENT_KIND"), machine.get("EVENT_FRAME")
        assert machine.get("MODE") == 1 and machine.get("TURN") == turn
        assert machine.read("DICE", 3) == initial_dice
        assert machine.read(0xC000, 256) == bank
        assert machine.read("ROLES", 3)[die] == choice + 1
        assert machine.get("USED") & (1 << die)
        scenes.append((kind, phase, lib.clocks(machine.p)))
        images.setdefault(kind, set()).add(machine.read(0xC100, 768))
        if kind == 1:
            assert machine.get("ENEMY_HP") == enemy_hp
        elif kind == 2:
            assert machine.get("EVENT_BEFORE") == enemy_hp
            assert machine.get("EVENT_AFTER") == max(0, enemy_hp - initial_dice[die])
        elif kind == 3:
            assert machine.get("EVENT_BEFORE") == shield
            assert machine.get("EVENT_AFTER") == shield + initial_dice[die]
        elif kind == 4:
            assert machine.get("EVENT_BEFORE") == hp
            assert machine.get("EVENT_AFTER") == min(42, hp + initial_dice[die])
            assert machine.get("EVENT_VALUE") == min(42 - hp, initial_dice[die])
        elif kind == 7:
            assert machine.get("EVENT_BEFORE") == hp
            assert machine.get("EVENT_AFTER") == state.hp
        lib.key(machine.p, *KEYS[5], 0)
        if phase == 0:
            lib.key(machine.p, *KEYS[4], 1)
        if phase == 1:
            lib.key(machine.p, *KEYS[4], 0)
        # Leave this breakpoint before waiting for the next scene.
        lib.ticks(machine.p, 1)
    lib.key(machine.p, *KEYS[5], 0)
    machine.until("INPUT_DONE")
    compare(machine, state)
    assert [(kind, phase) for kind, phase, _ in scenes] == [
        (kind, phase) for kind in expected for phase in range(3)
    ]
    assert all(len(frames) >= 2 for frames in images.values())
    assert (
        machine.get("EVENT_KIND")
        == machine.get("PACE_ACTIVE")
        == machine.get("KEY_PENDING")
        == 0
    )
    assert machine.read(0x300, len(machine.code)) == machine.code
    assert lib.min_sp(machine.p) >= 0x3E00 and lib.audio_peak(machine.p) > 0
    for a, b in zip(scenes, scenes[1:]):
        assert b[2] - a[2] >= 14900 * 8


check(State(dice=[6, 4, 2], turn=1), 0, 0, [1, 2])
check(State(dice=[6, 4, 2], turn=1), 0, 1, [3])
check(State(dice=[6, 4, 2], hp=35, turn=1), 0, 2, [4])
check(State(dice=[6, 4, 2], hp=41, turn=1), 0, 2, [4])
check(State(dice=[6, 4, 2], used=3, turn=4), 2, 1, [3, 5, 6, 7])
check(State(dice=[6, 4, 2], used=3, shield=20, turn=1), 2, 0, [1, 2, 5, 6])
check(State(dice=[6, 4, 2], used=3, turn=4, hp=2), 2, 0, [1, 2, 5, 7, 10])
check(State(dice=[6, 4, 2], used=3, turn=4, hp=1, enemy_hp=1), 2, 0, [1, 2, 8, 9])
print(
    "PASS: dice_relic, assigned dice retained, ten three-frame effects, visible before/after stats, shield absorption, lethal ordering and input isolation"
)
