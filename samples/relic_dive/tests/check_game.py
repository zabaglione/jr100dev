"""Runtime regression checks against the actual assembled game, standard 16K RAM."""

import argparse
import hashlib
import json
import multiprocessing
import time
from collections import deque
from concurrent.futures import ProcessPoolExecutor

from check_opcodes import check as check_opcodes
from machine import KEYS, PADS, ROOT, SYMS, Machine, lib
from reference_inputs import check as check_references

WIDTH = SYMS["MAP_WIDTH"]
HEIGHT = SYMS["MAP_HEIGHT"]


def require(value, message):
    if not value:
        raise AssertionError(message)


def reset_room(m):
    for a in range(SYMS["STATE_BEGIN"], SYMS["STATE_END"]):
        m.set(a, 0)
    for a in range(SYMS["SCRATCH_BEGIN"], SYMS["SCRATCH_END"]):
        m.set(a, 0)
    m.call("SELECT_FLOOR")
    for y in range(1, 31):
        for x in range(1, WIDTH - 1):
            address = SYMS["FLOORS"] + y * (WIDTH // 2) + x // 2
            m.set(address, m.get(address) | (1 << (4 * (x & 1))))
    m.set("G_X", 12)
    m.set("G_Y", 12)
    m.set("G_HP", 24)
    m.set("G_MAX_HP", 24)
    m.set("G_ATTACK", 3)
    m.set("G_FOOD", 240)
    m.set("G_LEVEL", 1)
    m.set("G_MODE", 1)
    m.set("G_DEPTH", 5)
    m.call("UPDATE_VISIBILITY")


def tile(m, x, y, v):
    m.call("CELL", x, y)
    m.call("WRITE_CELL", v)


def enemy(m, x, y, kind=2, hp=5, index=0):
    a = SYMS["FLOORS"] + SYMS["ENEMY_START"] + index * 8
    for j, v in enumerate((x, y, kind, hp, 255, 255, 0, 0)):
        m.set(a + j, v)
    return a


def mechanics():
    m = Machine()
    for a, b in [(0, 255), (255, 255), (WIDTH, 31), (64, 8), (213, 98)]:
        hi, lo, _, _ = m.call("MULTIPLY", a, b)
        require(hi * 256 + lo == a * b, "multiply")
    m.setw("G_RNG", 1)
    state = 1
    for _ in range(100):
        a, b, _, _ = m.call("RANDOM")
        state = (25173 * state + 13849) & 65535
        require(m.word("G_RNG") == state and a == state >> 8, "LCG differs")
    reset_room(m)
    for x, y in [
        (0, 0),
        (WIDTH - 1, HEIGHT - 1),
        (8, 4),
        (9, 4),
        (WIDTH - 2, HEIGHT - 2),
    ]:
        for v in range(10):
            tile(m, x, y, v)
            a, _, _, _ = m.call("CELL", x, y)
            require(a & 15 == v, "packed terrain")
            m.call("MARK_SEEN")
            a, _, _, _ = m.call("CELL", x, y)
            require(a == v | 128, "explored bit")
            m.call("MARK_VISIBLE", x, y)
            _, _, visible_ptr, _ = m.call("VISIBLE_CELL", x, y)
            require(m.get(visible_ptr) != 0, "visibility bit at map edge")
    reset_room(m)
    for action, (dx, dy) in {
        1: (0, -1),
        2: (0, 1),
        3: (-1, 0),
        4: (1, 0),
        7: (-1, -1),
        8: (1, -1),
        9: (-1, 1),
        10: (1, 1),
    }.items():
        m.set("G_X", 12)
        m.set("G_Y", 12)
        m.set("G_KEY", action)
        before = m.word("G_TURNS")
        m.call("WORLD_DIRECTION")
        require((m.get("G_X"), m.get("G_Y")) == (12 + dx, 12 + dy), "8-way movement")
        require(m.word("G_TURNS") == before + 1, "movement turn")
    reset_room(m)
    tile(m, 13, 12, 0)
    m.set("G_KEY", 8)
    m.call("WORLD_DIRECTION")
    require(m.word("G_TURNS") == 0 and m.get("G_X") == 12, "diagonal corner")
    reset_room(m)
    e = enemy(m, 13, 12)
    m.set("G_KEY", 4)
    m.call("WORLD_DIRECTION")
    require(m.get(e + 3) == 2 and m.get("G_X") == 12, "melee damage")
    m.call("WORLD_DIRECTION")
    require(m.get(e + 3) == 0, "melee kill")
    # Each kind: regeneration, poison, rust, theft, food stealing and ranged damage.
    for kind in range(1, 13):
        reset_room(m)
        e = enemy(m, 13, 12, kind, 8)
        m.set("E_INDEX", 0)
        m.set("G_DEFENSE", 2)
        m.set("G_ARMOR", 11)
        m.setw("G_GOLD", 20)
        m.call("ENEMY_STRIKE")
        require(m.get("G_HP") < 24, f"enemy {kind} strike")
        if kind == 4:
            require(m.get("G_FOOD") == 237, "wraith drain")
        if kind == 9:
            require(m.word("G_GOLD") == 10 and m.get(e + 6) == 1, "thief")
        if kind == 10:
            require(m.get("G_POISON") == 6, "snake")
        if kind == 11:
            require(m.get("G_DEFENSE") == 1, "rust")
    reset_room(m)
    e = enemy(m, 16, 12, 12, 10)
    m.call("UPDATE_VISIBILITY")
    m.call("ENEMIES_TURN")
    require(m.get("G_HP") == 21, "ranged attack")
    reset_room(m)
    e = enemy(m, 15, 12, 8, 8)
    m.setw("G_TURNS", 4)
    m.call("ENEMIES_TURN")
    require(m.get(e + 3) == 9, "troll regeneration")
    reset_room(m)
    m.set("G_HP", 10)
    for _ in range(12):
        m.call("COMMIT_TURN")
    require(m.get("G_HP") == 11 and m.get("G_FOOD") == 228, "natural healing")
    m.set("G_FOOD", 0)
    m.call("COMMIT_TURN")
    m.call("COMMIT_TURN")
    require(m.get("G_HP") == 10, "starvation")
    reset_room(m)
    tile(m, 13, 12, 5)
    tile(m, 12, 13, 6)
    tile(m, 11, 12, 7)
    m.call("SEARCH_ACTION")
    require(
        m.map()[12 * WIDTH + 13] == 1
        and m.map()[13 * WIDTH + 12] == 8
        and m.map()[12 * WIDTH + 11] == 9,
        "search reveals secrets/traps",
    )
    require(m.word("G_TURNS") == 1, "search turn")
    m.set("G_KEY", 2)
    m.call("WORLD_DIRECTION")
    require(m.get("G_HP") == 21 and m.map()[13 * WIDTH + 12] == 1, "damage trap")
    reset_room(m)
    tile(m, 13, 12, 7)
    m.set("G_KEY", 4)
    m.call("WORLD_DIRECTION")
    require(m.get("G_POISON") == 5 and m.map()[12 * WIDTH + 13] == 1, "poison trap")
    # All item effects, identification and equipment.
    for item in range(1, 13):
        reset_room(m)
        for i in range(5):
            m.set(SYMS["G_IDENTITIES"] + i, i)
        m.set("G_HP", 10)
        m.set("G_FOOD", 100)
        m.set("G_BAG", item)
        m.call("USE_ITEM")
        require(m.get("G_BAG") == 0 and m.word("G_TURNS") == 1, f"item {item} consumed")
        if 2 <= item <= 6:
            require(m.get("G_KNOWN") & (1 << (item - 2)), f"item {item} identified")
        if item == 1:
            require(m.get("G_FOOD") == 179, "food")
        if item == 2:
            require(m.get("G_HP") == 22, "healing potion")
        if item == 3:
            require(m.get("G_HP") == 7, "poison potion")
        if item == 4:
            require(m.get("G_BUFF") == 12, "strength duration")
        if item == 5:
            require(
                m.read("SEEN", SYMS["MASK_BYTES"]) == bytes([255]) * SYMS["MASK_BYTES"],
                "mapping",
            )
        if 7 <= item <= 9:
            require(m.get("G_ATTACK") == item - 3, "weapon")
        if 10 <= item <= 12:
            require(m.get("G_DEFENSE") == item - 9, "armor")
    reset_room(m)
    m.set("G_BAG", 9)
    m.set("G_WEAPON", 7)
    m.call("USE_ITEM")
    require(
        m.items()[0] == [12, 12, 7] and m.get("G_WEAPON") == 9, "equipment exchange"
    )
    m.set("G_BAG", 8)
    before = m.word("G_TURNS")
    m.call("USE_ITEM")
    require(m.word("G_TURNS") == before and m.get("G_BAG") == 8, "blocked exchange")
    reset_room(m)
    for i in range(6):
        m.set(SYMS["G_BAG"] + i, 1)
    a = SYMS["FLOORS"] + SYMS["ITEM_START"]
    for j, v in enumerate((12, 12, 2)):
        m.set(a + j, v)
    m.call("PICKUP")
    require(m.get(a + 2) == 2, "full bag leaves item")
    m.set(a + 2, 13)
    m.call("PICKUP")
    require(m.word("G_GOLD") == 10 and m.get(a + 2) == 0, "gold")
    reset_room(m)
    m.set("G_HP", 1)
    m.set("G_FOOD", 0)
    m.set("G_STARVE", 1)
    m.call("COMMIT_TURN")
    require(m.get("G_MODE") == 8, "death")
    reset_room(m)
    tile(m, 13, 12, 4)
    m.set("G_KEY", 4)
    m.call("WORLD_DIRECTION")
    require(m.get("G_MODE") == 9 and m.get("G_TREASURE") == 1, "relic victory")
    # Safe held walking is limited to known unbranched corridors.
    reset_room(m)
    for address in range(SYMS["FLOORS"], SYMS["FLOORS"] + SYMS["TERRAIN_BYTES"]):
        m.set(address, 0)
    for x in range(5, 21):
        tile(m, x, 12, 1)
    m.set("G_X", 10)
    m.set("G_Y", 12)
    m.set("LAST_DIRECTION", 4)
    for address in range(SYMS["SEEN"], SYMS["SEEN"] + SYMS["MASK_BYTES"]):
        m.set(address, 255)
    m.call("UPDATE_VISIBILITY")
    m.call("SAFE_WALK")
    require(m.get("SAFE_FLAG") == 1, "known corridor should repeat")
    tile(m, 10, 11, 1)
    m.call("SAFE_WALK")
    require(m.get("SAFE_FLAG") == 0, "branch stops repeat")
    tile(m, 10, 11, 0)
    tile(m, 11, 12, 8)
    m.call("SAFE_WALK")
    require(m.get("SAFE_FLAG") == 0, "trap stops repeat")
    tile(m, 11, 12, 1)
    m.set("G_FOOD", 40)
    m.call("SAFE_WALK")
    require(m.get("SAFE_FLAG") == 0, "hunger stops repeat")
    # Bounds and line of sight at both camera extremes, including secret walls.
    reset_room(m)
    tile(m, 13, 12, 5)
    m.set("LOS_TX", 14)
    m.set("LOS_TY", 12)
    a, _, _, _ = m.call("LINE_VISIBLE")
    require(a == 0, "secret wall blocks sight")
    for x, y, vx, vy in [
        (1, 1, 0, 0),
        (WIDTH - 2, HEIGHT - 2, WIDTH - 32, HEIGHT - 20),
    ]:
        m.set("G_X", x)
        m.set("G_Y", y)
        m.call("UPDATE_VISIBILITY")
        m.call("RENDER_SCREEN")
        require((m.get("VIEW_X"), m.get("VIEW_Y")) == (vx, vy), "camera clamp")
    require(m.read(0x300, len(m.code)) == m.code, "runtime modified code")
    m.close()
    return "passed"


def inputs():
    m = Machine()
    for action, (row, bit) in KEYS.items():
        lib.key(m.p, row, bit, 1)
        m.call("POLL_KEY")
        require(m.get("G_PENDING") == action, f"keyboard {action}")
        m.set("G_PENDING", 0)
        m.call("POLL_KEY")
        require(m.get("G_PENDING") == 0, "held key repeated")
        lib.key(m.p, row, bit, 0)
        m.call("POLL_KEY")
    # Former U/I/O/J/K/L bindings are removed, not retained as aliases.
    for row, bit in [(5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)]:
        lib.key(m.p, row, bit, 1)
        m.call("POLL_KEY")
        require(m.get("G_PENDING") == 0, "obsolete key binding")
        lib.key(m.p, row, bit, 0)
        m.call("POLL_KEY")
    for action, mask in PADS.items():
        lib.pad(m.p, mask | 0xE0)
        m.call("POLL_KEY")
        require(m.get("G_PENDING") == action, f"pad {mask}")
        m.set("G_PENDING", 0)
        m.call("POLL_KEY")
        require(m.get("G_PENDING") == 0, "held pad repeated")
        lib.pad(m.p, 0)
        m.call("POLL_KEY")
    for mask in (3, 12, 15):
        lib.pad(m.p, mask)
        m.call("POLL_KEY")
        require(m.get("G_PENDING") == 0, "opposite axes")
        lib.pad(m.p, 0)
        m.call("POLL_KEY")
    m.resume()
    m.start(0)
    turns = m.word("G_TURNS")
    m.action(5, True)
    for _ in range(6):
        m.action(2, True)
    m.action(5, True)
    require(m.get("G_MODE") == 1, "pad main BACK")
    m.action(5, True)
    m.action(5, True)
    for _ in range(6):
        m.action(2, True)
    m.action(5, True)
    require(m.get("G_MODE") == 2, "pad bag BACK")
    for _ in range(3):
        m.action(2, True)
    m.action(5, True)
    require(m.get("G_MODE") == 7, "suspend")
    m.action(5, True)
    require(m.get("G_MODE") == 1, "resume")
    require(m.word("G_TURNS") == turns, "menus advanced time")
    # BREAK restores the original caller stack, low RAM, and PCG.
    expected_zp = m.read("SAVE_ZP", 128)
    expected_pcg = m.read("SAVE_PCG", 256)
    m.set(0x245, 2)
    m.set(0x246, 0x80)
    lib.key(m.p, 0, 0, 1)
    lib.key(m.p, 0, 4, 1)
    m.until(0x280)
    require(lib.reg(m.p, 1) == 0x246, "caller stack restored")
    require(m.read(0x80, 128) == expected_zp, "caller direct page restored")
    require(m.read(0xC000, 256) == expected_pcg, "caller PCG restored")
    m.close()
    return "passed"


def terrain(seeds, start=1):
    m = Machine()
    hashes = set()
    rooms = set()
    secrets = 0
    ring_floors = 0
    eligible_ring_floors = 0
    loot_signatures = set()
    item_kinds = set()
    missing_food_floors = 0
    missing_wand_floors = 0
    duplicate_magic_floors = 0
    worst = 0
    guard_addresses = [
        *range(0x3B60, 0x3B80),
        *range(0x3D70, 0x3D80),
        *range(0x3D87, 0x3E00),
    ]
    for address in guard_addresses:
        m.set(address, 0xA5)
    for seed in range(start, start + seeds):
        difficulty = (seed - 1) % 3
        depth = (5, 10, 20)[difficulty]
        floor = (seed // 3) % depth
        m.set("G_DIFFICULTY", difficulty)
        m.set("G_DEPTH", depth)
        m.set("G_FLOOR", floor)
        m.setw("G_RNG", seed)
        _, _, _, cycles = m.call("GENERATE_WORLD")
        worst = max(worst, cycles)
        grid = m.map()
        hashes.add(bytes(grid))
        rooms.add(m.get("GEN_ROOMS"))
        secrets += 5 in grid
        x, y = m.get("G_X"), m.get("G_Y")
        start = y * WIDTH + x
        require(grid[start] == 1, f"seed {seed}: start")
        visited = {start}
        q = deque([start])
        while q:
            p = q.popleft()
            px, py = p % WIDTH, p // WIDTH
            for nx, ny in [(px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)]:
                if 0 <= nx < WIDTH and 0 <= ny < 32:
                    n = ny * WIDTH + nx
                    if grid[n] not in (0, 5) and n not in visited:
                        visited.add(n)
                        q.append(n)
        require(
            len(visited) == sum(v not in (0, 5) for v in grid),
            f"seed {seed}: connectivity",
        )
        goal = 4 if floor == depth - 1 else 3
        require(
            grid.count(goal) == 1 and grid.index(goal) in visited, f"seed {seed}: goal"
        )
        require(
            all(
                grid[i] == 0
                for i in range(WIDTH * HEIGHT)
                if i % WIDTH in (0, WIDTH - 1) or i // WIDTH in (0, 31)
            ),
            f"seed {seed}: boundary",
        )
        require(grid.count(6) + grid.count(7) == 4, "trap count")
        enemies = [e for e in m.entities() if e[3]]
        items = [i for i in m.items() if i[2]]
        kinds = [i[2] for i in items]
        item_kinds.update(kinds)
        loot_signatures.add(tuple(sorted(kinds)))
        missing_food_floors += 1 not in kinds
        missing_wand_floors += 17 not in kinds
        duplicate_magic_floors += any(
            kinds.count(k) > 1 for k in (2, 3, 4, 5, 6, 14, 15, 16)
        )
        positions = [(e[0], e[1]) for e in enemies] + [(i[0], i[1]) for i in items]
        require(len(positions) == len(set(positions)), f"seed {seed}: overlap")
        require(
            all(grid[ey * WIDTH + ex] == 1 for ex, ey in positions), "entity terrain"
        )
        require(
            all(abs(e[0] - x) + abs(e[1] - y) >= 6 for e in enemies), "arrival distance"
        )
        require(len(enemies) == 4 + difficulty * 2 + floor, "enemy population")
        require(all(1 <= e[2] <= 15 for e in enemies), "enemy type limit")
        require(all(i[2] in (*range(1, 18), 21) for i in items), "item types")
        rings = sum(i[2] == 21 for i in items)
        require(rings in (0, 1), "ring population")
        require(floor >= 3 or rings == 0, "early floor ring")
        ring_floors += rings
        eligible_ring_floors += floor >= 3
        low = 16 if difficulty == 0 else 12
        require(low <= len(items) - rings <= low + 7, "item population")
        require(m.read(0x300, len(m.code)) == m.code, "generation modified code")
        require(
            all(m.get(address) == 0xA5 for address in guard_addresses),
            "generation crossed RAM allocation",
        )
        if seed % 100 == 0:
            print(f"generated seed={seed}", flush=True)
    m.close()
    return {
        "seeds": seeds,
        "unique_maps": len(hashes),
        "room_counts": sorted(rooms),
        "secret_floors": secrets,
        "ring_floors": ring_floors,
        "loot_signatures": list(loot_signatures),
        "item_kinds": sorted(item_kinds),
        "missing_food_floors": missing_food_floors,
        "missing_wand_floors": missing_wand_floors,
        "duplicate_magic_floors": duplicate_magic_floors,
        "eligible_ring_floors": eligible_ring_floors,
        "max_generation_cycles": worst,
        "hashes": [hashlib.sha256(h).hexdigest() for h in hashes],
    }


def terrain_worker(args):
    return terrain(*args)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seeds", type=int, default=1000)
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()
    started = time.monotonic()
    result = {
        "mechanics": mechanics(),
        "input": inputs(),
        "opcodes": check_opcodes(),
        "reference_inputs": check_references(),
    }
    from check_extensions import check as check_extensions

    result["extensions"] = check_extensions()
    from check_tools import check as check_tools

    result["tools"] = check_tools()
    from check_rendering import check as check_rendering

    result["rendering"] = check_rendering()
    from check_menu_wrap import check as check_menu_wrap

    result["menu_wrap"] = check_menu_wrap()
    print("mechanics, input, and opcode checks passed", flush=True)
    workers = max(1, min(args.workers, args.seeds))
    jobs = []
    for worker in range(workers):
        start = 1 + args.seeds * worker // workers
        end = 1 + args.seeds * (worker + 1) // workers
        jobs.append((end - start, start))
    with ProcessPoolExecutor(
        max_workers=workers, mp_context=multiprocessing.get_context("spawn")
    ) as pool:
        reports = list(pool.map(terrain_worker, jobs))
    result["terrain"] = {
        "seeds": args.seeds,
        "seed_first": 1,
        "seed_last": args.seeds,
        "workers": workers,
        "unique_maps": len({h for r in reports for h in r["hashes"]}),
        "room_counts": sorted({c for r in reports for c in r["room_counts"]}),
        "secret_floors": sum(r["secret_floors"] for r in reports),
        "ring_floors": sum(r["ring_floors"] for r in reports),
        "unique_loot": len({tuple(v) for r in reports for v in r["loot_signatures"]}),
        "item_kinds": sorted({v for r in reports for v in r["item_kinds"]}),
        "missing_food_floors": sum(r["missing_food_floors"] for r in reports),
        "missing_wand_floors": sum(r["missing_wand_floors"] for r in reports),
        "duplicate_magic_floors": sum(r["duplicate_magic_floors"] for r in reports),
        "eligible_ring_floors": sum(r["eligible_ring_floors"] for r in reports),
        "max_generation_cycles": max(r["max_generation_cycles"] for r in reports),
    }
    if args.seeds >= 1000:
        t = result["terrain"]
        require(t["item_kinds"] == [*range(1, 18), 21], "loot coverage")
        require(t["unique_loot"] > args.seeds // 2, "loot variation")
        require(0 < t["ring_floors"] < t["eligible_ring_floors"], "rare ring variation")
        for key in (
            "missing_food_floors",
            "missing_wand_floors",
            "duplicate_magic_floors",
        ):
            require(0 < t[key] < args.seeds, key)
    result["binary_sha256"] = hashlib.sha256(
        (ROOT / "build/relic_dive.bin").read_bytes()
    ).hexdigest()
    result["elapsed_seconds"] = round(time.monotonic() - started, 3)
    result["clock_hz"] = 894000
    (ROOT / "build/verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
