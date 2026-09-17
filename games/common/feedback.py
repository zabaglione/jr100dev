"""Original, non-looping victory phrases with a held final tonic."""

from art import emit

FAILURES = {
    "quiet-route": "CAUGHT / BATTERY EMPTY",
    "night-swarm": "OVERRUN BY THE SWARM",
    "star-lance": "HULL LOST / TIME EXPIRED",
    "orbit-dodge": "HIT BY THE ORBITAL SHOT",
    "gate-runner": "BARRIER OR GAP COLLISION",
    "brick-pulse": "NO BALLS REMAIN",
    "ribbon-snake": "WALL OR BODY COLLISION",
    "lunar-touchdown": "HARD OR OFF-PAD LANDING",
    "echo-parry": "GUARD BROKEN",
    "pendulum-port": "MISSED THE LANDING",
    "five-forge": "RIVAL LINE / BOARD FULL",
    "corner-crown": "NOT ENOUGH WHITE STONES",
    "hearth-zero": "HEAT OR FOOD EXHAUSTED",
    "tide-bridge": "BRIDGE MOVE LIMIT",
    "mirror-relic": "ROTATION LIMIT",
    "chrono-breach": "HIT BY ENEMY FIRE",
    "sigil-deck": "HEALTH EXHAUSTED",
    "dice-relic": "HEALTH EXHAUSTED",
    "abyss-signal": "OXYGEN OR HULL EXHAUSTED",
    "chain-suit": "SCORE BELOW THE TARGET",
    "lumen-cross": "SIXTY MOVE LIMIT",
    "potion-path": "TWELVE DOSE LIMIT",
    "phase-pairs": "SIX INCORRECT PAIRS",
    "twenty-one": "COINS BELOW THE TARGET",
    "auction-house": "CASH BELOW THE TARGET",
    "memory-mosaic": "TWELVE MISSED PAIRS",
    "cargo-balance": "SHIP OUT OF BALANCE",
    "tidal-nets": "CATCH BELOW THE TARGET",
    "stone-balance": "RIVAL TOOK THE LAST STONE",
    "metro-weave": "TOO MANY WRONG DELIVERIES",
    "ruin-lexicon": "FIVE INCORRECT ANSWERS",
    "number-vault": "TEN ATTEMPTS EXHAUSTED",
    "orchard-days": "HARVEST DEADLINE REACHED",
    "seed-merge": "NO LEGAL MERGES REMAIN",
    "word-foundry": "EIGHT STEP LIMIT",
    "shadow-archive": "WRONG SUSPECT ACCUSED",
    "orbit-draft": "NOT ENOUGH ORBIT COMBOS",
    "sand-rescue": "WATER BUDGET EXHAUSTED",
}

REVEAL = {
    "iron-script",
    "quiet-route",
    "magnet-vault",
    "frost-steps",
    "glyph-shift",
    "compass-rose",
    "mirror-relic",
    "ribbon-snake",
    "night-swarm",
    "orbit-dodge",
    "gate-runner",
    "star-lance",
    "lunar-touchdown",
    "echo-parry",
    "pendulum-port",
    "five-forge",
    "corner-crown",
    "tide-bridge",
}


def pacing_assets(metadata):
    gid = metadata["id"]
    reveal = metadata.get("nativeRules") and gid in REVEAL
    groups = (1, 1, 3, 2, 2, 4, 2, 1) if reveal else (1,) * 8
    return (
        f"INTRO_STEPS: .equ {4 if reveal else 1}\n"
        + emit("INTRO_GROUPS", [g for g in groups for _ in range(4)])
        + emit(
            "START_MESSAGE",
            [64 if c == " " else ord(c) - 32 for c in "   GAME START   "],
        )
        + emit("INTRO_NOTE", [5, 1, 25, 4])
        + emit("START_NOTE", [5, 3, 20, 4, 25, 4, 32, 12])
        + emit("IMPACT_NOTE", [5, 3, 30, 2, 8, 3, 3, 5])
        + emit("FAILURE_JINGLE", [6, 5, 20, 9, 16, 9, 13, 14, 0, 6, 6, 30])
        + emit(
            "FAILURE_TEXT", [*FAILURES.get(gid, "OBJECTIVE NOT REACHED").encode(), 0]
        )
    )


def jingle(game_id):
    # C-major shape, a minor expedition cadence, or a bright high-register motif.
    if game_id in ("frost-steps", "lumen-cross", "prism-trace", "phase-pairs"):
        notes = [(25, 8), (32, 8), (37, 12), (0, 4), (34, 8), (32, 8), (37, 30)]
    elif game_id in (
        "abyss-signal",
        "sigil-deck",
        "dice-relic",
        "loop-ten",
        "ruin-lexicon",
        "shadow-archive",
        "mirror-relic",
    ):
        notes = [(13, 8), (16, 8), (20, 12), (0, 4), (23, 8), (20, 8), (25, 30)]
    else:
        notes = [(13, 8), (17, 8), (20, 12), (0, 4), (25, 8), (20, 8), (25, 30)]
    return [6, len(notes), *(v for note in notes for v in note)]
