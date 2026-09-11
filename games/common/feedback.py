"""Original, non-looping victory phrases with a held final tonic."""


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
